import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ApprovalManager:
    def __init__(self):
        self.approvals_dir = Path("vault/Approvals")
        self.approvals_dir.mkdir(parents=True, exist_ok=True)
        self.email_notifications = os.getenv('EMAIL_NOTIFICATIONS', 'true').lower() == 'true'
        self.notification_email = os.getenv('NOTIFICATION_EMAIL', os.getenv('EMAIL_ADDRESS', ''))

    def send_email_notification(self, action_type, action_data, request_path):
        """Send email notification when approval is needed"""
        if not self.email_notifications:
            return False

        # Get email configuration
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        email_address = os.getenv('EMAIL_ADDRESS', '')
        email_password = os.getenv('EMAIL_PASSWORD', '')

        if not email_address or not email_password or email_password == 'your_app_password_here':
            print("[EMAIL NOTIFICATION] Email credentials not configured - skipping notification")
            return False

        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = self.notification_email or email_address
            msg['Subject'] = f"🔒 Approval Required: {action_type}"

            # Email body
            body = f"""
Approval Required for Sensitive Action

Action Type: {action_type}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Action Details:
{json.dumps(action_data, indent=2)}

---
Approval File: {request_path}

To approve:
1. Open the approval file
2. Change "status: pending" to "status: approved"

To reject:
1. Open the approval file
2. Change "status: pending" to "status: rejected"

--
Silver Tier AI Employee - Approval System
"""

            msg.attach(MIMEText(body, 'plain'))

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_address, email_password)
                server.send_message(msg)

            print(f"[EMAIL NOTIFICATION] Sent to {self.notification_email or email_address}")
            return True

        except Exception as e:
            print(f"[EMAIL NOTIFICATION] Failed to send: {type(e).__name__}: {str(e)}")
            return False

    def is_sensitive_action(self, action_data):
        """Determine if an action is sensitive based on its content"""
        sensitive_keywords = [
            'delete', 'remove', 'terminate', 'shutdown', 'payment',
            'financial', 'money', 'salary', 'confidential', 'private',
            'password', 'credentials', 'security', 'admin', 'administrator'
        ]

        action_str = json.dumps(action_data).lower()
        return any(keyword in action_str for keyword in sensitive_keywords)

    def request_approval(self, action_type, action_data, interactive=False):
        """Request approval for a sensitive action
        
        Args:
            action_type: Type of action (e.g., 'email_reply', 'delete_file')
            action_data: Dictionary containing action details
            interactive: If True, ask directly in terminal (for foreground mode)
        
        Returns:
            bool: True if approved, False if rejected
        """
        if not self.is_sensitive_action(action_data):
            return True  # Not sensitive, proceed

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create approval request record
        approval_request = {
            "action_type": action_type,
            "data": action_data,
            "timestamp": timestamp,
            "status": "pending"
        }

        # Save the approval request to a markdown file
        request_filename = f"approval_request_{int(time.time())}.md"
        request_path = self.approvals_dir / request_filename

        with open(request_path, 'w', encoding='utf-8') as f:
            f.write(f"# Sensitive Action Approval Request\n\n")
            f.write(f"**Timestamp:** {timestamp}\n")
            f.write(f"**Action Type:** {action_type}\n\n")
            f.write(f"**Data:**\n```\n{json.dumps(action_data, indent=2)}\n```\n\n")
            f.write(f"**Status:** pending\n\n")
            f.write(f"**Approval File:** `{request_path}`\n\n")
            f.write("---\n")
            f.write("## How to Approve/Reject\n\n")
            f.write("### Option 1: Edit this file\n")
            f.write("Change the status line above from `pending` to `approved` or `rejected`\n\n")
            f.write("### Option 2: Email Notification\n")
            f.write("An email notification has been sent (if configured)\n\n")

        # Send email notification
        self.send_email_notification(action_type, action_data, str(request_path))

        # Print to terminal for notification
        print(f"\n{'='*70}")
        print(f"🔒 APPROVAL REQUIRED - Sensitive Action Detected")
        print(f"{'='*70}")
        print(f"Action Type: {action_type}")
        print(f"Timestamp: {timestamp}")
        print(f"\nDetails:")
        for key, value in action_data.items():
            print(f"  • {key}: {value}")
        print(f"\nApproval File: {request_path}")
        print(f"{'='*70}\n")

        # INTERACTIVE MODE: Ask directly in terminal
        if interactive:
            print("Choose an option:")
            print("  [A] Approve - Send the reply now")
            print("  [R] Reject - Cancel the reply")
            print("  [F] File-based - Edit approval file (for background mode)")
            print()
            
            while True:
                choice = input("Your choice (A/R/F): ").strip().lower()
                
                if choice in ['a', 'approve', 'yes', 'y']:
                    # Update file as approved
                    with open(request_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = content.replace("**Status:** pending", f"**Status:** approved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    with open(request_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("✅ Action APPROVED. Proceeding...\n")
                    return True
                    
                elif choice in ['r', 'reject', 'no', 'n']:
                    # Update file as rejected
                    with open(request_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content = content.replace("**Status:** pending", f"**Status:** rejected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    with open(request_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("❌ Action REJECTED. Canceling...\n")
                    return False
                    
                elif choice in ['f', 'file']:
                    print(f"📁 Open this file to approve/reject: {request_path}")
                    print("Waiting for file approval...\n")
                    break  # Fall through to file-based waiting
                    
                else:
                    print("Invalid choice. Please enter A, R, or F.\n")

        # FILE-BASED MODE: Wait for approval by monitoring the file
        return self.wait_for_approval(request_path)

    def wait_for_approval(self, request_path):
        """Wait for approval by monitoring the approval file"""
        print("Waiting for approval...")

        while True:
            try:
                with open(request_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple check for approval status in the file
                if "**Status:** approved" in content:
                    # Update the status in the file to show when it was approved
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    content = content.replace("**Status:** pending", f"**Status:** approved at {timestamp}")

                    with open(request_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print("Action approved. Proceeding...")
                    return True

                elif "**Status:** rejected" in content:
                    # Update the status in the file to show when it was rejected
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    content = content.replace("**Status:** pending", f"**Status:** rejected at {timestamp}")

                    with open(request_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    print("Action rejected. Canceling...")
                    return False

                time.sleep(5)  # Check every 5 seconds

            except FileNotFoundError:
                print("Approval file was removed. Canceling action...")
                return False
            except Exception as e:
                print(f"Error checking approval status: {e}")
                time.sleep(5)


# Global approval manager instance
approval_manager = ApprovalManager()


def check_approval_needed(action_type, action_data, interactive=False):
    """Check if an action needs approval and wait for it if needed
    
    Args:
        action_type: Type of action (e.g., 'email_reply', 'delete_file')
        action_data: Dictionary containing action details
        interactive: If True, ask directly in terminal (for foreground mode)
    
    Returns:
        bool: True if approved or not sensitive, False if rejected
    """
    return approval_manager.request_approval(action_type, action_data, interactive)