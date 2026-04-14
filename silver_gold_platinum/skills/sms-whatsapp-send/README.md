# SMS/WhatsApp Send Skill

Silver Tier skill for sending SMS and WhatsApp messages via Twilio.

## Features

- ✅ Send SMS messages
- ✅ Send WhatsApp messages
- ✅ Message templates (appointment reminders, meeting invites, etc.)
- ✅ Human-in-the-loop approval
- ✅ CLI and Python API

## Setup

### 1. Install Dependencies

```bash
cd silver/skills/sms-whatsapp-send
pip install -r requirements.txt
```

### 2. Configure Twilio

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your credentials from [Console](https://console.twilio.com/)
3. Add to project root `.env`:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

### 3. WhatsApp Setup (Optional)

For WhatsApp messaging:

1. Enable WhatsApp in Twilio Console
2. Use the sandbox number or configure your own WhatsApp-enabled number
3. Recipients must join your sandbox first (Twilio will provide instructions)

## Usage

### Send SMS

```bash
python sms_whatsapp_send.py --sms \
  --to +1234567890 \
  --message "Hello! This is a test SMS."
```

### Send WhatsApp

```bash
python sms_whatsapp_send.py --whatsapp \
  --to +1234567890 \
  --message "Hi from WhatsApp!"
```

### Use Template

```bash
# Appointment reminder
python sms_whatsapp_send.py --template appointment_reminder \
  --to +1234567890 \
  --vars name=John date=2026-03-25 time=10:00

# Meeting invite
python sms_whatsapp_send.py --template meeting_invite \
  --to +1234567890 \
  --vars name=Sarah date=2026-03-26 time=14:00 location="Conference Room A" agenda="Q2 Planning"
```

### Skip Approval (for automation)

```bash
python sms_whatsapp_send.py --sms \
  --to +1234567890 \
  --message "Automated alert" \
  --no-approval
```

## Python API

```python
from sms_whatsapp_send import send_sms, send_whatsapp, send_template

# Send SMS
result = send_sms(
    to_phone="+1234567890",
    message="Hello from AI Employee!",
    require_approval=True
)

# Send WhatsApp
result = send_whatsapp(
    to_phone="+1234567890",
    message="Hi via WhatsApp!",
    require_approval=True
)

# Use template
result = send_template(
    to_phone="+1234567890",
    template_name="appointment_reminder",
    template_vars={
        'name': 'John',
        'date': '2026-03-25',
        'time': '10:00'
    },
    channel='sms',
    require_approval=True
)
```

## Available Templates

### appointment_reminder
Variables: `name`, `date`, `time`

### meeting_invite
Variables: `name`, `date`, `time`, `location`, `agenda`

### follow_up
Variables: `name`, `topic`

### greeting
Variables: `name`, `greeting`, `message`

### status_update
Variables: `project_name`, `status`, `milestone`

## Response Format

```json
{
  "success": true,
  "message": "SMS sent successfully to +1234567890",
  "details": {
    "to": "+1234567890",
    "from": "+0987654321",
    "sid": "SMxxxxxxxxxxxxxxxxxxxxxxxx",
    "status": "queued",
    "date_created": "2026-03-24 10:30:00",
    "num_segments": 1
  }
}
```

## Troubleshooting

### "Credentials not configured"
- Add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER to `.env`

### "Invalid phone number"
- Use E.164 format: +1234567890 (include country code)

### "WhatsApp sandbox"
- Recipients must text the sandbox code to activate WhatsApp messaging

### "Message too long"
- SMS max: 1600 characters (will be split into segments)
