# Email Send Skill

## Purpose
This skill sends emails to recipients on behalf of the user.

## Functionality
- Accepts recipient, subject, and body
- Validates required fields
- Sends email via SMTP
- Returns success/failure status

## Input
- recipient: Email address of the recipient (required)
- subject: Subject of the email (optional, defaults to "No Subject")
- body: Body content of the email (optional, defaults to empty)

## Output
- Success message with recipient and subject on success
- Error message on failure