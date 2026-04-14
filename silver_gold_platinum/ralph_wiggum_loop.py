"""
Ralph Wiggum Loop - Gold Tier Autonomous Execution Engine

This is the autonomy engine that enables multi-step task execution without
constant human intervention. Named after Ralph Wiggum for his persistent
"My cat doesn't eat meatloaf" loop - but productive!

The loop:
1. Check vault for tasks needing action
2. Analyze with AI reasoning
3. Create execution plan
4. Execute approved steps
5. Learn from feedback
6. Repeat
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ralph_wiggum_loop')

# AI Provider Configuration
AI_PROVIDERS = {
    'gemini': {
        'api_key': os.getenv('GEMINI_API_KEY', ''),
        'url': 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent',
        'enabled': True
    },
    'openrouter': {
        'api_key': os.getenv('OPENROUTER_API_KEY', ''),
        'url': 'https://openrouter.ai/api/v1/chat/completions',
        'model': 'anthropic/claude-3-5-sonnet',
        'enabled': True
    }
}

# Vault paths
VAULT_BASE = Path('vault')
INBOX_PATH = VAULT_BASE / 'Inbox'
NEEDS_ACTION_PATH = VAULT_BASE / 'Needs_Action'
PLANS_PATH = VAULT_BASE / 'Plans'
COMPLETED_PATH = VAULT_BASE / 'Completed'
AUDIT_PATH = VAULT_BASE / 'Audit'

# MCP Server URLs
MCP_SERVERS = {
    'email': 'http://localhost:5000',
    'odoo': 'http://localhost:5001',
    'social_media': 'http://localhost:5002'
}

# Execution configuration
MAX_CONSECUTIVE_FAILURES = 3
LOOP_INTERVAL_SECONDS = 30  # Check every 30 seconds
AUTO_APPROVE_LOW_RISK = True  # Auto-approve low-risk actions


class RalphWiggumLoop:
    """Autonomous multi-step task execution engine"""
    
    def __init__(self):
        self.consecutive_failures = 0
        self.tasks_processed = 0
        self.last_activity = datetime.now()
        self.learning_data = self._load_learning_data()
        
    def _load_learning_data(self) -> dict:
        """Load historical learning data for better decisions"""
        learning_file = VAULT_BASE / 'learning_data.json'
        if learning_file.exists():
            with open(learning_file, 'r') as f:
                return json.load(f)
        return {
            'approved_patterns': [],
            'rejected_patterns': [],
            'task_success_rate': {},
            'preferred_times': []
        }
    
    def _save_learning_data(self):
        """Save learning data for future improvements"""
        learning_file = VAULT_BASE / 'learning_data.json'
        with open(learning_file, 'w') as f:
            json.dump(self.learning_data, f, indent=2)
    
    def _call_ai(self, prompt: str, system_prompt: str = None) -> str:
        """Call AI provider with fallback"""
        
        # Try Gemini first
        if AI_PROVIDERS['gemini']['enabled'] and AI_PROVIDERS['gemini']['api_key']:
            try:
                headers = {'Content-Type': 'application/json'}
                payload = {
                    'contents': [{
                        'parts': [{'text': prompt}]
                    }],
                    'generationConfig': {
                        'temperature': 0.7,
                        'maxOutputTokens': 2048
                    }
                }
                
                url = f"{AI_PROVIDERS['gemini']['url']}?key={AI_PROVIDERS['gemini']['api_key']}"
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        return result['candidates'][0]['content']['parts'][0]['text']
                
                logger.warning(f"Gemini API returned status {response.status_code}")
            except Exception as e:
                logger.warning(f"Gemini API error: {str(e)}, falling back to OpenRouter")
        
        # Fallback to OpenRouter
        if AI_PROVIDERS['openrouter']['enabled'] and AI_PROVIDERS['openrouter']['api_key']:
            try:
                headers = {
                    'Authorization': f"Bearer {AI_PROVIDERS['openrouter']['api_key']}",
                    'Content-Type': 'application/json'
                }
                
                messages = []
                if system_prompt:
                    messages.append({'role': 'system', 'content': system_prompt})
                messages.append({'role': 'user', 'content': prompt})
                
                payload = {
                    'model': AI_PROVIDERS['openrouter']['model'],
                    'messages': messages,
                    'max_tokens': 2048,
                    'temperature': 0.7
                }
                
                response = requests.post(
                    AI_PROVIDERS['openrouter']['url'],
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                
                logger.warning(f"OpenRouter API returned status {response.status_code}")
            except Exception as e:
                logger.error(f"OpenRouter API error: {str(e)}")
        
        raise Exception("All AI providers failed")
    
    def _scan_inbox(self) -> list:
        """Scan inbox for new tasks"""
        tasks = []
        
        if not INBOX_PATH.exists():
            INBOX_PATH.mkdir(parents=True, exist_ok=True)
            return tasks
        
        for file in INBOX_PATH.glob('*.md'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tasks.append({
                    'id': file.stem,
                    'file': file,
                    'content': content,
                    'created': datetime.fromtimestamp(file.stat().st_mtime)
                })
            except Exception as e:
                logger.error(f"Error reading {file}: {str(e)}")
        
        return tasks
    
    def _scan_needs_action(self) -> list:
        """Scan Needs_Action folder for pending tasks"""
        tasks = []
        
        if not NEEDS_ACTION_PATH.exists():
            return tasks
        
        for file in NEEDS_ACTION_PATH.glob('*.md'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if approval is pending
                if '[APPROVED]' in content or '[REJECTED]' in content:
                    continue
                
                tasks.append({
                    'id': file.stem,
                    'file': file,
                    'content': content,
                    'created': datetime.fromtimestamp(file.stat().st_mtime)
                })
            except Exception as e:
                logger.error(f"Error reading {file}: {str(e)}")
        
        return tasks
    
    def _analyze_task(self, task: dict) -> dict:
        """Analyze task with AI and determine action plan"""
        
        system_prompt = """You are an autonomous task execution engine. Analyze tasks and determine:
