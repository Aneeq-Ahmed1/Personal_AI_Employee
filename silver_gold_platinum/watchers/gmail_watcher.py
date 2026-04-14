"""
Silver Tier Gmail Watcher
Watches Gmail for new emails and creates tasks in Inbox.
Special handling: Emails with subject "Post to LinkedIn:" auto-trigger LinkedIn posting.
"""

import os
import time
import re
import base64
from datetime import datetime
from pathlib import Path
import sys
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add silver skills to path
sys.path.insert(0, str(PROJECT_ROOT / "silver" / "skills" / "linkedin-post"))

# Configuration
VAULT_PATH = PROJECT_ROOT / "silver" / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
LOG_FILE = PROJECT_ROOT / "silver" / "gmail_watcher.log"
POLL_INTERVAL = 60  # Check every 60 seconds

# Track processed message IDs
processed_messages = set()

# LinkedIn skill
linkedin_skill = None

# Load email configuration
load_dotenv()
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

def setup_logging():
    """Setup basic logging to file and console"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


def extract_email_from_header(from_header):
    """Extract email address from From header"""
    import re
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', from_header)
    return match.group(0) if match else from_header


def send_auto_reply(original_from, original_subject, reply_text, original_body, require_approval=True):
    """Send automatic reply to incoming email
    
    Args:
        original_from: Sender's email header
        original_subject: Original email subject
        reply_text: Reply message text
        original_body: Original email body
        require_approval: If True, check for sensitive content before sending
    
    Returns:
        bool: True if reply sent successfully, False otherwise
    """
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logger.error("Email credentials not configured for auto-reply")
        return False
    
    # Extract recipient email
    recipient_email = extract_email_from_header(original_from)
    
    # Create reply subject
    if not original_subject.startswith("Re:"):
        reply_subject = f"Re: {original_subject}"
    else:
        reply_subject = original_subject
    
    # Check if reply contains sensitive content (requires approval)
    if require_approval:
        sensitive_keywords = [
            'payment', 'money', 'bank', 'account', 'password', 'delete',
            'confidential', 'private', 'secret', 'contract', 'legal',
            'agree', 'commit', 'promise', 'guarantee', 'refund'
        ]
        
        reply_lower = reply_text.lower()
        is_sensitive = any(keyword in reply_lower for keyword in sensitive_keywords)
        
        if is_sensitive:
            logger.warning(f"⚠️ SENSITIVE reply detected - requires approval")
            logger.warning(f"Keywords found in reply")
            
            # Import approval system
            try:
                sys.path.insert(0, str(PROJECT_ROOT / "silver" / "skills" / "human-approval"))
                from human_approval import check_approval_needed
                
                approval_data = {
                    'action': 'send_email_reply',
                    'recipient': recipient_email,
                    'subject': reply_subject,
                    'reply_text': reply_text[:200],
                    'original_from': original_from
                }
                
                # Request approval (will wait for user approval)
                # interactive=True means it will ask directly in terminal
                approved = check_approval_needed('email_reply', approval_data, interactive=True)
                
                if not approved:
                    logger.info("❌ Reply REJECTED by user")
                    return False
                
                logger.info("✅ Reply APPROVED by user")
                
            except Exception as e:
                logger.error(f"Approval check failed: {e}")
                logger.info("Proceeding without approval (approval system error)")
    
    # Create email message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg['Subject'] = reply_subject
    
    # Email body
    body = f"""{reply_text}

---
Original Message:
{original_body[:500]}...

--
Sent by Silver Tier AI Employee - Auto Reply System
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Connect and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"✅ Auto-reply sent to: {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Auto-reply failed: {type(e).__name__}: {str(e)}")
        return False


def import_linkedin_skill():
    """Import LinkedIn posting skill"""
    global linkedin_skill
    try:
        from linkedin_post import post_to_linkedin
        linkedin_skill = post_to_linkedin
        logger.info("LinkedIn posting skill imported successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to import LinkedIn skill: {type(e).__name__}: {str(e)}")
        linkedin_skill = None
        return False


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

        # Load token if exists
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.error("Gmail credentials not found. Run test_gmail_auth.py first.")
                return None

            # Save refreshed token
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        return service

    except Exception as e:
        logger.error(f"Failed to get Gmail service: {type(e).__name__}: {str(e)}")
        return None


def decode_mime_words(s):
    """Decode MIME encoded words in email subjects"""
    if not s:
        return ""
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
        logger.error(f"Error extracting email body: {e}")
    return ""


def process_linkedin_post_email(subject, body, from_email):
    """
    Process emails with subject starting with "Post to LinkedIn:"
    Auto-posts content to LinkedIn
    """
    if linkedin_skill is None:
        logger.warning("LinkedIn skill not available - cannot auto-post")
        return False

    # Extract content after "Post to LinkedIn:"
    content = subject.split("Post to LinkedIn:", 1)[1].strip()

    # If body has more content, append it
    if body and len(body) > 10:
        content = f"{content}\n\n{body}"

    logger.info(f"Auto-posting to LinkedIn from email by {from_email}")
    logger.info(f"Content: {content[:100]}...")

    # Post to LinkedIn
    result = linkedin_skill(content, post_title="Business Update")

    if result['success']:
        logger.info("✅ LinkedIn post successful")
        return True
    else:
        logger.error(f"❌ LinkedIn post failed: {result.get('error', 'Unknown error')}")
        return False


