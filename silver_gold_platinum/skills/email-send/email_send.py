import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import sys
from pathlib import Path

# Force reload .env from project root
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Add approval system to path
sys.path.insert(0, str(Path(__file__).parent.parent / "human-approval"))
from human_approval import check_approval_needed


def send_email(recipient, subject="No Subject", body="", require_approval=True):
    """
    Send an email based on the provided parameters.
    
    Args:
        recipient: Email address of the recipient
        subject: Email subject line
        body: Email body content
        require_approval: If True, requires human approval before sending (default: True)
    
    Returns:
        dict: {'success': bool, 'message/error': str, 'details': dict}
    """

    # Validate required fields
    if not recipient:
        return {
            'success': False,
            'error': 'Recipient email address is required'
        }

    # Get email credentials from environment variables
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')

    # Validate configuration
    if not email_address or not email_password:
        return {
            'success': False,
            'error': 'Email credentials not configured in environment variables'
        }
    
    if email_password == 'your_app_password_here':
        return {
            'success': False,
            'error': 'EMAIL_PASSWORD is still set to placeholder. Please configure your Gmail App Password in .env'
        }

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient
    msg['Subject'] = subject

    # Add body to email
    msg.attach(MIMEText(body, 'plain'))

    # Prepare action data for approval
    action_data = {
        'recipient': recipient,
        'subject': subject,
        'body_preview': body[:500] + ('...' if len(body) > 500 else ''),
        'from_account': email_address
    }

    # HUMAN-IN-THE-LOOP APPROVAL
    if require_approval:
        print("\n" + "=" * 70)
        print("EMAIL SENDING - HUMAN APPROVAL REQUIRED")
        print("=" * 70)
        print(f"\nFROM:    {email_address}")
        print(f"TO:      {recipient}")
        print(f"SUBJECT: {subject}")
        print(f"\nBODY PREVIEW:")
        print("-" * 70)
        # Show first 1000 chars of body
        preview = body[:1000] + ('...\n[Body truncated]' if len(body) > 1000 else '')
        print(preview)
        print("-" * 70)
        print(f"\nThis email will be sent from: {email_address}")
        print("\nApprove sending this email?")
        
        while True:
            response = input("Type 'yes' to approve, 'no' to cancel: ").strip().lower()
            if response in ['yes', 'y']:
                print("Email sending APPROVED\n")
                break
            elif response in ['no', 'n']:
                print("Email sending CANCELLED by user\n")
                return {
                    'success': False,
                    'error': 'User cancelled email sending',
                    'details': action_data
                }
            else:
                print("Invalid response. Please type 'yes' or 'no'.")

    # Connect to server and send email
    try:
        print(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")
        print(f"Authenticating as: {email_address}")

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)
        text = msg.as_string()
        server.sendmail(email_address, recipient, text)
        server.quit()

        print(f"Email sent successfully to {recipient}")

        return {
            'success': True,
            'message': f'Email sent successfully to {recipient}',
            'details': {
                'recipient': recipient,
                'subject': subject,
                'from_account': email_address
            }
        }
    except smtplib.SMTPAuthenticationError:
        error_msg = f"SMTP Authentication failed. Verify EMAIL_ADDRESS and EMAIL_PASSWORD in .env"
        print(f"ERROR: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except smtplib.SMTPConnectError:
        error_msg = f"Failed to connect to SMTP server {smtp_server}:{smtp_port}"
        print(f"ERROR: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"Failed to send email: {type(e).__name__}: {str(e)}"
        print(f"ERROR: {error_msg}")
        return {
            'success': False,
            'error': error_msg
        }
