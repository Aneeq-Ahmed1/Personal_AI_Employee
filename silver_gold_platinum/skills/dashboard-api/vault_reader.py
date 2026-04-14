"""
Silver Tier Vault Reader
Utility module for reading/writing vault files.

Used by:
- Dashboard API
- Task Manager
- Approval Handler
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
VAULT_PATH = PROJECT_ROOT / "silver" / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PLANS_PATH = VAULT_PATH / "Plans"
APPROVALS_PATH = VAULT_PATH / "Approvals"
COMPLETED_PATH = VAULT_PATH / "Completed"
MEMORY_PATH = VAULT_PATH / "memory"

# Ensure directories exist
for path in [INBOX_PATH, NEEDS_ACTION_PATH, PLANS_PATH, APPROVALS_PATH, COMPLETED_PATH, MEMORY_PATH]:
    path.mkdir(parents=True, exist_ok=True)


class VaultReader:
    """Read and write operations for vault files"""
    
    def __init__(self):
        self.vault_path = VAULT_PATH
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """Read a file and return its content"""
        if not file_path.exists():
            return None
        
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return None
    
    def write_file(self, file_path: Path, content: str) -> bool:
        """Write content to a file"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False
    
    def delete_file(self, file_path: Path) -> bool:
        """Delete a file"""
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def move_file(self, source: Path, destination: Path) -> bool:
        """Move a file from source to destination"""
        try:
            content = self.read_file(source)
            if content is None:
                return False
            
            self.write_file(destination, content)
            self.delete_file(source)
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    def parse_markdown(self, file_path: Path) -> Dict:
        """Parse a markdown file and extract structured data"""
        content = self.read_file(file_path)
        if not content:
            return {}
        
        # Extract title (first # heading)
        title = file_path.stem.replace("_", " ").replace("TODO_", "").title()
        for line in content.split("\n"):
            if line.startswith("# "):
                title = line[2:].strip()
                break
        
        # Extract sections
        sections = {}
        current_section = "content"
        current_content = []
        
        for line in content.split("\n"):
            if line.startswith("## "):
                # Save previous section
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                # Start new section
                current_section = line[3:].strip().lower().replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = "\n".join(current_content).strip()
        
        # Extract metadata
        metadata = {
            "title": title,
            "filename": file_path.name,
            "path": str(file_path),
            "created_at": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "size": file_path.stat().st_size
        }
        
        # Add sections to metadata
        metadata.update(sections)
        
        return metadata
    
    def list_files(self, directory: Path, extension: str = ".md") -> List[Path]:
        """List all files in a directory with given extension"""
        if not directory.exists():
            return []
        
        return sorted(directory.glob(f"*{extension}"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    def get_inbox_files(self) -> List[Dict]:
        """Get all files from Inbox with parsed data"""
        files = self.list_files(INBOX_PATH)
        return [self.parse_markdown(f) for f in files if self.parse_markdown(f)]
    
    def get_needs_action_files(self) -> List[Dict]:
        """Get all files from Needs_Action with parsed data"""
        files = self.list_files(NEEDS_ACTION_PATH)
        return [self.parse_markdown(f) for f in files if self.parse_markdown(f)]
    
    def get_plan_files(self) -> List[Dict]:
        """Get all files from Plans with parsed data"""
        files = self.list_files(PLANS_PATH)
        return [self.parse_markdown(f) for f in files if self.parse_markdown(f)]
    
    def get_approval_files(self) -> List[Dict]:
        """Get all files from Approvals with parsed data"""
        files = self.list_files(APPROVALS_PATH)
        approvals = []
        
        for f in files:
            data = self.parse_markdown(f)
            content = self.read_file(f)
            
            # Check if pending
            if content and ("**Status:** pending" in content or "**Status:**pending" in content):
                data["status"] = "pending"
                approvals.append(data)
            elif content:
                # Extract status
                if "**Status:** approved" in content or "**Status:**approved" in content:
                    data["status"] = "approved"
                elif "**Status:** rejected" in content or "**Status:**rejected" in content:
                    data["status"] = "rejected"
                else:
                    data["status"] = "unknown"
                approvals.append(data)
        
        return approvals
    
    def get_completed_files(self) -> List[Dict]:
        """Get all files from Completed with parsed data"""
        files = self.list_files(COMPLETED_PATH)
        return [self.parse_markdown(f) for f in files if self.parse_markdown(f)]
    
    def get_stats(self) -> Dict:
        """Get vault statistics"""
        return {
            "inbox_count": len(self.list_files(INBOX_PATH)),
            "needs_action_count": len(self.list_files(NEEDS_ACTION_PATH)),
            "plans_count": len(self.list_files(PLANS_PATH)),
            "pending_approvals_count": len([a for a in self.get_approval_files() if a.get("status") == "pending"]),
            "completed_count": len(self.list_files(COMPLETED_PATH)),
            "completed_today": self._count_completed_today()
        }
    
    def _count_completed_today(self) -> int:
        """Count files completed today"""
        today = datetime.now().strftime("%Y-%m-%d")
        count = 0
        
        for file in self.list_files(COMPLETED_PATH):
            file_date = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d")
            if file_date == today:
                count += 1
        
        return count
    
    def create_task(self, title: str, content: str, priority: str = "medium") -> Optional[Path]:
        """Create a new task in Inbox"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"manual_task_{timestamp}.md"
        file_path = INBOX_PATH / filename
        
        markdown_content = f"""# {title}

## Priority
{priority}

## Content
{content}

## Created At
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Source
Manually created from dashboard
"""
        
        if self.write_file(file_path, markdown_content):
            return file_path
        return None
    
    def approve_task(self, file_path: Path) -> bool:
        """Approve a task (move to Completed)"""
        if not file_path.exists():
            # Try with TODO_ prefix
            file_path = NEEDS_ACTION_PATH / f"TODO_{file_path.name}"
        
        if not file_path.exists():
            return False
        
        destination = COMPLETED_PATH / file_path.name
        return self.move_file(file_path, destination)
    
    def reject_task(self, file_path: Path) -> bool:
        """Reject a task (delete it)"""
        if not file_path.exists():
            # Try with TODO_ prefix
            file_path = NEEDS_ACTION_PATH / f"TODO_{file_path.name}"
        
        if not file_path.exists():
            return False
        
        return self.delete_file(file_path)
    
    def get_activity_log(self, limit: int = 20) -> List[Dict]:
        """Get recent activity from vault"""
        activities = []
        
        # Get recent plans
        plan_files = self.list_files(PLANS_PATH)[:limit]
        for file in plan_files:
            activities.append({
                "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "type": "plan_generated",
                "description": f"Plan generated: {file.name}",
                "details": {"file": file.name, "category": "plans"}
            })
        
        # Get recent completed tasks
        completed_files = self.list_files(COMPLETED_PATH)[:limit]
        for file in completed_files:
            activities.append({
                "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "type": "task_completed",
                "description": f"Task completed: {file.name}",
                "details": {"file": file.name, "category": "completed"}
            })
        
        # Get recent inbox additions
        inbox_files = self.list_files(INBOX_PATH)[:limit]
        for file in inbox_files:
            activities.append({
                "timestamp": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "type": "task_received",
                "description": f"Task received: {file.name}",
                "details": {"file": file.name, "category": "inbox"}
            })
        
        # Sort by timestamp (newest first)
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return activities[:limit]
    
    def save_memory(self, memory_type: str, data: dict) -> bool:
        """Save data to memory (for tracking processed items)"""
        memory_file = MEMORY_PATH / f"{memory_type}.json"
        
        # Load existing memory
        existing = []
        if memory_file.exists():
            try:
                existing = json.loads(memory_file.read_text(encoding="utf-8"))
            except:
                existing = []
        
        # Add new data
        if isinstance(data, list):
            existing.extend(data)
        else:
            existing.append(data)
        
        # Save back
        return self.write_file(memory_file, json.dumps(existing, indent=2))
    
    def get_memory(self, memory_type: str) -> Optional[dict]:
        """Get memory data"""
        memory_file = MEMORY_PATH / f"{memory_type}.json"
        
        if not memory_file.exists():
            return None
        
        try:
            return json.loads(memory_file.read_text(encoding="utf-8"))
        except:
            return None


# Singleton instance
_vault_reader = None

def get_vault_reader() -> VaultReader:
    """Get singleton VaultReader instance"""
    global _vault_reader
    if _vault_reader is None:
        _vault_reader = VaultReader()
    return _vault_reader


# Convenience functions
def read_file(file_path: Path) -> Optional[str]:
    return get_vault_reader().read_file(file_path)

def write_file(file_path: Path, content: str) -> bool:
    return get_vault_reader().write_file(file_path, content)

def get_stats() -> Dict:
    return get_vault_reader().get_stats()

def get_activity_log(limit: int = 20) -> List[Dict]:
    return get_vault_reader().get_activity_log(limit)


# Test
if __name__ == "__main__":
    reader = VaultReader()
    
    print("=" * 60)
    print("VAULT READER TEST")
    print("=" * 60)
    
    stats = reader.get_stats()
    print(f"\nVault Statistics:")
    print(f"  Inbox: {stats['inbox_count']}")
    print(f"  Needs Action: {stats['needs_action_count']}")
    print(f"  Plans: {stats['plans_count']}")
    print(f"  Pending Approvals: {stats['pending_approvals_count']}")
    print(f"  Completed: {stats['completed_count']}")
    print(f"  Completed Today: {stats['completed_today']}")
    
    print(f"\nRecent Activity:")
    activities = reader.get_activity_log(5)
    for activity in activities:
        print(f"  [{activity['type']}] {activity['description']}")
    
    print("=" * 60)
