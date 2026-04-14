"""
Silver Tier Dashboard API
FastAPI server for Next.js frontend dashboard.

Provides:
- REST API for tasks, plans, approvals, stats
- WebSocket for real-time updates
- Vault file read/write operations
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dashboard_api')

# FastAPI imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configuration
VAULT_PATH = PROJECT_ROOT / "silver" / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PLANS_PATH = VAULT_PATH / "Plans"
APPROVALS_PATH = VAULT_PATH / "Approvals"
COMPLETED_PATH = VAULT_PATH / "Completed"

# Ensure directories exist
for path in [INBOX_PATH, NEEDS_ACTION_PATH, PLANS_PATH, APPROVALS_PATH, COMPLETED_PATH]:
    path.mkdir(parents=True, exist_ok=True)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WebSocket] Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"[WebSocket] Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WebSocket] Error sending to client: {e}")
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"[WebSocket] Error sending personal message: {e}")


manager = ConnectionManager()

# Track server start time for uptime calculation
start_time = time.time()


# FastAPI App
app = FastAPI(
    title="Silver Tier Dashboard API",
    description="API for Personal AI Employee Dashboard",
    version="1.0.0"
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class TaskResponse(BaseModel):
    id: str
    title: str
    summary: str
    next_step: str
    source_file: str
    created_at: str
    status: str


class ApprovalRequest(BaseModel):
    task_id: str
    action: str


class TaskCreate(BaseModel):
    title: str
    content: str
    priority: Optional[str] = "medium"


class ActivityItem(BaseModel):
    timestamp: str
    type: str
    description: str
    details: Optional[dict] = None


# Helper Functions
def read_markdown_file(file_path: Path) -> dict:
    """Read and parse a markdown file"""
    if not file_path.exists():
        return {}
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    title = file_path.stem.replace("_", " ").replace("TODO_", "").title()
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break
    
    summary = ""
    if "## Summary" in content:
        summary = content.split("## Summary")[1].split("##")[0].strip()
    
    next_step = ""
    if "## Suggested Next Step" in content:
        next_step = content.split("## Suggested Next Step")[1].split("##")[0].strip()
    
    created_at = ""
    if "## Ingestion Timestamp" in content:
        created_at = content.split("## Ingestion Timestamp")[1].split("##")[0].strip()
    else:
        created_at = datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "title": title,
        "summary": summary,
        "next_step": next_step,
        "content": content,
        "created_at": created_at,
        "source_file": file_path.name
    }


def get_all_tasks() -> List[dict]:
    """Get all tasks from vault"""
    tasks = []
    
    for file in INBOX_PATH.glob("*.md"):
        data = read_markdown_file(file)
        if data:
            data["id"] = f"inbox_{file.stem}"
            data["status"] = "inbox"
            tasks.append(data)
    
    for file in NEEDS_ACTION_PATH.glob("*.md"):
        data = read_markdown_file(file)
        if data:
            data["id"] = f"needs_action_{file.stem}"
            data["status"] = "needs_action"
            tasks.append(data)
    
    for file in COMPLETED_PATH.glob("*.md"):
        data = read_markdown_file(file)
        if data:
            data["id"] = f"completed_{file.stem}"
            data["status"] = "completed"
            tasks.append(data)
    
    tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return tasks


def get_pending_approvals() -> List[dict]:
    """Get all pending approval requests"""
    approvals = []
    
    for file in APPROVALS_PATH.glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "**Status:** pending" in content or "**Status:**pending" in content:
            approval_data = {
                "id": file.stem,
                "file_path": str(file),
                "content": content,
                "created_at": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if "**Action Type:**" in content:
                action_type = content.split("**Action Type:**")[1].split("\n")[0].strip()
                approval_data["action_type"] = action_type
            
            approvals.append(approval_data)
    
    return approvals


def get_stats() -> dict:
    """Get dashboard statistics"""
    inbox_count = len(list(INBOX_PATH.glob("*.md")))
    needs_action_count = len(list(NEEDS_ACTION_PATH.glob("*.md")))
    pending_approvals = len(get_pending_approvals())
    total_plans = len(list(PLANS_PATH.glob("*.md")))

    # Count ALL completed tasks (not just today) for better UX
    total_completed = len(list(COMPLETED_PATH.glob("*.md")))

    return {
        "inbox_count": inbox_count,
        "needs_action_count": needs_action_count,
        "pending_approvals": pending_approvals,
        "completed_today": total_completed,  # Show all-time count to match modal
        "total_plans": total_plans,
        "total_tasks_completed": total_completed
    }


def get_recent_activity(limit: int = 20) -> List[dict]:
    """Get recent activity from vault"""
    activities = []
    
    plan_files = sorted(PLANS_PATH.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]
    for file in plan_files:
        activities.append({
            "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "plan_generated",
            "description": f"Plan generated: {file.name}",
            "details": {"file": file.name}
        })
    
    completed_files = sorted(COMPLETED_PATH.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]
    for file in completed_files:
        activities.append({
            "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "type": "task_completed",
            "description": f"Task completed: {file.name}",
            "details": {"file": file.name}
        })
    
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    return activities[:limit]


def approve_task(task_id: str) -> dict:
    """Approve a task"""
    task_file = NEEDS_ACTION_PATH / f"{task_id.replace('needs_action_', '')}.md"
    
    if not task_file.exists():
        task_file = NEEDS_ACTION_PATH / f"TODO_{task_id.replace('needs_action_', '')}.md"
    
    if not task_file.exists():
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    completed_file = COMPLETED_PATH / task_file.name
    completed_file.write_text(task_file.read_text(encoding="utf-8"), encoding="utf-8")
    task_file.unlink()
    
    return {"success": True, "message": f"Task {task_id} approved and moved to completed"}


def reject_task(task_id: str) -> dict:
    """Reject a task"""
    task_file = NEEDS_ACTION_PATH / f"{task_id.replace('needs_action_', '')}.md"
    
    if not task_file.exists():
        task_file = NEEDS_ACTION_PATH / f"TODO_{task_id.replace('needs_action_', '')}.md"
    
    if not task_file.exists():
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    
    task_file.unlink()
    return {"success": True, "message": f"Task {task_id} rejected and removed"}


# API Routes
@app.get("/")
async def root():
    """API Health Check"""
    return {
        "status": "ok",
        "message": "Silver Tier Dashboard API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/health/full")
async def full_health_check():
    """
    Comprehensive health check for all services
    Checks: Dashboard API, Odoo MCP, Social Media MCP, Odoo, Dashboard Frontend
    """
    try:
        # Import utility functions
        sys.path.insert(0, str(PROJECT_ROOT / 'silver'))
        from utils import ServiceHealthChecker, VaultStatsChecker
        
        # Check all services
        service_checker = ServiceHealthChecker()
        services_health = service_checker.check_all_services()
        
        # Check vault stats
        vault_checker = VaultStatsChecker(str(PROJECT_ROOT / 'silver' / 'vault'))
        vault_stats = vault_checker.get_stats()
        
        # Check local API health
        local_health = {
            "api_status": "healthy",
            "api_version": "1.0.0",
            "uptime_seconds": int(time.time() - start_time) if 'start_time' in globals() else 0,
            "websocket_connections": len(manager.active_connections)
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": services_health['overall_status'],
            "local": local_health,
            "services": services_health,
            "vault": vault_stats,
            "summary": {
                "healthy_services": services_health['healthy_services'],
                "total_services": services_health['total_services'],
                "vault_total_files": vault_stats['total_files']
            }
        }
        
    except Exception as e:
        logger.error(f"Full health check failed: {str(e)}")
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "error",
            "error": str(e),
            "local": {
                "api_status": "healthy",
                "api_version": "1.0.0"
            }
        }


@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(status: Optional[str] = None):
    """Get all tasks, optionally filtered by status"""
    tasks = get_all_tasks()
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    return tasks


@app.get("/api/tasks/inbox")
async def get_inbox_tasks():
    """Get tasks in Inbox"""
    tasks = [t for t in get_all_tasks() if t.get("status") == "inbox"]
    return {"count": len(tasks), "tasks": tasks}


@app.get("/api/tasks/needs-action")
async def get_needs_action_tasks():
    """Get tasks in Needs Action"""
    tasks = [t for t in get_all_tasks() if t.get("status") == "needs_action"]
    return {"count": len(tasks), "tasks": tasks}


@app.get("/api/tasks/completed")
async def get_completed_tasks():
    """Get completed tasks"""
    tasks = [t for t in get_all_tasks() if t.get("status") == "completed"]
    return {"count": len(tasks), "tasks": tasks}


@app.post("/api/tasks/approve")
async def approve_task_endpoint(request: ApprovalRequest):
    """Approve a task"""
    result = approve_task(request.task_id)
    
    await manager.broadcast({
        "type": "task_approved",
        "task_id": request.task_id,
        "timestamp": datetime.now().isoformat()
    })
    
    return result


@app.post("/api/tasks/reject")
async def reject_task_endpoint(request: ApprovalRequest):
    """Reject a task"""
    result = reject_task(request.task_id)
    
    await manager.broadcast({
        "type": "task_rejected",
        "task_id": request.task_id,
        "timestamp": datetime.now().isoformat()
    })
    
    return result


@app.post("/api/tasks/create")
async def create_task(request: TaskCreate, background_tasks: BackgroundTasks):
    """Create a new task manually"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"manual_task_{timestamp}.md"
    file_path = INBOX_PATH / filename
    
    content = f"""# {request.title}

## Priority
{request.priority}

## Content
{request.content}

## Created At
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Source
Manually created from dashboard
"""
    
    file_path.write_text(content, encoding="utf-8")
    
    await manager.broadcast({
        "type": "task_created",
        "task_id": f"inbox_{filename}",
        "title": request.title,
        "timestamp": datetime.now().isoformat()
    })
    
    return {"success": True, "task_id": f"inbox_{filename}", "message": "Task created successfully"}


