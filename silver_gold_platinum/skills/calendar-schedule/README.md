# Calendar Schedule Skill

Silver Tier skill for Google Calendar integration.

## Features

- ✅ Create calendar events
- ✅ Check calendar availability
- ✅ Find next available time slot
- ✅ Quick schedule (auto-find available slot)
- ✅ Human-in-the-loop approval
- ✅ Conflict detection

## Setup

### 1. Install Dependencies

```bash
cd silver/skills/calendar-schedule
pip install -r requirements.txt
```

### 2. Configure Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Google Calendar API**
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Choose **Desktop app** as application type
6. Download the credentials JSON file
7. Save as `credentials.json` in this directory

### 3. First-Time Authentication

Run the skill once to authenticate:

```bash
python calendar_schedule.py --quick --summary "Test Event" --no-approval
```

Follow the authorization URL and paste the redirect response.

## Usage

### Create Event at Specific Time

```bash
python calendar_schedule.py --create \
  --summary "Team Meeting" \
  --start "2026-03-25T10:00:00" \
  --end "2026-03-25T11:00:00" \
  --description "Weekly team sync" \
  --attendees "team@example.com" "manager@example.com"
```

### Quick Schedule (Find Next Available Slot)

```bash
python calendar_schedule.py --quick \
  --summary "Client Call" \
  --duration 30 \
  --description "Discussion about project requirements"
```

### Check Availability

```bash
python calendar_schedule.py --check \
  --start "2026-03-25T10:00:00" \
  --end "2026-03-25T11:00:00"
```

### Skip Approval (for automation)

```bash
python calendar_schedule.py --create \
  --summary "Auto Meeting" \
  --start "2026-03-25T14:00:00" \
  --end "2026-03-25T14:30:00" \
  --no-approval
```

## Python API

```python
from calendar_schedule import schedule_event, quick_schedule

# Schedule at specific time
result = schedule_event(
    summary="Team Meeting",
    start_time="2026-03-25T10:00:00",
    end_time="2026-03-25T11:00:00",
    description="Weekly sync",
    attendees=["team@example.com"],
    require_approval=True
)

# Quick schedule (finds next available slot)
result = quick_schedule(
    summary="Client Call",
    duration_minutes=30,
    attendees=["client@example.com"],
    require_approval=True
)
```

## Environment Variables (Optional)

Add to project root `.env`:

```env
# Google Calendar (optional - credentials file preferred)
GOOGLE_CALENDAR_ID=primary
```

## Response Format

```json
{
  "success": true,
  "message": "Event 'Team Meeting' created successfully",
  "details": {
    "event_id": "abc123xyz",
    "html_link": "https://calendar.google.com/...",
    "summary": "Team Meeting",
    "start": "2026-03-25T10:00:00",
    "end": "2026-03-25T11:00:00"
  }
}
```

## Troubleshooting

### "Credentials file not found"
- Download `credentials.json` from Google Cloud Console
- Save in this directory

### "Token expired"
- Delete `token.pickle` file
- Re-run authentication

### "API not enabled"
- Enable Google Calendar API in Google Cloud Console