1. What action needs to be taken
2. Which MCP server to use
3. Whether this is low-risk (auto-approve) or high-risk (needs human approval)
4. The exact parameters for the action

Respond in JSON format:
{
    "action": "send_email" | "post_social" | "create_invoice" | "other",
    "mcp_server": "email" | "social_media" | "odoo",
    "risk_level": "low" | "medium" | "high",
    "auto_approve": true | false,
    "parameters": {...},
    "reasoning": "Why this action was chosen"
}"""
        
        prompt = f"""Analyze this task and determine the appropriate action:

Task File: {task['id']}.md
Task Content:
{task['content']}

Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Based on the task content, determine what action needs to be taken."""
        
        try:
            response = self._call_ai(prompt, system_prompt)
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
                analysis['task_id'] = task['id']
                return analysis
            else:
                logger.warning(f"Could not parse JSON from AI response: {response}")
                return {
                    'action': 'unknown',
                    'risk_level': 'high',
                    'auto_approve': False,
                    'reasoning': 'Could not parse AI response'
                }
                
        except Exception as e:
            logger.error(f"Error analyzing task: {str(e)}")
            return {
                'action': 'unknown',
                'risk_level': 'high',
                'auto_approve': False,
                'error': str(e)
            }
    
    def _execute_action(self, analysis: dict) -> dict:
        """Execute the analyzed action via MCP server"""
        
        action = analysis.get('action')
        mcp_server = analysis.get('mcp_server')
        parameters = analysis.get('parameters', {})
        
        if not action or not mcp_server:
            return {'success': False, 'error': 'Invalid analysis'}
        
        mcp_url = MCP_SERVERS.get(mcp_server)
        if not mcp_url:
            return {'success': False, 'error': f'MCP server {mcp_server} not available'}
        
        try:
            # Map actions to endpoints
            endpoint_map = {
                ('email', 'send_email'): '/send_email',
                ('social_media', 'post_social'): '/post',
                ('odoo', 'create_invoice'): '/account/invoices',
                ('odoo', 'get_invoices'): '/account/invoices',
            }
            
            endpoint = endpoint_map.get((mcp_server, action))
            if not endpoint:
                # Try generic endpoint
                endpoint = f'/{mcp_server}/{action}'
            
            url = f"{mcp_url}{endpoint}"
            
            logger.info(f"Executing {action} via {mcp_server} at {url}")
            
            response = requests.post(url, json=parameters, timeout=30)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return result
            else:
                return {'success': False, 'error': f'MCP returned status {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP server connection error: {str(e)}")
            return {'success': False, 'error': f'Connection error: {str(e)}'}
        except Exception as e:
            logger.error(f"Execution error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _create_plan(self, task: dict, analysis: dict) -> Path:
        """Create a Plan.md file for the task"""
        
        plan_content = f"""# Task Plan: {task['id']}

## Original Task
{task['content']}

## AI Analysis
- **Action**: {analysis.get('action', 'unknown')}
- **MCP Server**: {analysis.get('mcp_server', 'unknown')}
- **Risk Level**: {analysis.get('risk_level', 'unknown')}
- **Auto Approve**: {analysis.get('auto_approve', False)}
- **Reasoning**: {analysis.get('reasoning', 'No reasoning provided')}

## Parameters
```json
{json.dumps(analysis.get('parameters', {}), indent=2)}
```

## Execution Status
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Status**: Pending Execution

