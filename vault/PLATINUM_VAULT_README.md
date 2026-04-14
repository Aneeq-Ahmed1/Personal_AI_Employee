# Platinum Tier Vault Structure

## Directory Layout

### `/Needs_Action/`
Unassigned tasks waiting to be claimed by agents
- `/email/` - New emails requiring attention
- `/social/` - Social media tasks
- `/whatsapp/` - WhatsApp messages

### `/In_Progress/`
Tasks currently being worked on
- `/cloud/` - Tasks owned by Cloud agent
- `/local/` - Tasks owned by Local agent

### `/Pending_Approval/`
Draft actions awaiting human approval
- Email drafts
- Social media post drafts
- WhatsApp messages
- Payment actions

### `/Updates/`
Agent updates and audit logs
- `/approved/` - Actions that were approved
- `/rejected/` - Actions that were rejected
- `/audit_log/` - Execution audit trail

### `/Signals/`
Health and status signals from agents
- Cloud health signals
- Local health signals

### `/Done/`
Completed and executed tasks

## Claim-by-Move Rule

1. Tasks start in `/Needs_Action/<domain>/`
2. First agent to move to `/In_Progress/<agent>/` claims ownership
3. Single-writer rule prevents conflicts
4. All moves are logged in `/Updates/audit_log/`

## Security Rules

- Cloud agent: Draft-only mode
- Local agent: Final execution
- Secrets never sync to cloud
- Dashboard.md owned by Local only