@app.get("/api/plans")
async def get_plans(limit: Optional[int] = 10):
    """Get generated plans"""
    plans = []
    plan_files = sorted(PLANS_PATH.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if limit:
        plan_files = plan_files[:limit]
    
    for file in plan_files:
        data = read_markdown_file(file)
        if data:
            data["id"] = file.stem
            plans.append(data)
    
    return {"count": len(plans), "plans": plans}


@app.get("/api/approvals")
async def get_approvals():
    """Get pending approval requests"""
    approvals = get_pending_approvals()
    return {"count": len(approvals), "approvals": approvals}


@app.get("/api/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return get_stats()


@app.get("/api/activity")
async def get_activity(limit: Optional[int] = 20):
    """Get recent activity"""
    activities = get_recent_activity(limit or 20)
    return {"count": len(activities), "activities": activities}


# AI Post Enhancement Endpoint
@app.post("/api/ai/enhance")
async def enhance_post(data: dict):
    """Enhance social media post using AI (OpenRouter/Gemini)"""
    import httpx
    
    message = data.get("message", "")
    if not message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
    if not openrouter_key:
        raise HTTPException(status_code=500, detail="OpenRouter API key not configured")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Personal AI Employee Dashboard"
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a social media expert. Enhance posts by making them more engaging, adding relevant emojis, and including trending hashtags. Keep it professional and concise. Return ONLY the enhanced post, nothing else."
                        },
                        {
                            "role": "user",
                            "content": f"Enhance this social media post:\n\n{message}"
                        }
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=f"AI API error: {response.status_code}")
            
            result = response.json()
            
            if result.get("choices") and result["choices"][0].get("message"):
                enhanced_text = result["choices"][0]["message"]["content"].strip()
                return {
                    "success": True,
                    "enhanced_post": enhanced_text,
                    "original": message
                }
            else:
                raise HTTPException(status_code=500, detail="Invalid AI response")
                
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI enhancement failed: {str(e)}")


