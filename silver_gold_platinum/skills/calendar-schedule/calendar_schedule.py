"""
Calendar Schedule Skill - Silver Tier
Integrates with Google Calendar to schedule events and meetings.

Supports:
- Create calendar events
- Check calendar availability
- Human-in-the-loop approval for event creation
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = PROJECT_ROOT / "silver" / "skills" / "calendar-schedule" / "credentials.json"
TOKEN_FILE = PROJECT_ROOT / "silver" / "skills" / "calendar-schedule" / "token.pickle"


def authenticate_calendar():
    """
    Authenticate with Google Calendar API.
    
    Returns:
        googleapiclient.discovery.Resource: Calendar API service object, or None if auth fails
    """
    creds = None
    
    # Load existing token
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"[Calendar] Token refresh failed: {e}")
                creds = None
        
        if not creds:
            if not CREDENTIALS_FILE.exists():
                print(f"[Calendar] Credentials file not found: {CREDENTIALS_FILE}")
                print("[Calendar] Please download credentials.json from Google Cloud Console")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0, open_browser=False)
                print("[Calendar] Please open the following URL in your browser:")
                print(flow.authorization_url()[0])
                print("\nAfter authorization, paste the redirect URL here:")
                auth_response = input("Authorization response URL: ").strip()
                
                # Parse the authorization code from the response
                if 'code=' in auth_response:
                    code = auth_response.split('code=')[1].split('&')[0]
                    flow.fetch_token(code=code)
                    creds = flow.credentials
                else:
                    print("[Calendar] Invalid authorization response")
                    return None
                    
            except Exception as e:
                print(f"[Calendar] Authentication error: {e}")
                return None
            
            # Save credentials for future use
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            print("[Calendar] Credentials saved successfully")
    
    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"[Calendar] Failed to build service: {e}")
        return None


def check_availability(service, start_time: str, end_time: str, calendar_id: str = 'primary') -> dict:
    """
    Check if a time slot is available on the calendar.
    
    Args:
        service: Calendar API service object
        start_time: Start time in ISO format (e.g., "2026-03-25T10:00:00")
        end_time: End time in ISO format
        calendar_id: Calendar ID (default: 'primary')
    
    Returns:
        dict: {'available': bool, 'conflicts': list}
    """
    try:
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_time + 'Z',
            timeMax=end_time + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {'available': True, 'conflicts': []}
        else:
            conflicts = []
            for event in events:
                conflicts.append({
                    'summary': event.get('summary', 'No Title'),
                    'start': event.get('start', {}).get('dateTime', event.get('start', {}).get('date')),
                    'end': event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
                })
            return {'available': False, 'conflicts': conflicts}
            
    except HttpError as error:
        print(f"[Calendar] Error checking availability: {error}")
        return {'available': False, 'error': str(error)}


def create_event(
    service,
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    attendees: list = None,
    location: str = "",
    calendar_id: str = 'primary'
) -> dict:
    """
    Create a calendar event.
    
    Args:
        service: Calendar API service object
        summary: Event title/summary
        start_time: Start time in ISO format
        end_time: End time in ISO format
        description: Event description
        attendees: List of attendee email addresses
        location: Event location
        calendar_id: Calendar ID (default: 'primary')
    
    Returns:
        dict: {'success': bool, 'event_id': str, 'html_link': str, 'error': str}
    """
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time + 'Z',
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time + 'Z',
            'timeZone': 'UTC',
        },
    }
    
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]
    
    try:
        event_result = service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates='all' if attendees else 'none'
        ).execute()
        
        return {
            'success': True,
            'event_id': event_result['id'],
            'html_link': event_result.get('htmlLink', ''),
            'summary': summary,
            'start': start_time,
            'end': end_time
        }
        
    except HttpError as error:
        print(f"[Calendar] Error creating event: {error}")
        return {
            'success': False,
            'error': str(error)
        }


def schedule_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str = "",
    attendees: list = None,
    location: str = "",
    require_approval: bool = True
) -> dict:
    """
    Schedule a calendar event with optional human approval.
    
    Args:
        summary: Event title/summary
        start_time: Start time in ISO format (e.g., "2026-03-25T10:00:00")
        end_time: End time in ISO format
        description: Event description
        attendees: List of attendee email addresses
        location: Event location
        require_approval: If True, requires human approval before creating (default: True)
    
    Returns:
        dict: {'success': bool, 'message/error': str, 'details': dict}
    """
    
    # Validate required fields
    if not summary:
        return {
            'success': False,
            'error': 'Event summary/title is required'
        }
    
    if not start_time or not end_time:
        return {
            'success': False,
            'error': 'Start time and end time are required'
        }
    
    # Authenticate with Google Calendar
    service = authenticate_calendar()
    if not service:
        return {
            'success': False,
            'error': 'Failed to authenticate with Google Calendar. Please check credentials.'
        }
    
    # Check for conflicts
    availability = check_availability(service, start_time, end_time)
    
    # Prepare event data for approval
    event_data = {
        'summary': summary,
        'start': start_time,
        'end': end_time,
        'description': description[:200] + ('...' if len(description) > 200 else ''),
        'attendees': attendees or [],
        'location': location,
        'has_conflicts': not availability.get('available', True),
        'conflicts': availability.get('conflicts', [])
    }
    
    # HUMAN-IN-THE-LOOP APPROVAL
    if require_approval:
        print("\n" + "=" * 70)
        print("CALENDAR EVENT - HUMAN APPROVAL REQUIRED")
        print("=" * 70)
        print(f"\n📅 EVENT: {summary}")
        print(f"⏰ TIME: {start_time} to {end_time}")
        
        if location:
            print(f"📍 LOCATION: {location}")
        
        if attendees:
            print(f"👥 ATTENDEES: {', '.join(attendees)}")
        
        if description:
            print(f"\n📝 DESCRIPTION:")
            print("-" * 70)
            print(description[:500] + ('...\n[Description truncated]' if len(description) > 500 else ''))
            print("-" * 70)
        
        if event_data['has_conflicts']:
            print("\n⚠️  WARNING: Scheduling conflicts detected!")
            for conflict in event_data['conflicts']:
                print(f"   - {conflict['summary']} ({conflict['start']} to {conflict['end']})")
        
        print("\nApprove creating this calendar event?")
        
        while True:
            response = input("Type 'yes' to approve, 'no' to cancel: ").strip().lower()
            if response in ['yes', 'y']:
                print("Event creation APPROVED\n")
                break
            elif response in ['no', 'n']:
                print("Event creation CANCELLED by user\n")
                return {
                    'success': False,
                    'error': 'User cancelled event creation',
                    'details': event_data
                }
            else:
                print("Invalid response. Please type 'yes' or 'no'.")
    
    # Create the event
    result = create_event(
        service=service,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        attendees=attendees,
        location=location
    )
    
    if result['success']:
        print(f"✅ Event created successfully!")
        print(f"🔗 Calendar Link: {result['html_link']}")
        return {
            'success': True,
            'message': f"Event '{summary}' created successfully",
            'details': result
        }
    else:
        print(f"❌ Failed to create event: {result.get('error', 'Unknown error')}")
        return {
            'success': False,
            'error': result.get('error', 'Failed to create event'),
            'details': event_data
        }


def find_available_slot(
    service,
    duration_minutes: int,
    date: str = None,
    start_hour: int = 9,
    end_hour: int = 17,
    calendar_id: str = 'primary'
) -> dict:
    """
    Find the next available time slot on the calendar.
    
    Args:
        service: Calendar API service object
        duration_minutes: Duration of the meeting in minutes
        date: Date to search (YYYY-MM-DD format, default: today)
        start_hour: Start of working hours (default: 9)
        end_hour: End of working hours (default: 17)
        calendar_id: Calendar ID (default: 'primary')
    
    Returns:
        dict: {'available': bool, 'start': str, 'end': str} or error
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Try to find a slot today
    current_date = datetime.strptime(date, '%Y-%m-%d')
    
    for day_offset in range(7):  # Try next 7 days
        check_date = current_date + timedelta(days=day_offset)
        date_str = check_date.strftime('%Y-%m-%d')
        
        # Try each hour slot
        for hour in range(start_hour, end_hour):
            slot_start = f"{date_str}T{hour:02d}:00:00"
            slot_end = f"{date_str}T{hour:02d}:{duration_minutes:02d}:00"
            
            # Make sure end time doesn't exceed working hours
            if hour + (duration_minutes / 60) > end_hour:
                continue
            
            availability = check_availability(service, slot_start, slot_end, calendar_id)
            
            if availability.get('available', False):
                return {
                    'available': True,
                    'start': slot_start,
                    'end': slot_end,
                    'date': date_str
                }
    
    return {
        'available': False,
        'error': 'No available slots found in the next 7 days'
    }


