"""
SMS/WhatsApp Send Skill - Silver Tier
Send SMS and WhatsApp messages via Twilio.

Supports:
- Send SMS messages
- Send WhatsApp messages
- Human-in-the-loop approval
- Message templates
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


def get_twilio_client() -> Client:
    """
    Initialize and return Twilio client.
    
    Returns:
        Client: Twilio client object, or None if credentials missing
    """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    
    if not account_sid or not auth_token:
        print("[Twilio] Error: TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN not configured")
        return None
    
    if not twilio_phone:
        print("[Twilio] Error: TWILIO_PHONE_NUMBER not configured")
        return None
    
    try:
        client = Client(account_sid, auth_token)
        # Validate credentials by fetching account
        client.api.accounts(account_sid).fetch()
        return client
    except Exception as e:
        print(f"[Twilio] Authentication failed: {e}")
        return None


def send_sms(to_phone: str, message: str, require_approval: bool = True) -> dict:
    """
    Send an SMS message.
    
    Args:
        to_phone: Recipient phone number (e.g., "+1234567890")
        message: Message content
        require_approval: If True, requires human approval (default: True)
    
    Returns:
        dict: {'success': bool, 'message/error': str, 'details': dict}
    """
    
    # Validate inputs
    if not to_phone:
        return {'success': False, 'error': 'Recipient phone number is required'}
    
    if not message:
        return {'success': False, 'error': 'Message content is required'}
    
    if len(message) > 1600:
        return {'success': False, 'error': 'Message too long (max 1600 characters)'}
    
    # Get Twilio credentials
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    if not twilio_phone:
        return {'success': False, 'error': 'TWILIO_PHONE_NUMBER not configured in .env'}
    
    client = get_twilio_client()
    if not client:
        return {'success': False, 'error': 'Failed to initialize Twilio client'}
    
    # Prepare message data for approval
    message_data = {
        'to': to_phone,
        'from': twilio_phone,
        'message_preview': message[:200] + ('...' if len(message) > 200 else ''),
        'message_length': len(message),
        'type': 'SMS'
    }
    
    # HUMAN-IN-THE-LOOP APPROVAL
    if require_approval:
        print("\n" + "=" * 70)
        print("SMS MESSAGE - HUMAN APPROVAL REQUIRED")
        print("=" * 70)
        print(f"\n📱 TO:   {to_phone}")
        print(f"📤 FROM: {twilio_phone}")
        print(f"📝 LENGTH: {len(message)} characters")
        print(f"\n💬 MESSAGE:")
        print("-" * 70)
        print(message)
        print("-" * 70)
        print(f"\nThis SMS will be sent via Twilio from: {twilio_phone}")
        print("\nApprove sending this SMS?")
        
        while True:
            response = input("Type 'yes' to approve, 'no' to cancel: ").strip().lower()
            if response in ['yes', 'y']:
                print("SMS sending APPROVED\n")
                break
            elif response in ['no', 'n']:
                print("SMS sending CANCELLED by user\n")
                return {
                    'success': False,
                    'error': 'User cancelled SMS sending',
                    'details': message_data
                }
            else:
                print("Invalid response. Please type 'yes' or 'no'.")
    
    # Send SMS via Twilio
    try:
        print(f"[Twilio] Sending SMS to {to_phone}...")
        
        message_result = client.messages.create(
            body=message,
            from_=twilio_phone,
            to=to_phone
        )
        
        print(f"✅ SMS sent successfully! SID: {message_result.sid}")
        
        return {
            'success': True,
            'message': f'SMS sent successfully to {to_phone}',
            'details': {
                'to': to_phone,
                'from': twilio_phone,
                'sid': message_result.sid,
                'status': message_result.status,
                'date_created': str(message_result.date_created),
                'num_segments': message_result.num_segments
            }
        }
        
    except TwilioRestException as e:
        error_msg = f"Twilio API error: {e.status}: {e.msg}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'details': message_data
        }
    except Exception as e:
        error_msg = f"Failed to send SMS: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'details': message_data
        }


def send_whatsapp(to_phone: str, message: str, require_approval: bool = True) -> dict:
    """
    Send a WhatsApp message.
    
    Args:
        to_phone: Recipient phone number with whatsapp prefix (e.g., "whatsapp:+1234567890")
        message: Message content
        require_approval: If True, requires human approval (default: True)
    
    Returns:
        dict: {'success': bool, 'message/error': str, 'details': dict}
    """
    
    # Validate inputs
    if not to_phone:
        return {'success': False, 'error': 'Recipient phone number is required'}
    
    if not message:
        return {'success': False, 'error': 'Message content is required'}
    
    if len(message) > 1600:
        return {'success': False, 'error': 'Message too long (max 1600 characters)'}
    
    # Get Twilio credentials
    twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
    if not twilio_phone:
        return {'success': False, 'error': 'TWILIO_PHONE_NUMBER not configured in .env'}
    
    # Format WhatsApp numbers
    if not to_phone.startswith('whatsapp:'):
        to_phone = f'whatsapp:{to_phone}'
    
    from_whatsapp = f'whatsapp:{twilio_phone}'
    
    client = get_twilio_client()
    if not client:
        return {'success': False, 'error': 'Failed to initialize Twilio client'}
    
    # Prepare message data for approval
    message_data = {
        'to': to_phone,
        'from': from_whatsapp,
        'message_preview': message[:200] + ('...' if len(message) > 200 else ''),
        'message_length': len(message),
        'type': 'WhatsApp'
    }
    
    # HUMAN-IN-THE-LOOP APPROVAL
    if require_approval:
        print("\n" + "=" * 70)
        print("WHATSAPP MESSAGE - HUMAN APPROVAL REQUIRED")
        print("=" * 70)
        print(f"\n📱 TO:   {to_phone.replace('whatsapp:', '')}")
        print(f"📤 FROM: {from_whatsapp.replace('whatsapp:', '')}")
        print(f"📝 LENGTH: {len(message)} characters")
        print(f"\n💬 MESSAGE:")
        print("-" * 70)
        print(message)
        print("-" * 70)
        print(f"\nThis WhatsApp message will be sent via Twilio from: {from_whatsapp}")
        print("\nApprove sending this WhatsApp message?")
        
        while True:
            response = input("Type 'yes' to approve, 'no' to cancel: ").strip().lower()
            if response in ['yes', 'y']:
                print("WhatsApp sending APPROVED\n")
                break
            elif response in ['no', 'n']:
                print("WhatsApp sending CANCELLED by user\n")
                return {
                    'success': False,
                    'error': 'User cancelled WhatsApp sending',
                    'details': message_data
                }
            else:
                print("Invalid response. Please type 'yes' or 'no'.")
    
    # Send WhatsApp via Twilio
    try:
        print(f"[Twilio] Sending WhatsApp to {to_phone}...")
        
        message_result = client.messages.create(
            body=message,
            from_=from_whatsapp,
            to=to_phone
        )
        
        print(f"✅ WhatsApp sent successfully! SID: {message_result.sid}")
        
        return {
            'success': True,
            'message': f'WhatsApp sent successfully to {to_phone.replace("whatsapp:", "")}',
            'details': {
                'to': to_phone.replace('whatsapp:', ''),
                'from': from_whatsapp.replace('whatsapp:', ''),
                'sid': message_result.sid,
                'status': message_result.status,
                'date_created': str(message_result.date_created),
                'num_segments': message_result.num_segments
            }
        }
        
    except TwilioRestException as e:
        error_msg = f"Twilio API error: {e.status}: {e.msg}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'details': message_data
        }
    except Exception as e:
        error_msg = f"Failed to send WhatsApp: {type(e).__name__}: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            'success': False,
            'error': error_msg,
            'details': message_data
        }


def send_message(
    to_phone: str,
    message: str,
    channel: str = 'sms',
    require_approval: bool = True
) -> dict:
    """
    Send a message via SMS or WhatsApp.
    
    Args:
        to_phone: Recipient phone number
        message: Message content
        channel: 'sms' or 'whatsapp' (default: 'sms')
        require_approval: If True, requires human approval (default: True)
    
    Returns:
        dict: {'success': bool, 'message/error': str, 'details': dict}
    """
    if channel.lower() == 'whatsapp':
        return send_whatsapp(to_phone, message, require_approval)
    else:
        return send_sms(to_phone, message, require_approval)


def send_template(
    to_phone: str,
    template_name: str,
    template_vars: dict = None,
    channel: str = 'sms',
    require_approval: bool = True
) -> dict:
    """
    Send a message using a predefined template.
    
    Args:
        to_phone: Recipient phone number
        template_name: Name of the template to use
        template_vars: Variables to substitute in template
        channel: 'sms' or 'whatsapp' (default: 'sms')
        require_approval: If True, requires human approval (default: True)
    
    Returns:
        dict: {'success': bool, 'message/error': str, 'details': dict}
    """
    
    # Predefined templates
    templates = {
        'appointment_reminder': """Hi {name}, this is a reminder about your appointment on {date} at {time}. Please reply to confirm. Thanks!""",
        
        'meeting_invite': """Hi {name}, you're invited to a meeting on {date} at {time}. Location: {location}. Agenda: {agenda}""",
        
        'follow_up': """Hi {name}, following up on our conversation about {topic}. Let me know if you have any questions!""",
        
        'greeting': """Hi {name}, {greeting}! {message}""",
        
        'status_update': """Project Update: {project_name} - {status}. Next milestone: {milestone}. Questions? Reply here."""
    }
    
    if template_name not in templates:
        return {
            'success': False,
            'error': f'Template "{template_name}" not found. Available: {", ".join(templates.keys())}'
        }
    
    template = templates[template_name]
    template_vars = template_vars or {}
    
    # Substitute variables
    try:
        message = template.format(**template_vars)
    except KeyError as e:
        return {
            'success': False,
            'error': f'Missing template variable: {e}'
        }
    
    return send_message(to_phone, message, channel, require_approval)