def create_task_from_email(subject, body, from_email, timestamp):
    """Create a markdown task file in Inbox from email"""
    # Sanitize subject for filename
    safe_subject = re.sub(r'[^\w\s-]', '', subject)[:50]
    safe_subject = safe_subject.replace(' ', '_')

    filename = f"email_{timestamp}_{safe_subject}.md"
    filepath = INBOX_PATH / filename

    # Format email content
    content = f"""# {subject}

## From
{from_email}

## Received
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Email Body
{body}

---
*Imported from Gmail by Silver Tier Gmail Watcher*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info(f"Task created in Inbox: {filename}")
    return filepath


def check_new_emails():
    """Check Gmail for new emails and process them"""
    service = get_gmail_service()
    if not service:
        return []

    try:
        # STEP 1: Check INBOX for unread messages
        logger.info("Checking INBOX for unread emails...")
        inbox_results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX', 'UNREAD'],
            maxResults=10
        ).execute()

        inbox_messages = inbox_results.get('messages', [])
        logger.info(f"Found {len(inbox_messages)} unread email(s) in INBOX")

        # STEP 2: Check SPAM folder for unread messages
        logger.info("Checking SPAM folder for unread emails...")
        spam_results = service.users().messages().list(
            userId='me',
            labelIds=['SPAM', 'UNREAD'],
            maxResults=10
        ).execute()

        spam_messages = spam_results.get('messages', [])
        logger.info(f"Found {len(spam_messages)} unread email(s) in SPAM")

        # Combine messages from both folders
        all_messages = []
        for msg in inbox_messages:
            msg['folder'] = 'INBOX'
            all_messages.append(msg)
        for msg in spam_messages:
            msg['folder'] = 'SPAM'
            all_messages.append(msg)

        if not all_messages:
            logger.info("No new emails in INBOX or SPAM")
            return []

        logger.info(f"Total emails to process: {len(all_messages)}")

        processed_count = 0
        linkedin_posts = 0
        spam_count = 0
        inbox_count = 0

        for message in all_messages:
            msg_id = message['id']
            folder = message.get('folder', 'INBOX')

            # Skip if already processed
            if msg_id in processed_messages:
                continue

            # Get full message details
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

            # Extract body
            body = get_email_body(msg)

            # Mark as processed
            processed_messages.add(msg_id)

            # Log folder source
            if folder == 'SPAM':
                logger.warning(f"EMAIL FROM SPAM: Subject='{subject}', From='{from_email}'")
                spam_count += 1
            else:
                logger.info(f"EMAIL FROM INBOX: Subject='{subject}', From='{from_email}'")
                inbox_count += 1

            # Check if this is a LinkedIn post request
            if subject.startswith("Post to LinkedIn:"):
                logger.info(f"📧 LinkedIn post email detected: {subject}")
                success = process_linkedin_post_email(subject, body, from_email)
                if success:
                    linkedin_posts += 1
                    # Mark email as read
                    service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                    continue

            # Check if this is an auto-reply request (subject starts with "Reply:")
            if subject.startswith("Reply:"):
                logger.info(f"📧 Auto-reply email detected: {subject}")
                reply_text = subject.replace("Reply:", "").strip()
                success = send_auto_reply(from_email, subject, reply_text, body)
                if success:
                    logger.info("✅ Auto-reply sent successfully")
                    # Mark email as read
                    service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                    continue

            # Regular email - create task in Inbox
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            create_task_from_email(subject, body, from_email, timestamp)
            processed_count += 1

            # Mark email as read
            service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        logger.info(f"Processed: {processed_count} emails (INBOX: {inbox_count}, SPAM: {spam_count}), {linkedin_posts} LinkedIn posts")
        return all_messages

    except Exception as e:
        logger.error(f"Error checking emails: {type(e).__name__}: {str(e)}")
        return []


def main():
    """Main function to start Gmail watcher"""
    logger.info("=" * 60)
    logger.info("SILVER TIER GMAIL WATCHER STARTING")
    logger.info("=" * 60)

    # Setup directories
    INBOX_PATH.mkdir(parents=True, exist_ok=True)

    # Import LinkedIn skill
    import_linkedin_skill()

    logger.info(f"Watching Gmail every {POLL_INTERVAL} seconds")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Initial check
    logger.info("Running initial email check...")
    check_new_emails()

    try:
        while True:
            time.sleep(POLL_INTERVAL)
            check_new_emails()
    except KeyboardInterrupt:
        logger.info("Stopping Gmail watcher...")

    logger.info("Gmail watcher stopped")


if __name__ == "__main__":
    main()