# Gold Tier Endpoints
@app.get("/api/audit")
async def get_audit_logs(limit: Optional[int] = 20):
    """Get audit logs (Gold Tier)"""
    audit_path = VAULT_PATH / "Audit"
    
    if not audit_path.exists():
        return {"count": 0, "logs": []}
    
    logs = []
    audit_files = sorted(audit_path.glob("audit_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    for file in audit_files[:7]:  # Last 7 days
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                logs.extend(data)
        except Exception:
            pass
    
    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"count": len(logs[:limit]), "logs": logs[:limit]}


@app.get("/api/ralph-wiggum/status")
async def get_ralph_wiggum_status():
    """Get Ralph Wiggum Loop status (Gold Tier)"""
    import subprocess
    
    try:
        # Try to get status from running loop
        ralph_script = PROJECT_ROOT / "silver" / "ralph_wiggum_loop.py"
        
        if ralph_script.exists():
            # For now, return mock status
            # In production, this would query the running loop process
            return {
                "running": False,
                "tasks_processed": 0,
                "consecutive_failures": 0,
                "last_activity": None
            }
        
        return {
            "running": False,
            "tasks_processed": 0,
            "consecutive_failures": 0,
            "last_activity": None
        }
    except Exception as e:
        return {
            "running": False,
            "tasks_processed": 0,
            "consecutive_failures": 0,
            "last_activity": None,
            "error": str(e)
        }


@app.get("/api/ralph-wiggum/start")
async def start_ralph_wiggum(background_tasks: BackgroundTasks):
    """Start Ralph Wiggum Loop (Gold Tier)"""
    import subprocess
    
    ralph_script = PROJECT_ROOT / "silver" / "ralph_wiggum_loop.py"
    
    if not ralph_script.exists():
        raise HTTPException(status_code=404, detail="Ralph Wiggum Loop script not found")
    
    try:
        # Start in background
        background_tasks.add_task(
            subprocess.run,
            [sys.executable, str(ralph_script)],
            cwd=str(PROJECT_ROOT / "silver")
        )
        
        return {"success": True, "message": "Ralph Wiggum Loop started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start loop: {str(e)}")


@app.get("/api/ceo-briefing/generate")
async def generate_ceo_briefing(briefing_type: Optional[str] = "daily"):
    """Generate CEO Briefing (Gold Tier)"""
    import subprocess
    
    briefing_script = PROJECT_ROOT / "silver" / "skills" / "ceo-briefing" / "ceo_briefing.py"
    
    if not briefing_script.exists():
        raise HTTPException(status_code=404, detail="CEO Briefing script not found")
    
    try:
        result = subprocess.run(
            [sys.executable, str(briefing_script), "--type", briefing_type],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT / "silver")
        )
        
        return {
            "success": True,
            "content": result.stdout,
            "briefing_type": briefing_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate briefing: {str(e)}")


@app.get("/api/vault/file/{file_path:path}")
async def get_vault_file(file_path: str):
    """Get a specific vault file content"""
    if ".." in file_path or file_path.startswith("/"):
        raise HTTPException(status_code=400, detail="Invalid file path")

    full_path = VAULT_PATH / file_path

    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    if not full_path.is_file():
        raise HTTPException(status_code=400, detail="Not a file")

    content = full_path.read_text(encoding="utf-8")

    return {
        "filename": full_path.name,
        "path": str(full_path),
        "content": content
    }


# Browser Automation Endpoints (Gold Tier - No API Keys Required)
class BrowserPostRequest(BaseModel):
    message: str
    platforms: Optional[List[str]] = ["facebook", "twitter", "linkedin"]
    image_path: Optional[str] = None


class WhatsAppMessageRequest(BaseModel):
    phone: str
    message: str


class GmailRequest(BaseModel):
    to: str
    subject: str
    body: str


@app.get("/api/browser-automation/status")
async def get_browser_automation_status():
    """Get browser automation status and configured platforms"""
    browser_skill_path = PROJECT_ROOT / "silver" / "skills" / "browser-automation"
    
    platforms_configured = {
        "facebook": bool(os.getenv("FACEBOOK_EMAIL") and os.getenv("FACEBOOK_PASSWORD")),
        "instagram": bool(os.getenv("INSTAGRAM_USERNAME") and os.getenv("INSTAGRAM_PASSWORD")),
        "twitter": bool(os.getenv("TWITTER_USERNAME") and os.getenv("TWITTER_PASSWORD")),
        "linkedin": bool(os.getenv("LINKEDIN_EMAIL") and os.getenv("LINKEDIN_PASSWORD")),
        "whatsapp": True,  # WhatsApp Web doesn't need credentials
        "gmail": bool(os.getenv("GMAIL_EMAIL") and os.getenv("GMAIL_PASSWORD")),
    }
    
    return {
        "available": browser_skill_path.exists(),
        "platforms": platforms_configured,
        "selenium_installed": True
    }


@app.post("/api/browser-automation/post")
async def browser_post(request: BrowserPostRequest):
    """
    Post to social media using browser automation (no API keys required).
    Uses Selenium to automate posting directly through the browser.
    """
    try:
        # Add browser-automation module to path FIRST
        browser_auto_path = PROJECT_ROOT / "silver" / "skills" / "browser-automation"
        browser_auto_path_str = str(browser_auto_path)
        
        # Clear any existing paths and add fresh
        sys.path = [p for p in sys.path if 'browser-automation' not in p]
        sys.path.insert(0, browser_auto_path_str)
        
        logger.info(f"Added to path: {browser_auto_path_str}")
        logger.info(f"Current sys.path: {sys.path[:5]}")

        # Now import
        logger.info("Importing BrowserSocialPoster...")
        from browser_poster import BrowserSocialPoster
        logger.info("✅ Import successful!")

        results = {
            'success': False,
            'posted_to': 0,
            'failed_on': 0,
            'results': {
                'success': [],
                'failed': []
            },
            'timestamp': datetime.now().isoformat()
        }

        # Initialize poster (non-headless for better reliability)
        logger.info("Initializing BrowserSocialPoster...")
        poster = BrowserSocialPoster(headless=False)

        try:
            # Post to each selected platform
            for platform in request.platforms:
                logger.info(f"Posting to {platform}...")

                if platform == "facebook":
                    result = poster.post_to_facebook(request.message, request.image_path)
                elif platform == "instagram":
                    result = poster.post_to_instagram(request.message, request.image_path)
                elif platform == "twitter":
                    result = poster.post_to_twitter(request.message, request.image_path)
                elif platform == "linkedin":
                    result = poster.post_to_linkedin(request.message, request.image_path)
                else:
                    result = {
                        'success': False,
                        'platform': platform,
                        'error': f'Unsupported platform: {platform}'
                    }

                # Track results
                if result.get('success'):
                    results['posted_to'] += 1
                    results['results']['success'].append(result)
                else:
                    results['failed_on'] += 1
                    results['results']['failed'].append(result)

        finally:
            # Always close the browser
            logger.info("Closing browser...")
            poster.close_driver()

        # Set overall success
        results['success'] = results['posted_to'] > 0
        
        logger.info(f"Post result: {results}")

        return results

    except Exception as e:
        logger.error(f"Browser automation error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'success': False,
            'error': str(e),
            'posted_to': 0,
            'failed_on': len(request.platforms)
        }


@app.post("/api/browser-automation/post/{platform}")
async def browser_post_single(platform: str, request: BrowserPostRequest, auto_post: bool = True):
    """
    Post to a single platform using browser automation.
    Supported: facebook, instagram, twitter, linkedin
    
    Args:
        platform: Platform name (facebook, instagram, twitter, linkedin)
        request: Post request with message and optional image
        auto_post: If True, auto-click Post button. If False, wait for manual confirm (HITL mode)
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "silver" / "skills"))
        from browser_automation.browser_poster import BrowserSocialPoster

        poster = BrowserSocialPoster(headless=False)

        if platform == "facebook":
            result = poster.post_to_facebook(request.message, request.image_path, auto_post=auto_post)
        elif platform == "instagram":
            if not request.image_path:
                return {"success": False, "error": "Instagram requires an image"}
            result = poster.post_to_instagram(request.message, request.image_path)
        elif platform == "twitter":
            result = poster.post_to_twitter(request.message, request.image_path)
        elif platform == "linkedin":
            result = poster.post_to_linkedin(request.message, request.image_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

        await manager.broadcast({
            "type": "browser_automation",
            "action": f"post_{platform}",
            "success": result.get("success"),
            "timestamp": datetime.now().isoformat()
        })

        return result

    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Browser automation module not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Browser automation failed: {str(e)}")


@app.post("/api/browser-automation/whatsapp")
async def send_whatsapp_message(request: WhatsAppMessageRequest):
    """
    Send WhatsApp message using browser automation.
    Uses WhatsApp Web - no API key required.
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "silver" / "skills"))
        from browser_automation.browser_poster import BrowserSocialPoster
        
        poster = BrowserSocialPoster(headless=False)
        result = poster.send_whatsapp_message(request.phone, request.message)
        
        await manager.broadcast({
            "type": "browser_automation",
            "action": "whatsapp_message",
            "recipient": request.phone,
            "success": result.get("success"),
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Browser automation module not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Browser automation failed: {str(e)}")


@app.post("/api/browser-automation/gmail")
async def send_gmail_email(request: GmailRequest):
    """
    Send email using Gmail browser automation.
    Uses Gmail Web - no API key required (just login credentials).
    """
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "silver" / "skills"))
        from browser_automation.browser_poster import BrowserSocialPoster
        
        poster = BrowserSocialPoster(headless=False)
        result = poster.send_gmail_email(request.to, request.subject, request.body)
        
        await manager.broadcast({
            "type": "browser_automation",
            "action": "gmail_email",
            "recipient": request.to,
            "success": result.get("success"),
            "timestamp": datetime.now().isoformat()
        })
        
        return result
        
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Browser automation module not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Browser automation failed: {str(e)}")