---
*Generated by Ralph Wiggum Loop*
"""
        
        plan_file = PLANS_PATH / f"{task['id']}_plan.md"
        plan_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        logger.info(f"Plan created: {plan_file}")
        return plan_file
    
    def _log_audit(self, task_id: str, action: str, result: dict):
        """Log action to audit trail"""
        
        AUDIT_PATH.mkdir(parents=True, exist_ok=True)
        
        audit_file = AUDIT_PATH / f"audit_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        audit_logs = []
        if audit_file.exists():
            with open(audit_file, 'r') as f:
                audit_logs = json.load(f)
        
        audit_logs.append({
            'timestamp': datetime.now().isoformat(),
            'task_id': task_id,
            'action': action,
            'result': result,
            'loop_iteration': self.tasks_processed
        })
        
        with open(audit_file, 'w') as f:
            json.dump(audit_logs, f, indent=2)
    
    def _update_learning(self, task_id: str, action: str, success: bool):
        """Update learning data based on execution results"""
        
        task_type = action.split('_')[0] if '_' in action else action
        
        if task_type not in self.learning_data['task_success_rate']:
            self.learning_data['task_success_rate'][task_type] = {
                'success': 0,
                'failure': 0
            }
        
        if success:
            self.learning_data['task_success_rate'][task_type]['success'] += 1
        else:
            self.learning_data['task_success_rate'][task_type]['failure'] += 1
        
        self._save_learning_data()
    
    def _move_to_completed(self, task: dict, result: dict):
        """Move task to Completed folder"""
        
        COMPLETED_PATH.mkdir(parents=True, exist_ok=True)
        
        # Add completion metadata
        completed_content = f"""{task['content']}

---
## Completed
- **Completed At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Result**: {json.dumps(result, indent=2)}
"""
        
        completed_file = COMPLETED_PATH / f"{task['id']}.md"
        with open(completed_file, 'w', encoding='utf-8') as f:
            f.write(completed_content)
        
        # Remove from original location
        try:
            task['file'].unlink()
        except Exception as e:
            logger.error(f"Error removing original file: {str(e)}")
        
        logger.info(f"Task moved to completed: {task['id']}")
    
    def run_loop_iteration(self):
        """Run a single iteration of the Ralph Wiggum Loop"""
        
        logger.info(f"=== Ralph Wiggum Loop Iteration {self.tasks_processed + 1} ===")
        
        # Scan for tasks
        inbox_tasks = self._scan_inbox()
        action_tasks = self._scan_needs_action()
        
        all_tasks = inbox_tasks + action_tasks
        
        if not all_tasks:
            logger.info("No tasks to process")
            self.last_activity = datetime.now()
            return
        
        # Process each task
        for task in all_tasks:
            logger.info(f"Processing task: {task['id']}")
            
            # Analyze task
            analysis = self._analyze_task(task)
            logger.info(f"Analysis: {analysis.get('action')} (risk: {analysis.get('risk_level')})")
            
            # Create plan
            plan_file = self._create_plan(task, analysis)
            
            # Check if auto-approve
            auto_approve = analysis.get('auto_approve', False)
            
            if not auto_approve:
                # Move to Needs_Action for human approval
                if task['file'].parent != NEEDS_ACTION_PATH:
                    new_file = NEEDS_ACTION_PATH / f"{task['id']}.md"
                    task['file'].rename(new_file)
                    logger.info(f"Task moved to Needs_Action: {task['id']}")
                continue
            
            # Execute action
            result = self._execute_action(analysis)
            
            # Log and update learning
            self._log_audit(task['id'], analysis.get('action'), result)
            self._update_learning(task['id'], analysis.get('action'), result.get('success', False))
            
            if result.get('success'):
                logger.info(f"Task executed successfully: {task['id']}")
                self._move_to_completed(task, result)
                self.consecutive_failures = 0
            else:
                logger.warning(f"Task execution failed: {task['id']} - {result.get('error')}")
                self.consecutive_failures += 1
            
            self.tasks_processed += 1
        
        self.last_activity = datetime.now()
        
        # Check for consecutive failures
        if self.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
            logger.error(f"Max consecutive failures ({MAX_CONSECUTIVE_FAILURES}) reached. Pausing loop.")
            # Could send alert or pause execution
    
    def run_continuous(self):
        """Run the loop continuously"""
        
        logger.info("🚀 Starting Ralph Wiggum Loop (autonomous mode)")
        logger.info(f"Loop interval: {LOOP_INTERVAL_SECONDS} seconds")
        logger.info(f"Auto-approve low risk: {AUTO_APPROVE_LOW_RISK}")
        
        try:
            while True:
                self.run_loop_iteration()
                time.sleep(LOOP_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("Loop stopped by user")
        except Exception as e:
            logger.error(f"Loop error: {str(e)}")
            raise
    
    def get_status(self) -> dict:
        """Get current loop status"""
        return {
            'tasks_processed': self.tasks_processed,
            'consecutive_failures': self.consecutive_failures,
            'last_activity': self.last_activity.isoformat(),
            'learning_data_summary': {
                'task_types': list(self.learning_data['task_success_rate'].keys()),
                'success_rates': {
                    k: f"{v['success']/(v['success']+v['failure'])*100:.1f}%"
                    for k, v in self.learning_data['task_success_rate'].items()
                    if (v['success'] + v['failure']) > 0
                }
            }
        }


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop - Autonomous Task Execution')
    parser.add_argument('--once', action='store_true', help='Run only one iteration')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
    parser.add_argument('--interval', type=int, default=LOOP_INTERVAL_SECONDS, help='Loop interval in seconds')
    
    args = parser.parse_args()
    
    loop = RalphWiggumLoop()
    
    if args.status:
        status = loop.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if args.once:
        loop.run_loop_iteration()
        status = loop.get_status()
        print(json.dumps(status, indent=2))
        return
    
    # Run continuous
    loop.run_continuous()


if __name__ == '__main__':
    main()