def quick_schedule(
    summary: str,
    duration_minutes: int = 30,
    attendees: list = None,
    description: str = "",
    require_approval: bool = True
) -> dict:
    """
    Quick schedule - finds the next available slot and creates an event.
    
    Args:
        summary: Event title/summary
        duration_minutes: Duration in minutes (default: 30)
        attendees: List of attendee email addresses
        description: Event description
        require_approval: If True, requires human approval (default: True)
    
    Returns:
        dict: {'success': bool, 'message/error': str, 'details': dict}
    """
    service = authenticate_calendar()
    if not service:
        return {
            'success': False,
            'error': 'Failed to authenticate with Google Calendar'
        }
    
    # Find available slot
    slot = find_available_slot(service, duration_minutes)
    
    if not slot.get('available', False):
        return {
            'success': False,
            'error': slot.get('error', 'No available slots found')
        }
    
    print(f"\n[Calendar] Found available slot: {slot['start']} to {slot['end']}")
    
    # Schedule the event
    return schedule_event(
        summary=summary,
        start_time=slot['start'],
        end_time=slot['end'],
        description=description,
        attendees=attendees,
        require_approval=require_approval
    )


# CLI Interface
if __name__ == "__main__":
    print("=" * 70)
    print("CALENDAR SCHEDULE SKILL - Silver Tier")
    print("=" * 70)
    print("\nUsage examples:")
    print("  python calendar_schedule.py --create --summary 'Team Meeting' --start '2026-03-25T10:00:00' --end '2026-03-25T11:00:00'")
    print("  python calendar_schedule.py --quick --summary 'Client Call' --duration 30")
    print("  python calendar_schedule.py --check --start '2026-03-25T10:00:00' --end '2026-03-25T11:00:00'")
    print("\n" + "=" * 70)
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Calendar Schedule Skill')
    parser.add_argument('--create', action='store_true', help='Create a calendar event')
    parser.add_argument('--quick', action='store_true', help='Quick schedule (find next available slot)')
    parser.add_argument('--check', action='store_true', help='Check availability for a time slot')
    parser.add_argument('--summary', type=str, help='Event summary/title')
    parser.add_argument('--start', type=str, help='Start time (ISO format: YYYY-MM-DDTHH:MM:SS)')
    parser.add_argument('--end', type=str, help='End time (ISO format)')
    parser.add_argument('--duration', type=int, default=30, help='Duration in minutes (for quick schedule)')
    parser.add_argument('--description', type=str, default='', help='Event description')
    parser.add_argument('--attendees', type=str, nargs='*', help='Attendee email addresses')
    parser.add_argument('--location', type=str, default='', help='Event location')
    parser.add_argument('--no-approval', action='store_true', help='Skip approval prompt')
    
    args = parser.parse_args()
    
    if args.create:
        if not args.summary or not args.start or not args.end:
            print("Error: --summary, --start, and --end are required for --create")
            sys.exit(1)
        
        result = schedule_event(
            summary=args.summary,
            start_time=args.start,
            end_time=args.end,
            description=args.description,
            attendees=args.attendees,
            location=args.location,
            require_approval=not args.no_approval
        )
        
        if result['success']:
            print(f"\n✅ {result['message']}")
        else:
            print(f"\n❌ {result.get('error', 'Unknown error')}")
    
    elif args.quick:
        if not args.summary:
            print("Error: --summary is required for --quick")
            sys.exit(1)
        
        result = quick_schedule(
            summary=args.summary,
            duration_minutes=args.duration,
            attendees=args.attendees,
            description=args.description,
            require_approval=not args.no_approval
        )
        
        if result['success']:
            print(f"\n✅ {result['message']}")
        else:
            print(f"\n❌ {result.get('error', 'Unknown error')}")
    
    elif args.check:
        if not args.start or not args.end:
            print("Error: --start and --end are required for --check")
            sys.exit(1)
        
        service = authenticate_calendar()
        if service:
            result = check_availability(service, args.start, args.end)
            if result.get('available', False):
                print(f"\n✅ Time slot is AVAILABLE")
            else:
                print(f"\n❌ Time slot has CONFLICTS:")
                for conflict in result.get('conflicts', []):
                    print(f"   - {conflict['summary']} ({conflict['start']} to {conflict['end']})")
    
    else:
        parser.print_help()