@app.get("/api/browser-automation/history")
async def get_browser_automation_history(limit: Optional[int] = 10):
    """Get browser automation history from vault"""
    history_dir = VAULT_PATH / "Browser_Automation_History"
    
    if not history_dir.exists():
        return {"count": 0, "history": []}
    
    history_files = sorted(history_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    history = []
    for file in history_files[:limit]:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                history.append(data)
        except Exception:
            pass
    
    return {"count": len(history), "history": history}


# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "ping":
                    await manager.send_personal(websocket, {"type": "pong", "timestamp": datetime.now().isoformat()})
                
                elif msg_type == "subscribe":
                    events = message.get("events", [])
                    await manager.send_personal(websocket, {
                        "type": "subscribed",
                        "events": events,
                        "timestamp": datetime.now().isoformat()
                    })
                
            except json.JSONDecodeError:
                pass
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"[WebSocket] Error: {e}")
        manager.disconnect(websocket)


# Background Task: File Watcher
async def watch_vault_changes():
    """Watch for vault changes and broadcast updates"""
    import asyncio
    
    last_state = {
        "inbox": len(list(INBOX_PATH.glob("*.md"))),
        "needs_action": len(list(NEEDS_ACTION_PATH.glob("*.md"))),
        "plans": len(list(PLANS_PATH.glob("*.md")))
    }
    
    while True:
        await asyncio.sleep(5)
        
        current_state = {
            "inbox": len(list(INBOX_PATH.glob("*.md"))),
            "needs_action": len(list(NEEDS_ACTION_PATH.glob("*.md"))),
            "plans": len(list(PLANS_PATH.glob("*.md")))
        }
        
        if current_state["inbox"] != last_state["inbox"]:
            await manager.broadcast({
                "type": "vault_change",
                "category": "inbox",
                "old_count": last_state["inbox"],
                "new_count": current_state["inbox"],
                "timestamp": datetime.now().isoformat()
            })
        
        if current_state["needs_action"] != last_state["needs_action"]:
            await manager.broadcast({
                "type": "vault_change",
                "category": "needs_action",
                "old_count": last_state["needs_action"],
                "new_count": current_state["needs_action"],
                "timestamp": datetime.now().isoformat()
            })
        
        if current_state["plans"] != last_state["plans"]:
            await manager.broadcast({
                "type": "vault_change",
                "category": "plans",
                "old_count": last_state["plans"],
                "new_count": current_state["plans"],
                "timestamp": datetime.now().isoformat()
            })
        
        last_state = current_state


