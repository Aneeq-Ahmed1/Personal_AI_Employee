"""
Platinum Tier - Cloud Gmail Watcher (Draft-Only Mode)
Runs on Cloud VM - Monitors emails and creates draft replies
NEVER sends emails - Local agent handles final send
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger('CloudGmailWatcher')


class CloudGmailWatcher:
    """
    Cloud-based Gmail watcher (Draft-Only Mode)
    
    Responsibilities:
    - Poll Gmail for new emails
    - AI-generate draft replies
    - Write drafts to /Pending_Approval/
    - NEVER send emails (Local agent does that)
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.pending_path = vault_path / 'Pending_Approval'
        self.needs_action_path = vault_path / 'Needs_Action' / 'email'
        self.last_checked_path = vault_path / 'Updates' / 'gmail_last_checked.json'
        
        # Ensure directories exist
        for path in [self.pending_path, self.needs_action_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        self.last_message_id = None
        self._load_last_state()
    
    def _load_last_state(self):
        """Load last checked state"""
        if self.last_checked_path.exists():
            try:
                with open(self.last_checked_path, 'r') as f:
                    state = json.load(f)
                self.last_message_id = state.get('last_message_id')
                logger.info(f"Loaded last state: {self.last_message_id}")
            except:
                pass
    
    def _save_last_state(self, message_id: str):
        """Save last checked state"""
        self.last_message_id = message_id
        
        state = {
            'last_message_id': message_id,
            'last_checked': datetime.now().isoformat(),
            'agent': 'cloud'
        }
        
        with open(self.last_checked_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def check_new_emails(self) -> List[Dict]:
        """
        Check Gmail for new emails
        Returns list of new email data
        """
        try:
            # Import existing Gmail watcher
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from gmail_watcher import GmailWatcher as BaseGmailWatcher
            
            watcher = BaseGmailWatcher()
            
            # Authenticate if needed
            if not watcher.service:
                watcher.authenticate()
            
            if not watcher.service:
                logger.error("Failed to authenticate with Gmail")
                return []
            
            # Get recent messages
            results = watcher.service.users().messages().list(
                userId='me',
                maxResults=10,
                q='is:unread'
            ).execute()
            
            messages = results.get('messages', [])
            new_emails = []
            
            for msg in messages:
                # Get message details
                message = watcher.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Skip if already processed
                if self.last_message_id and msg['id'] == self.last_message_id:
                    continue
                
                # Extract email data
                email_data = self._extract_email_data(message)
                new_emails.append(email_data)
                
                # Update last message ID
                self._save_last_state(msg['id'])
            
            logger.info(f"Found {len(new_emails)} new emails")
            return new_emails
        
        except ImportError:
            logger.warning("Base GmailWatcher not available, using mock data")
            return self._generate_mock_emails()
        
        except Exception as e:
            logger.error(f"Error checking emails: {e}")
            return []
    
    def _extract_email_data(self, message: Dict) -> Dict:
        """Extract relevant data from Gmail message"""
        headers = message.get('payload', {}).get('headers', [])
        
        email_data = {
            'message_id': message.get('id'),
            'thread_id': message.get('threadId'),
            'subject': '',
            'from': '',
            'to': '',
            'date': '',
            'body': '',
            'has_attachments': False
        }
        
        for header in headers:
            if header['name'] == 'Subject':
                email_data['subject'] = header['value']
            elif header['name'] == 'From':
                email_data['from'] = header['value']
            elif header['name'] == 'To':
                email_data['to'] = header['value']
            elif header['name'] == 'Date':
                email_data['date'] = header['value']
        
        # Extract body
        payload = message.get('payload', {})
        if 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    import base64
                    body = part.get('body', {}).get('data', '')
                    if body:
                        email_data['body'] = base64.urlsafe_b64decode(body).decode('utf-8')
        elif 'body' in payload:
            import base64
            body = payload['body'].get('data', '')
            if body:
                email_data['body'] = base64.urlsafe_b64decode(body).decode('utf-8')
        
        return email_data
    
    def create_draft_reply(self, email_data: Dict) -> Dict:
        """Create AI-powered draft reply"""
        
        # TODO: Integrate with AI reasoning engine
        # For now, use simple template
        
        subject = email_data.get('subject', '')
        sender = email_data.get('from', '')
        body = email_data.get('body', '')
        
        # Generate reply based on email content
        reply_body = self._generate_ai_reply(subject, sender, body)
        
        draft = {
            'type': 'email_draft',
            'original_email': {
                'subject': subject,
                'from': sender,
                'date': email_data.get('date', ''),
                'message_id': email_data.get('message_id')
            },
            'draft_reply': {
                'to': sender,
                'subject': f"Re: {subject}",
                'body': reply_body,
                'attachments': []
            },
            'created_at': datetime.now().isoformat(),
            'created_by': 'cloud_gmail_watcher',
            'status': 'pending_approval',
            'assigned_to': 'cloud',
            'risk_level': 'low'
        }
        
        return draft
    
    def _generate_ai_reply(self, subject: str, sender: str, body: str) -> str:
        """Generate AI-powered reply (placeholder)"""
        
        # Simple keyword-based reply generation
        subject_lower = subject.lower()
        body_lower = body.lower()
        
        # Meeting requests
        if any(word in subject_lower for word in ['meeting', 'schedule', 'calendar']):
            return f"""Hi,

Thank you for your email regarding "{subject}".

I've received your request and will check the schedule. I'll confirm the meeting time shortly.

Best regards,
AI Employee"""
        
        # Questions
        elif any(word in body_lower for word in ['question', 'could you', 'can you', 'please']):
            return f"""Hi,

Thank you for reaching out. I've received your email and will look into this.

I'll get back to you with a detailed response soon.

Best regards,
AI Employee"""
        
        # Default reply
        else:
            return f"""Hi,

Thank you for your email regarding "{subject}".

I've received your message and will review it carefully. I'll respond with more details shortly.

Best regards,
AI Employee"""
    
    def write_draft_to_approval(self, draft: Dict):
        """Write draft to Pending_Approval for Local agent"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"email_draft_{timestamp}.json"
        
        filepath = self.pending_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(draft, f, indent=2)
        
        logger.info(f"✅ Draft reply written to: {filename}")
    
    def write_needs_action(self, email_data: Dict):
        """Write email to Needs_Action for processing"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"email_{timestamp}.md"
        
        filepath = self.needs_action_path / filename
        
        content = f"""---
type: email
subject: {email_data.get('subject', '')}
from: {email_data.get('from', '')}
date: {email_data.get('date', '')}
message_id: {email_data.get('message_id')}
status: needs_action
created_at: {datetime.now().isoformat()}
---

# Email: {email_data.get('subject', '')}

**From:** {email_data.get('from', '')}
**Date:** {email_data.get('date', '')}

## Body

{email_data.get('body', '')}

## Action Required

This email requires attention. Cloud agent will process and create draft reply.
"""
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        logger.info(f"✅ Email written to Needs_Action: {filename}")
    
    def process_emails(self):
        """Main processing cycle"""
        logger.info("📧 Cloud Gmail Watcher - Checking emails...")
        
        # Get new emails
        new_emails = self.check_new_emails()
        
        for email_data in new_emails:
            logger.info(f"📬 New email: {email_data['subject']}")
            
            # Write to Needs_Action
            self.write_needs_action(email_data)
            
            # Create draft reply
            draft = self.create_draft_reply(email_data)
            
            # Write to Pending_Approval
            self.write_draft_to_approval(draft)
        
        return len(new_emails)
    
    def _generate_mock_emails(self) -> List[Dict]:
        """Generate mock emails for testing"""
        mock_emails = [
            {
                'subject': 'Meeting Request - Project Update',
                'from': 'john.doe@example.com',
                'date': datetime.now().isoformat(),
                'body': 'Hi, can we schedule a meeting to discuss the project progress?',
                'message_id': 'mock_001'
            },
            {
                'subject': 'Invoice #12345',
                'from': 'billing@vendor.com',
                'date': datetime.now().isoformat(),
                'body': 'Please find attached invoice for services rendered.',
                'message_id': 'mock_002'
            }
        ]
        
        logger.info(f"Generated {len(mock_emails)} mock emails")
        return mock_emails


def main():
    """Test cloud Gmail watcher"""
    vault_path = Path(os.environ.get('VAULT_PATH', '../vault'))
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        return
    
    watcher = CloudGmailWatcher(vault_path)
    
    logger.info("Starting Cloud Gmail Watcher (Draft-Only Mode)...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            count = watcher.process_emails()
            logger.info(f"✅ Processed {count} emails")
            
            # Sleep for 60 seconds
            import time
            time.sleep(60)
    
    except KeyboardInterrupt:
        logger.info("Cloud Gmail Watcher stopped")


if __name__ == '__main__':
    main()