# CLI Interface
if __name__ == "__main__":
    print("=" * 70)
    print("SMS/WHATSAPP SEND SKILL - Silver Tier")
    print("=" * 70)
    print("\nUsage examples:")
    print("  python sms_whatsapp_send.py --sms --to +1234567890 --message 'Hello!'")
    print("  python sms_whatsapp_send.py --whatsapp --to +1234567890 --message 'Hi from WhatsApp!'")
    print("  python sms_whatsapp_send.py --template appointment_reminder --to +1234567890 --vars name=John date=2026-03-25 time=10:00")
    print("\n" + "=" * 70)
    
    import argparse
    
    parser = argparse.ArgumentParser(description='SMS/WhatsApp Send Skill')
    parser.add_argument('--sms', action='store_true', help='Send SMS message')
    parser.add_argument('--whatsapp', action='store_true', help='Send WhatsApp message')
    parser.add_argument('--to', type=str, help='Recipient phone number')
    parser.add_argument('--message', type=str, help='Message content')
    parser.add_argument('--template', type=str, help='Template name to use')
    parser.add_argument('--vars', type=str, nargs='*', help='Template variables (key=value)')
    parser.add_argument('--no-approval', action='store_true', help='Skip approval prompt')
    
    args = parser.parse_args()
    
    if not args.sms and not args.whatsapp:
        print("Error: Specify --sms or --whatsapp")
        parser.print_help()
        sys.exit(1)
    
    if not args.to:
        print("Error: --to is required")
        sys.exit(1)
    
    channel = 'whatsapp' if args.whatsapp else 'sms'
    
    if args.template:
        # Parse template variables
        template_vars = {}
        if args.vars:
            for var in args.vars:
                if '=' in var:
                    key, value = var.split('=', 1)
                    template_vars[key] = value
        
        result = send_template(
            to_phone=args.to,
            template_name=args.template,
            template_vars=template_vars,
            channel=channel,
            require_approval=not args.no_approval
        )
    else:
        if not args.message:
            print("Error: --message is required (or use --template)")
            sys.exit(1)
        
        result = send_message(
            to_phone=args.to,
            message=args.message,
            channel=channel,
            require_approval=not args.no_approval
        )
    
    if result['success']:
        print(f"\n✅ {result['message']}")
    else:
        print(f"\n❌ {result.get('error', 'Unknown error')}")