# ============================================
# PLATINUM TIER ENDPOINTS
# ============================================

@app.get("/api/platinum/status")
async def get_platinum_status():
    """Get Platinum Tier cloud/local agent status"""
    try:
        # Check cloud health signal
        cloud_health_file = VAULT_PATH.parent / "vault" / "Signals" / "cloud_health.json"
        cloud_status = None
        if cloud_health_file.exists():
            with open(cloud_health_file, 'r') as f:
                cloud_status = json.load(f)
        
        # Check local health signal
        local_health_file = VAULT_PATH.parent / "vault" / "Signals" / "local_health.json"
        local_status = None
        if local_health_file.exists():
            with open(local_health_file, 'r') as f:
                local_status = json.load(f)
        
        # Count items in each state
        needs_action = len(list((VAULT_PATH.parent / "vault" / "Needs_Action").rglob("*.md"))) if (VAULT_PATH.parent / "vault" / "Needs_Action").exists() else 0
        in_progress_cloud = len(list((VAULT_PATH.parent / "vault" / "In_Progress" / "cloud").glob("*"))) if (VAULT_PATH.parent / "vault" / "In_Progress" / "cloud").exists() else 0
        in_progress_local = len(list((VAULT_PATH.parent / "vault" / "In_Progress" / "local").glob("*"))) if (VAULT_PATH.parent / "vault" / "In_Progress" / "local").exists() else 0
        pending_approval = len(list((VAULT_PATH.parent / "vault" / "Pending_Approval").glob("*.json"))) if (VAULT_PATH.parent / "vault" / "Pending_Approval").exists() else 0
        done = len(list((VAULT_PATH.parent / "vault" / "Done").glob("*.json"))) if (VAULT_PATH.parent / "vault" / "Done").exists() else 0
        
        return {
            "cloud": cloud_status or {"status": "offline", "message": "Cloud agent not running"},
            "local": local_status or {"status": "offline", "message": "Local agent not running"},
            "queue": {
                "needs_action": needs_action,
                "in_progress_cloud": in_progress_cloud,
                "in_progress_local": in_progress_local,
                "pending_approval": pending_approval,
                "done": done
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting platinum status: {e}")
        return {
            "error": str(e),
            "cloud": {"status": "error"},
            "local": {"status": "error"},
            "queue": {}
        }


@app.get("/api/platinum/pending-approvals")
async def get_platinum_pending_approvals():
    """Get all pending approvals from Platinum Tier"""
    try:
        pending_path = VAULT_PATH.parent / "vault" / "Pending_Approval"
        
        if not pending_path.exists():
            return {"pending": []}
        
        pending_items = []
        
        for approval_file in pending_path.glob("*.json"):
            try:
                with open(approval_file, 'r') as f:
                    data = json.load(f)
                
                pending_items.append({
                    "id": approval_file.stem,
                    "filename": approval_file.name,
                    "type": data.get("type", "unknown"),
                    "status": data.get("status", "pending"),
                    "created_at": data.get("created_at", ""),
                    "assigned_to": data.get("assigned_to", ""),
                    "risk_level": data.get("risk_level", "unknown"),
                    "data": data
                })
            except Exception as e:
                logger.error(f"Error reading {approval_file}: {e}")
        
        return {"pending": pending_items}
    
    except Exception as e:
        logger.error(f"Error getting pending approvals: {e}")
        return {"error": str(e), "pending": []}


@app.post("/api/platinum/approvals/{approval_id}/approve")
async def approve_platinum_action(approval_id: str):
    """Approve a pending Platinum Tier action"""
    try:
        pending_path = VAULT_PATH.parent / "vault" / "Pending_Approval"
        approved_path = VAULT_PATH.parent / "vault" / "Updates" / "approved"
        
        # Ensure approved path exists
        approved_path.mkdir(parents=True, exist_ok=True)
        
        approval_file = pending_path / f"{approval_id}.json"
        
        if not approval_file.exists():
            raise HTTPException(status_code=404, detail=f"Approval {approval_id} not found")
        
        # Read and update
        with open(approval_file, 'r') as f:
            data = json.load(f)
        
        data['status'] = 'approved'
        data['approved_by'] = 'dashboard_user'
        data['approved_at'] = datetime.now().isoformat()
        
        # Move to approved
        dest = approved_path / approval_file.name
        with open(dest, 'w') as f:
            json.dump(data, f, indent=2)
        
        approval_file.unlink()
        
        await manager.broadcast({
            "type": "approval_action",
            "action": "approved",
            "id": approval_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "message": f"Approved {approval_id}"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving {approval_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/platinum/approvals/{approval_id}/reject")
async def reject_platinum_action(approval_id: str, reason: str = ""):
    """Reject a pending Platinum Tier action"""
    try:
        pending_path = VAULT_PATH.parent / "vault" / "Pending_Approval"
        rejected_path = VAULT_PATH.parent / "vault" / "Updates" / "rejected"
        
        # Ensure rejected path exists
        rejected_path.mkdir(parents=True, exist_ok=True)
        
        approval_file = pending_path / f"{approval_id}.json"
        
        if not approval_file.exists():
            raise HTTPException(status_code=404, detail=f"Approval {approval_id} not found")
        
        # Read and update
        with open(approval_file, 'r') as f:
            data = json.load(f)
        
        data['status'] = 'rejected'
        data['rejected_by'] = 'dashboard_user'
        data['rejected_at'] = datetime.now().isoformat()
        data['rejection_reason'] = reason
        
        # Move to rejected
        dest = rejected_path / approval_file.name
        with open(dest, 'w') as f:
            json.dump(data, f, indent=2)
        
        approval_file.unlink()
        
        await manager.broadcast({
            "type": "approval_action",
            "action": "rejected",
            "id": approval_id,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "message": f"Rejected {approval_id}"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting {approval_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/platinum/audit-log")
async def get_platinum_audit_log():
    """Get Platinum Tier audit log"""
    try:
        audit_path = VAULT_PATH.parent / "vault" / "Updates" / "audit_log"
        
        if not audit_path.exists():
            return {"audit_log": []}
        
        audit_entries = []
        
        for audit_file in audit_path.glob("*.json"):
            try:
                with open(audit_file, 'r') as f:
                    data = json.load(f)
                audit_entries.append(data)
            except Exception as e:
                logger.error(f"Error reading {audit_file}: {e}")
        
        return {"audit_log": audit_entries}
    
    except Exception as e:
        logger.error(f"Error getting audit log: {e}")
        return {"error": str(e), "audit_log": []}


@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    import asyncio
    asyncio.create_task(watch_vault_changes())
    print("[Dashboard API] Server started successfully!")
    print(f"[Dashboard API] Vault Path: {VAULT_PATH}")
    print(f"[Dashboard API] CORS enabled for: http://localhost:3000")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("SILVER TIER DASHBOARD API")
    print("=" * 60)
    print(f"Starting server on http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"Vault Path: {VAULT_PATH}")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
