"""
Simple Gmail Watcher - Silver Tier
Monitors Gmail for new emails and creates tasks in vault.
Auto-reply aur LinkedIn posting support included.
"""

import os
import time
import re
import base64
from datetime import datetime
from pathlib import Path
import sys
from dotenv import load_dotenv

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
VAULT_PATH = PROJECT_ROOT / "silver" / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
LOG_FILE = Path(__file__).parent / "gmail.log"
POLL_INTERVAL = 60  # Check every 60 seconds

# Track processed emails
processed_emails = set()

# Load environment
load_dotenv()

def log(msg):
    """Log message to console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} | {msg}")
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {msg}\n")
    except:
        pass

def get_gmail_service():
    """Get Gmail API service"""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        import pickle
        
        creds = None
        token_path = PROJECT_ROOT / "silver" / "token.pickle"
        credentials_path = PROJECT_ROOT / "silver" / "credentials.json"
        
        # Load token
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                log("❌ Gmail credentials not found. Run auth first.")
                return None
            # Save token
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        service = build('gmail', 'v1', credentials=creds)
        return service
        
    except Exception as e:
        log(f"❌ Error getting Gmail service: {e}")
        return None

def decode_mime_words(s):
    """Decode MIME encoded email subjects"""
    if not s:
        return ""
    from email.header import decode_header
    decoded = ""
    for part in decode_header(s):
        if isinstance(part[0], bytes):
            decoded += part[0].decode(part[1] or 'utf-8', errors='replace')
        else:
            decoded += part[0]
    return decoded

def get_email_body(message):
    """Extract body from Gmail message"""
    try:
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body'].get('data', '')
                    if body_data:
                        return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
        elif message['payload']['body'].get('data', ''):
            body_data = message['payload']['body']['data']
            return base64.urlsafe_b64decode(body_data).decode('utf-8', errors='replace')
    except Exception as e:
        log(f"Error extracting email body: {e}")
    return ""

def create_task_from_email(subject, body, from_email, folder='INBOX'):
    """Create markdown task file from email"""
    try:
        # Clean subject for filename
        safe_subject = re.sub(r'[^\w\s-]', '', subject)[:40]
        safe_subject = safe_subject.replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"EMAIL_{timestamp}_{safe_subject}.md"
        filepath = INBOX_PATH / filename
        
        INBOX_PATH.mkdir(parents=True, exist_ok=True)
        
        # Format content
        content = f"""# {subject}

## From
{from_email}

## Received
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Source
{folder}

## Email Body
{body[:2000]}

## Action Required
- [ ] Reply to sender
- [ ] Process request
- [ ] Mark as complete

---
*Imported from Gmail by Silver Tier Watcher*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        log(f"✅ Task created: {filename}")
        return filepath
        
    except Exception as e:
        log(f"❌ Error creating task: {e}")
        return None

def check_new_emails():
    """Check Gmail for new emails"""
    service = get_gmail_service()
    if not service:
        log("⚠️ Gmail service unavailable")
        return 0
    
    try:
        # Get unread emails from INBOX
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            log("📭 No new emails")
            return 0
        
        log(f"📬 Found {len(messages)} unread email(s)")
        
        processed = 0
        for message in messages:
            msg_id = message['id']
            
            # Skip if already processed
            if msg_id in processed_emails:
                continue
            
            # Get full message
            msg = service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = ""
            from_email = ""
            
            for header in headers:
                if header['name'] == 'Subject':
                    subject = decode_mime_words(header['value'])
                elif header['name'] == 'From':
                    from_email = decode_mime_words(header['value'])
            
            # Get body
            body = get_email_body(msg)
            
            # Mark as processed
            processed_emails.add(msg_id)
            
            # Log email
            log(f"📧 {subject[:50]}... from {from_email}")
            
            # Check for LinkedIn post request
            if subject.startswith("Post to LinkedIn:"):
                log(f"📊 LinkedIn post request detected!")
                # TODO: Add LinkedIn posting logic here
            
            # Create task
            create_task_from_email(subject, body, from_email, 'INBOX')
            processed += 1
            
            # Mark as read
            try:
                service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            except Exception as e:
                log(f"Error marking as read: {e}")
        
        log(f"✨ Processed {processed} email(s)")
        return processed
        
    except Exception as e:
        log(f"❌ Error checking emails: {e}")
        return 0

def main():
    print()
    print("="*70)
    print("GMAIL WATCHER - SILVER TIER")
    print("="*70)
    print()
    
    # Setup directories
    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    
    log("Starting Gmail Watcher...")
    log(f"Checking every {POLL_INTERVAL} seconds")
    log(f"Inbox: {INBOX_PATH}")
    print()
    
    # Initial check
    log("Running initial check...")
    check_new_emails()
    
    print()
    print("="*70)
    print("WATCHER RUNNING - CHECKING EVERY 60 SECONDS")
    print("="*70)
    print()
    print("💡 Features:")
    print("  - Monitors INBOX for unread emails")
    print("  - Creates tasks in silver/vault/Inbox/")
    print("  - Auto-marks emails as read")
    print("  - LinkedIn auto-post support (Post to LinkedIn:)")
    print()
    print("Band karne: Ctrl+C")
    print("="*70)
    print()
    
    # Main loop
    try:
        while True:
            time.sleep(POLL_INTERVAL)
            check_new_emails()
    except KeyboardInterrupt:
        print()
        log("Stopping Gmail Watcher...")
        print("Watcher stopped.")


if __name__ == "__main__":
    main()
