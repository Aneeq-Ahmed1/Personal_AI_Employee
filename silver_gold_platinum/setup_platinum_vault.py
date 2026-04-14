"""
Platinum Tier - Vault Structure Setup
Creates the required vault directory structure for Platinum Tier
"""

from pathlib import Path
import json
from datetime import datetime


def setup_platinum_vault(vault_path: Path):
    """
    Setup vault structure for Platinum Tier
    
    Creates:
    - /Needs_Action/<domain>/ - Unassigned tasks
    - /In_Progress/cloud/ - Cloud agent owned tasks
    - /In_Progress/local/ - Local agent owned tasks
    - /Pending_Approval/ - Awaiting approval
    - /Updates/ - Agent updates
    - /Signals/ - Health/status signals
    - /Done/ - Completed tasks
    """
    
    print("🏗️  Setting up Platinum Tier vault structure...")
    
    # Define vault directories
    vault_dirs = {
        'needs_action': vault_path / 'Needs_Action',
        'needs_action_email': vault_path / 'Needs_Action' / 'email',
        'needs_action_social': vault_path / 'Needs_Action' / 'social',
        'needs_action_whatsapp': vault_path / 'Needs_Action' / 'whatsapp',
        'in_progress': vault_path / 'In_Progress',
        'in_progress_cloud': vault_path / 'In_Progress' / 'cloud',
        'in_progress_local': vault_path / 'In_Progress' / 'local',
        'pending_approval': vault_path / 'Pending_Approval',
        'plans': vault_path / 'Plans',
        'updates': vault_path / 'Updates',
        'updates_approved': vault_path / 'Updates' / 'approved',
        'updates_rejected': vault_path / 'Updates' / 'rejected',
        'updates_audit': vault_path / 'Updates' / 'audit_log',
        'signals': vault_path / 'Signals',
        'done': vault_path / 'Done'
    }
    
    # Create all directories
    for name, dir_path in vault_dirs.items():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ Created: {dir_path.relative_to(vault_path)}")
    
    # Create security rules file
    security_rules = {
        'version': '1.0.0',
        'created_at': datetime.now().isoformat(),
        'rules': {
            'never_sync_files': [
                '.env',
                'token.pickle',
                'credentials.json',
                'whatsapp_session',
                '*.key',
                '*.pem',
                '*.secret',
                'chrome_cookies.json',
                '*.log'
            ],
            'allowed_sync_extensions': ['.md', '.json', '.txt', '.yaml', '.yml'],
            'cloud_restrictions': {
                'can_draft': True,
                'can_send_emails': False,
                'can_post_social': False,
                'can_send_whatsapp': False,
                'can_execute_payments': False,
                'writes_to': ['/Updates/', '/Signals/']
            },
            'local_permissions': {
                'can_draft': True,
                'can_send_emails': True,
                'can_post_social': True,
                'can_send_whatsapp': True,
                'can_execute_payments': True,
                'owns_dashboard_md': True
            },
            'claim_by_move_rule': {
                'description': 'First agent to move from Needs_Action to In_Progress/<agent>/ owns the task',
                'single_writer': True,
                'audit_required': True
            }
        }
    }
    
    security_file = vault_path / 'security_rules.json'
    with open(security_file, 'w') as f:
        json.dump(security_rules, f, indent=2)
    
    print(f"  ✅ Created: security_rules.json")
    
    # Create README for vault structure
    readme_content = """# Platinum Tier Vault Structure

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
"""
    
    readme_file = vault_path / 'PLATINUM_VAULT_README.md'
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    
    print(f"  ✅ Created: PLATINUM_VAULT_README.md")
    
    # Create a test task for demonstration
    test_task = {
        'type': 'email_draft',
        'original_email': {
            'subject': 'Test Email - Platinum Tier Setup',
            'from': 'test@example.com',
            'date': datetime.now().isoformat()
        },
        'draft_reply': {
            'to': 'test@example.com',
            'subject': 'Re: Test Email - Platinum Tier Setup',
            'body': 'This is a test draft reply from the Platinum Tier system.',
            'attachments': []
        },
        'created_at': datetime.now().isoformat(),
        'created_by': 'platinum_setup_script',
        'status': 'pending_approval',
        'assigned_to': 'cloud',
        'risk_level': 'low'
    }
    
    test_file = vault_path / 'Pending_Approval' / 'test_email_draft.json'
    with open(test_file, 'w') as f:
        json.dump(test_task, f, indent=2)
    
    print(f"  ✅ Created test task: Pending_Approval/test_email_draft.json")
    
    print("\n✅ Platinum Tier vault structure setup complete!")
    print(f"Vault path: {vault_path}")


if __name__ == '__main__':
    import sys
    
    # Get vault path from environment or default
    vault_path = Path(sys.argv[1] if len(sys.argv) > 1 else '../vault')
    
    if not vault_path.exists():
        print(f"❌ Vault path does not exist: {vault_path}")
        print("Creating vault directory...")
        vault_path.mkdir(parents=True, exist_ok=True)
    
    setup_platinum_vault(vault_path)
