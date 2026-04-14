"""
Platinum Tier - Cloud Orchestrator
Runs on Cloud VM (24/7) - Draft-only mode
Monitors emails, social media, creates drafts for Local approval
"""

import os
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Setup logging
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cloud_orchestrator.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('CloudOrchestrator')


class CloudOrchestrator:
    """
    Cloud Agent Orchestrator - Runs 24/7 on Cloud VM
    Responsibilities:
    - Monitor Gmail, LinkedIn, Social Media
    - Create draft replies and posts
    - Write to vault /Needs_Action/ and /Pending_Approval/
    - NEVER execute final actions (send/post)
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.running = False
        self.poll_interval = 30  # seconds
        
        # Create vault structure
        self.vault_dirs = {
            'needs_action': vault_path / 'Needs_Action',
            'in_progress_cloud': vault_path / 'In_Progress' / 'cloud',
            'pending_approval': vault_path / 'Pending_Approval',
            'plans': vault_path / 'Plans',
            'updates': vault_path / 'Updates',
            'signals': vault_path / 'Signals',
            'done': vault_path / 'Done'
        }
        
        for dir_path in self.vault_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cloud Orchestrator initialized. Vault: {vault_path}")
    
    def start(self):
        """Start the cloud orchestrator loop"""
        self.running = True
        logger.info("🚀 Cloud Orchestrator STARTED (Draft-Only Mode)")
        
        try:
            while self.running:
                try:
                    self.run_cycle()
                    time.sleep(self.poll_interval)
                except Exception as e:
                    logger.error(f"Error in orchestrator cycle: {e}")
                    time.sleep(60)  # Wait longer on error
        except KeyboardInterrupt:
            logger.info("Cloud Orchestrator stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the cloud orchestrator"""
        self.running = False
        logger.info("🛑 Cloud Orchestrator STOPPED")
    
    def run_cycle(self):
        """Run one complete cycle of all cloud tasks"""
        logger.info("=" * 60)
        logger.info(f"🔄 Cloud Orchestrator Cycle - {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        # Step 1: Check for new items in Needs_Action
        self.claim_unassigned_tasks()
        
        # Step 2: Process Gmail (draft replies only)
        self.process_gmail_drafts()
        
        # Step 3: Process Social Media (draft posts only)
        self.process_social_drafts()
        
        # Step 4: Generate CEO Briefing if needed
        self.generate_ceo_briefing_if_needed()
        
        # Step 5: Write health signal
        self.write_health_signal()
        
        logger.info("✅ Cloud Orchestrator Cycle Complete")
    
    def claim_unassigned_tasks(self):
        """
        Claim-by-move rule: Move unassigned tasks from Needs_Action to In_Progress/cloud
        First agent to move owns the task
        """
        needs_action_path = self.vault_dirs['needs_action']
        in_progress_path = self.vault_dirs['in_progress_cloud']
        
        if not needs_action_path.exists():
            return
        
        # Get all unassigned task files
        task_files = list(needs_action_path.glob('*.md'))
        
        for task_file in task_files:
            try:
                # Read task metadata
                with open(task_file, 'r') as f:
                    content = f.read()
                
                # Check if already assigned
                if 'assigned_to:' in content:
                    continue
                
                # Claim by moving to In_Progress/cloud
                dest = in_progress_path / task_file.name
                task_file.rename(dest)
                
                # Update task metadata
                with open(dest, 'r') as f:
                    task_content = f.read()
                
                # Add assignment
                if '---' in task_content:
                    lines = task_content.split('\n')
                    new_lines = []
                    inserted = False
                    for line in lines:
                        if line.startswith('---') and not inserted:
                            new_lines.append('assigned_to: cloud')
                            new_lines.append(f'claimed_at: {datetime.now().isoformat()}')
                            inserted = True
                        new_lines.append(line)
                    
                    with open(dest, 'w') as f:
                        f.write('\n'.join(new_lines))
                
                logger.info(f"✅ Claimed task: {task_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to claim task {task_file.name}: {e}")
    
    def process_gmail_drafts(self):
        """
        Process Gmail - Create draft replies only
        Does NOT send emails - Local agent handles final send
        """
        logger.info("📧 Processing Gmail Drafts...")
        
        # Import Gmail watcher if available
        try:
            from silver.gmail_watcher import GmailWatcher
            
            watcher = GmailWatcher()
            
            # Check for new emails
            new_emails = watcher.check_new_emails()
            
            for email in new_emails:
                # Create draft reply
                draft = self.create_draft_reply(email)
                
                # Write to Pending_Approval for Local to review
                self.write_pending_approval(draft)
                
                logger.info(f"📝 Draft reply created for: {email.get('subject', 'Unknown')}")
        
        except ImportError:
            logger.warning("GmailWatcher not available, skipping")
        except Exception as e:
            logger.error(f"Error processing Gmail drafts: {e}")
    
    def create_draft_reply(self, email_data: Dict) -> Dict:
        """Create a draft reply for an email"""
        return {
            'type': 'email_draft',
            'original_email': email_data,
            'draft_reply': {
                'to': email_data.get('from', ''),
                'subject': f"Re: {email_data.get('subject', '')}",
                'body': self.generate_ai_reply(email_data),
                'attachments': []
            },
            'created_at': datetime.now().isoformat(),
            'status': 'pending_approval',
            'assigned_to': 'cloud'
        }
    
    def generate_ai_reply(self, email_data: Dict) -> str:
        """Generate AI-powered reply to email (placeholder)"""
        subject = email_data.get('subject', '')
        
        # TODO: Integrate with AI reasoning engine
        reply = f"""Thank you for your email regarding "{subject}".

This is an AI-generated draft reply. It will be reviewed and sent by the Local agent.

Best regards,
AI Employee"""
        
        return reply
    
    def process_social_draft(self):
        """
        Process Social Media - Create draft posts only
        Does NOT post - Local agent handles final posting
        """
        logger.info("📱 Processing Social Media Drafts...")
        
        # Import social media poster if available
        try:
            from silver.skills.browser_automation.browser_poster import BrowserSocialPoster
            
            # Check for scheduled posts
            scheduled_file = self.vault_path / 'Plans' / 'social_schedule.json'
            
            if scheduled_file.exists():
                with open(scheduled_file, 'r') as f:
                    schedule = json.load(f)
                
                for post in schedule.get('posts', []):
                    if post.get('status') == 'draft':
                        # Create draft post
                        draft = self.create_social_draft(post)
                        self.write_pending_approval(draft)
                        logger.info(f"📝 Draft post created for: {post.get('platform', 'unknown')}")
        
        except ImportError:
            logger.warning("BrowserSocialPoster not available, skipping")
        except Exception as e:
            logger.error(f"Error processing social media drafts: {e}")
    
    def create_social_draft(self, post_data: Dict) -> Dict:
        """Create a draft social media post"""
        return {
            'type': 'social_post_draft',
            'platform': post_data.get('platform', 'facebook'),
            'content': post_data.get('content', ''),
            'image': post_data.get('image', None),
            'scheduled_time': post_data.get('scheduled_time', None),
            'created_at': datetime.now().isoformat(),
            'status': 'pending_approval',
            'assigned_to': 'cloud'
        }
    
    def write_pending_approval(self, draft: Dict):
        """Write draft to Pending_Approval for Local agent"""
        approval_path = self.vault_dirs['pending_approval']
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{draft['type']}_{timestamp}.json"
        
        filepath = approval_path / filename
        
        with open(filepath, 'w') as f:
            json.dump(draft, f, indent=2)
        
        logger.info(f"✅ Written to Pending_Approval: {filename}")
    
    def generate_ceo_briefing_if_needed(self):
        """Generate CEO Briefing if significant events detected"""
        # Check if briefing needed
        pending_path = self.vault_dirs['pending_approval']
        
        pending_count = len(list(pending_path.glob('*.json')))
        
        if pending_count >= 5:  # Generate briefing if 5+ pending items
            briefing = {
                'type': 'ceo_briefing',
                'generated_at': datetime.now().isoformat(),
                'pending_items': pending_count,
                'summary': f"You have {pending_count} items awaiting approval.",
                'status': 'generated'
            }
            
            self.write_pending_approval(briefing)
            logger.info(f"📋 CEO Briefing generated ({pending_count} pending items)")
    
    def write_health_signal(self):
        """Write health signal to indicate cloud agent is alive"""
        signal_file = self.vault_dirs['signals'] / 'cloud_health.json'
        
        health_data = {
            'agent': 'cloud',
            'status': 'alive',
            'timestamp': datetime.now().isoformat(),
            'pending_items': len(list(self.vault_dirs['pending_approval'].glob('*.json'))),
            'in_progress_items': len(list(self.vault_dirs['in_progress_cloud'].glob('*.md')))
        }
        
        with open(signal_file, 'w') as f:
            json.dump(health_data, f, indent=2)


def main():
    """Main entry point for Cloud Orchestrator"""
    import sys
    
    # Get vault path from environment or default
    vault_path = Path(os.environ.get('VAULT_PATH', '../vault'))
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    orchestrator = CloudOrchestrator(vault_path)
    
    logger.info("Starting Cloud Orchestrator (Draft-Only Mode)...")
    logger.info("Press Ctrl+C to stop")
    
    orchestrator.start()


if __name__ == '__main__':
    main()
