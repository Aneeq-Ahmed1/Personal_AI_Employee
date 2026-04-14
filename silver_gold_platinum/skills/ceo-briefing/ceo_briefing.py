"""
CEO Briefing Generator - Gold Tier

Generates executive briefings from vault data, including:
- Daily/Weekly task summaries
- Key metrics and KPIs
- Pending approvals
- Completed work highlights
- AI recommendations
"""

import os
import json
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
logger = logging.getLogger('ceo_briefing')

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
BRIEFINGS_PATH = VAULT_BASE / 'CEO_Briefings'


class CEOBriefingGenerator:
    """Generate executive briefings from vault data"""
    
    def __init__(self):
        self.vault_base = VAULT_BASE
        
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
                        'maxOutputTokens': 4096
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
                    'max_tokens': 4096,
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
    
    def _count_files(self, path: Path) -> int:
        """Count markdown files in a directory"""
        if not path.exists():
            return 0
        return len(list(path.glob('*.md')))
    
    def _read_recent_files(self, path: Path, limit: int = 5) -> list:
        """Read recent markdown files from a directory"""
        if not path.exists():
            return []
        
        files = sorted(path.glob('*.md'), key=lambda f: f.stat().st_mtime, reverse=True)[:limit]
        
        contents = []
        for file in files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    contents.append({
                        'filename': file.stem,
                        'content': f.read()[:500],  # First 500 chars
                        'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
            except Exception as e:
                logger.error(f"Error reading {file}: {str(e)}")
        
        return contents
    
    def _get_dashboard_stats(self) -> dict:
        """Get stats from dashboard API if available"""
        try:
            response = requests.get('http://localhost:8000/api/stats', timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        
        # Fallback to manual counting
        return {
            'inbox': self._count_files(INBOX_PATH),
            'needs_action': self._count_files(NEEDS_ACTION_PATH),
            'completed': self._count_files(COMPLETED_PATH),
            'plans': self._count_files(PLANS_PATH)
        }
    
    def _read_audit_log(self, days: int = 1) -> list:
        """Read recent audit log entries"""
        audit_path = VAULT_BASE / 'Audit'
        
        if not audit_path.exists():
            return []
        
        entries = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file in audit_path.glob('audit_*.json'):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    entries.extend(data[-20:])  # Last 20 entries per file
            except Exception as e:
                logger.error(f"Error reading audit file {file}: {str(e)}")
        
        return entries
    
    def generate_daily_briefing(self, date: datetime = None) -> dict:
        """Generate daily executive briefing"""
        
        if date is None:
            date = datetime.now()
        
        logger.info(f"Generating daily briefing for {date.strftime('%Y-%m-%d')}")
        
        # Gather data
        stats = self._get_dashboard_stats()
        completed_tasks = self._read_recent_files(COMPLETED_PATH, 10)
        pending_tasks = self._read_recent_files(NEEDS_ACTION_PATH, 5)
        audit_entries = self._read_audit_log(days=1)
        
        # Prepare context for AI
        context = {
            'date': date.strftime('%Y-%m-%d'),
            'stats': stats,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'audit_count': len(audit_entries)
        }
        
        system_prompt = """You are an executive assistant AI. Generate a concise, professional CEO briefing based on the provided data.

The briefing should include:
1. Executive Summary (2-3 sentences)
2. Key Metrics (bullet points)
3. Completed Work Highlights
4. Pending Decisions/Approvals
5. AI Recommendations

Keep it professional, concise, and action-oriented."""
        
        prompt = f"""Generate a CEO Daily Briefing for {date.strftime('%A, %B %d, %Y')}

## Data Summary:
- Inbox Items: {stats.get('inbox', 0)}
- Pending Approvals: {stats.get('needs_action', 0)}
- Completed Tasks: {stats.get('completed', 0)}
- Active Plans: {stats.get('plans', 0)}
- Audit Log Entries (today): {context['audit_count']}

## Recently Completed Tasks:
{json.dumps(completed_tasks[:5], indent=2)}

## Pending Approvals:
{json.dumps(pending_tasks, indent=2)}

Generate the executive briefing in markdown format."""
        
        try:
            briefing_content = self._call_ai(prompt, system_prompt)
            
            briefing = {
                'type': 'daily',
                'date': date.isoformat(),
                'generated_at': datetime.now().isoformat(),
                'stats': stats,
                'content': briefing_content,
                'context': context
            }
            
            # Save briefing
            self._save_briefing(briefing)
            
            logger.info(f"Daily briefing generated successfully")
            return briefing
            
        except Exception as e:
            logger.error(f"Error generating daily briefing: {str(e)}")
            return {
                'type': 'daily',
                'date': date.isoformat(),
                'error': str(e)
            }
    
    def generate_weekly_briefing(self, week_start: datetime = None) -> dict:
        """Generate weekly executive briefing"""
        
        if week_start is None:
            # Get current week start (Monday)
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        logger.info(f"Generating weekly briefing for {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}")
        
        # Gather weekly data
        stats = self._get_dashboard_stats()
        
        # Read audit log for the week
        audit_entries = self._read_audit_log(days=7)
        
        # Calculate weekly metrics
        completed_this_week = len([e for e in audit_entries if e.get('result', {}).get('success', False)])
        failed_this_week = len(audit_entries) - completed_this_week
        
        # Get top task types
        task_types = {}
        for entry in audit_entries:
            action = entry.get('action', 'unknown')
            task_types[action] = task_types.get(action, 0) + 1
        
        context = {
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d'),
            'stats': stats,
            'completed_this_week': completed_this_week,
            'failed_this_week': failed_this_week,
            'task_types': task_types,
            'total_actions': len(audit_entries)
        }
        
        system_prompt = """You are an executive assistant AI. Generate a comprehensive weekly CEO briefing.

The briefing should include:
1. Executive Summary
2. Weekly Metrics & KPIs
3. Top Accomplishments
4. Key Challenges
5. Pending Decisions
6. Next Week Priorities
7. AI Strategic Recommendations

Keep it strategic, data-driven, and actionable."""
        
        prompt = f"""Generate a CEO Weekly Briefing for the week of {week_start.strftime('%B %d, %Y')} to {week_end.strftime('%B %d, %Y')}

## Weekly Metrics:
- Total Actions Executed: {context['total_actions']}
- Successful: {completed_this_week}
- Failed: {failed_this_week}
- Success Rate: {completed_this_week/context['total_actions']*100:.1f}% if {context['total_actions']} > 0 else 0%

## Current Status:
- Inbox: {stats.get('inbox', 0)} items
- Pending Approvals: {stats.get('needs_action', 0)} items
- Completed (total): {stats.get('completed', 0)} items

## Task Distribution:
{json.dumps(task_types, indent=2)}

Generate the weekly executive briefing in markdown format."""
        
        try:
            briefing_content = self._call_ai(prompt, system_prompt)
            
            briefing = {
                'type': 'weekly',
                'week_start': week_start.isoformat(),
                'week_end': week_end.isoformat(),
                'generated_at': datetime.now().isoformat(),
                'stats': stats,
                'weekly_metrics': {
                    'total_actions': context['total_actions'],
                    'successful': completed_this_week,
                    'failed': failed_this_week,
                    'task_types': task_types
                },
                'content': briefing_content,
                'context': context
            }
            
            # Save briefing
            self._save_briefing(briefing)
            
            logger.info(f"Weekly briefing generated successfully")
            return briefing
            
        except Exception as e:
            logger.error(f"Error generating weekly briefing: {str(e)}")
            return {
                'type': 'weekly',
                'week_start': week_start.isoformat(),
                'error': str(e)
            }
    
    def _save_briefing(self, briefing: dict):
        """Save briefing to vault"""
        
        BRIEFINGS_PATH.mkdir(parents=True, exist_ok=True)
        
        if briefing['type'] == 'daily':
            date_str = datetime.fromisoformat(briefing['date']).strftime('%Y-%m-%d')
            filename = f"Daily_Briefing_{date_str}.md"
        else:
            week_start = datetime.fromisoformat(briefing['week_start'])
            date_str = week_start.strftime('%Y-%m-%d')
            filename = f"Weekly_Briefing_{date_str}.md"
        
        filepath = BRIEFINGS_PATH / filename
        
        # Generate markdown file
        markdown_content = f"""# CEO Briefing: {briefing.get('type', 'Executive').title()}

**Generated:** {datetime.fromisoformat(briefing['generated_at']).strftime('%Y-%m-%d %H:%M:%S')}

---

{briefing.get('content', 'No content generated')}

---

## Appendix: Raw Data

### Statistics
```json
{json.dumps(briefing.get('stats', {}), indent=2)}
```

### Context
```json
{json.dumps(briefing.get('context', {}), indent=2)}
```

---
*Generated by AI Employee - CEO Briefing Generator*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"Briefing saved to {filepath}")
    
    def get_briefing_history(self, limit: int = 10) -> list:
        """Get list of recent briefings"""
        
        if not BRIEFINGS_PATH.exists():
            return []
        
        files = sorted(BRIEFINGS_PATH.glob('*.md'), key=lambda f: f.stat().st_mtime, reverse=True)[:limit]
        
        return [
            {
                'filename': f.stem,
                'path': str(f),
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in files
        ]
    
    def send_briefing_email(self, briefing: dict, recipient: str) -> dict:
        """Send briefing via email"""
        
        try:
            # Use email MCP server
            mcp_url = 'http://localhost:5000/send_email'
            
            subject = f"CEO {'Daily' if briefing['type'] == 'daily' else 'Weekly'} Briefing - {datetime.now().strftime('%Y-%m-%d')}"
            
            payload = {
                'recipient': recipient,
                'subject': subject,
                'body': briefing.get('content', 'No content available')
            }
            
            response = requests.post(mcp_url, json=payload, timeout=30)
            
            if response.status_code in [200, 201]:
                return {'success': True, 'message': 'Briefing sent via email'}
            else:
                return {'success': False, 'error': f'Email API returned {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}


def generate_briefing(briefing_type: str = 'daily', send_email: bool = False, recipient: str = None):
    """
    Generate a CEO briefing.
    
    Args:
        briefing_type: 'daily' or 'weekly'
        send_email: Whether to send via email
        recipient: Email recipient (required if send_email=True)
    
    Returns:
        dict: Generated briefing
    """
    generator = CEOBriefingGenerator()
    
    if briefing_type == 'daily':
        briefing = generator.generate_daily_briefing()
    else:
        briefing = generator.generate_weekly_briefing()
    
    if send_email and recipient:
        result = generator.send_briefing_email(briefing, recipient)
        briefing['email_sent'] = result
    
    return briefing


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='CEO Briefing Generator')
    parser.add_argument('--type', choices=['daily', 'weekly'], default='daily', help='Briefing type')
    parser.add_argument('--send-email', action='store_true', help='Send briefing via email')
    parser.add_argument('--recipient', type=str, help='Email recipient')
    parser.add_argument('--history', action='store_true', help='Show briefing history')
    
    args = parser.parse_args()
    
    generator = CEOBriefingGenerator()
    
    if args.history:
        history = generator.get_briefing_history()
        print(json.dumps(history, indent=2))
        return
    
    briefing = generate_briefing(args.type, args.send_email, args.recipient)
    
    if 'content' in briefing:
        print(briefing['content'])
    elif 'error' in briefing:
        print(f"Error: {briefing['error']}")


if __name__ == '__main__':
    main()
