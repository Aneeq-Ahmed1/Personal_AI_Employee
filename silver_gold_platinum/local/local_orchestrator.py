"""
Platinum Tier - Local Orchestrator
Runs on Local Machine - Final actions with approval
Handles approvals, executes final send/post, manages WhatsApp/Banking
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
        logging.FileHandler('local_orchestrator.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('LocalOrchestrator')


class LocalOrchestrator:
    """
    Local Agent Orchestrator - Runs on Local Machine
    Responsibilities:
    - Review pending approvals from Cloud
    - Execute final actions (send emails, post to social)
    - Manage WhatsApp sessions
    - Handle banking/payments
    - Merge cloud updates into Dashboard.md
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.running = False
        self.poll_interval = 15  # Check more frequently on local
        self.auto_approve_low_risk = True  # Auto-approve low-risk actions
        
        # Create vault structure
        self.vault_dirs = {
            'in_progress_local': vault_path / 'In_Progress' / 'local',
            'pending_approval': vault_path / 'Pending_Approval',
            'plans': vault_path / 'Plans',
            'updates': vault_path / 'Updates',
            'done': vault_path / 'Done',
            'dashboard': vault_path
        }
        
        for dir_path in self.vault_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Local Orchestrator initialized. Vault: {vault_path}")
    
    def start(self):
        """Start the local orchestrator loop"""
        self.running = True
        logger.info("🚀 Local Orchestrator STARTED (Final Actions Mode)")
        
        try:
            while self.running:
                try:
                    self.run_cycle()
                    time.sleep(self.poll_interval)
                except Exception as e:
                    logger.error(f"Error in orchestrator cycle: {e}")
                    time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Local Orchestrator stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the local orchestrator"""
        self.running = False
        logger.info("🛑 Local Orchestrator STOPPED")
    
    def run_cycle(self):
        """Run one complete cycle of all local tasks"""
        logger.info("=" * 60)
        logger.info(f"🔄 Local Orchestrator Cycle - {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        # Step 1: Check Pending Approvals
        self.process_pending_approvals()
        
        # Step 2: Execute approved actions
        self.execute_approved_actions()
        
        # Step 3: Process WhatsApp messages
        self.process_whatsapp()
        
        # Step 4: Process Banking/Payments
        self.process_banking()
        
        # Step 5: Merge cloud updates into Dashboard.md
        self.update_dashboard()
        
        logger.info("✅ Local Orchestrator Cycle Complete")
    
    def process_pending_approvals(self):
        """
        Review pending approvals from Cloud agent
        Auto-approve low-risk, flag high-risk for manual review
        """
        logger.info("📋 Processing Pending Approvals...")
        
        approval_path = self.vault_dirs['pending_approval']
        
        if not approval_path.exists():
            return
        
        # Get all pending approval files
        approval_files = list(approval_path.glob('*.json'))
        
        for approval_file in approval_files:
            try:
                with open(approval_file, 'r') as f:
                    approval_data = json.load(f)
                
                approval_type = approval_data.get('type', '')
                
                # Auto-approve low-risk actions
                if self.should_auto_approve(approval_data):
                    logger.info(f"✅ Auto-approved: {approval_type}")
                    approval_data['status'] = 'approved'
                    approval_data['approved_at'] = datetime.now().isoformat()
                    approval_data['approved_by'] = 'local_auto'
                    
                    # Update file
                    with open(approval_file, 'w') as f:
                        json.dump(approval_data, f, indent=2)
                else:
                    logger.info(f"⚠️  Requires manual approval: {approval_type}")
                    approval_data['status'] = 'requires_manual_review'
                    
                    # Update file
                    with open(approval_file, 'w') as f:
                        json.dump(approval_data, f, indent=2)
            
            except Exception as e:
                logger.error(f"Error processing approval {approval_file.name}: {e}")
    
    def should_auto_approve(self, approval_data: Dict) -> bool:
        """Determine if action should be auto-approved"""
        if not self.auto_approve_low_risk:
            return False
        
        approval_type = approval_data.get('type', '')
        
        # Auto-approve email drafts (low risk)
        if approval_type == 'email_draft':
            return True
        
        # Auto-approve routine social posts
        if approval_type == 'social_post_draft':
            # Check if it's a scheduled routine post
            return True
        
        # CEO Briefings are informational
        if approval_type == 'ceo_briefing':
            return True
        
        # Don't auto-approve banking/payment actions
        if 'payment' in approval_type or 'bank' in approval_type:
            return False
        
        return False
    
    def execute_approved_actions(self):
        """Execute actions that have been approved"""
        logger.info("🎯 Executing Approved Actions...")
        
        approval_path = self.vault_dirs['pending_approval']
        
        if not approval_path.exists():
            return
        
        approval_files = list(approval_path.glob('*.json'))
        
        for approval_file in approval_files:
            try:
                with open(approval_file, 'r') as f:
                    approval_data = json.load(f)
                
                if approval_data.get('status') != 'approved':
                    continue
                
                # Check if already executed
                if approval_data.get('executed', False):
                    continue
                
                approval_type = approval_data.get('type', '')
                
                logger.info(f"🚀 Executing: {approval_type}")
                
                # Execute based on type
                if approval_type == 'email_draft':
                    self.send_email_draft(approval_data)
                
                elif approval_type == 'social_post_draft':
                    self.post_to_social_media(approval_data)
                
                elif approval_type == 'ceo_briefing':
                    self.mark_briefing_read(approval_data)
                
                # Mark as executed
                approval_data['executed'] = True
                approval_data['executed_at'] = datetime.now().isoformat()
                approval_data['status'] = 'completed'
                
                # Move to Done
                done_path = self.vault_dirs['done'] / approval_file.name
                approval_file.rename(done_path)
                
                # Update done file
                with open(done_path, 'w') as f:
                    json.dump(approval_data, f, indent=2)
                
                logger.info(f"✅ Executed and moved to Done: {approval_file.name}")
            
            except Exception as e:
                logger.error(f"Error executing approval {approval_file.name}: {e}")
                # Mark as failed
                try:
                    with open(approval_file, 'r') as f:
                        data = json.load(f)
                    data['status'] = 'failed'
                    data['error'] = str(e)
                    with open(approval_file, 'w') as f:
                        json.dump(data, f, indent=2)
                except:
                    pass
    
    def send_email_draft(self, approval_data: Dict):
        """Send an approved email draft"""
        try:
            draft = approval_data.get('draft_reply', {})
            
            # Import email sender
            from silver.skills.email_send import EmailSender
            
            sender = EmailSender()
            
            result = sender.send_email(
                to=draft.get('to', ''),
                subject=draft.get('subject', ''),
                body=draft.get('body', '')
            )
            
            if result.get('success'):
                logger.info("✅ Email sent successfully")
            else:
                logger.error(f"❌ Failed to send email: {result.get('error')}")
        
        except ImportError:
            logger.warning("EmailSender not available, skipping")
        except Exception as e:
            logger.error(f"Error sending email draft: {e}")
    
    def post_to_social_media(self, approval_data: Dict):
        """Post approved social media content"""
        try:
            platform = approval_data.get('platform', 'facebook')
            content = approval_data.get('content', '')
            
            # Import browser automation
            from silver.skills.browser_automation.browser_poster import BrowserSocialPoster
            
            poster = BrowserSocialPoster(headless=False)
            
            if platform == 'facebook':
                result = poster.post_to_facebook(content)
            elif platform == 'instagram':
                result = poster.post_to_instagram(content)
            elif platform == 'twitter':
                result = poster.post_to_twitter(content)
            elif platform == 'linkedin':
                result = poster.post_to_linkedin(content)
            else:
                logger.warning(f"Unknown platform: {platform}")
                return
            
            if result.get('success'):
                logger.info(f"✅ Posted to {platform} successfully")
            else:
                logger.error(f"❌ Failed to post to {platform}: {result.get('error')}")
        
        except ImportError:
            logger.warning("BrowserSocialPoster not available, skipping")
        except Exception as e:
            logger.error(f"Error posting to social media: {e}")
    
    def mark_briefing_read(self, approval_data: Dict):
        """Mark CEO briefing as read"""
        logger.info("📋 CEO Briefing marked as read")
    
    def process_whatsapp(self):
        """Process WhatsApp messages"""
        logger.info("💬 Processing WhatsApp...")
        
        try:
            from silver.whatsapp_handler import WhatsAppHandler
            
            handler = WhatsAppHandler()
            
            # Check for pending WhatsApp messages
            pending_file = self.vault_path / 'Needs_Action' / 'whatsapp_pending.json'
            
            if pending_file.exists():
                with open(pending_file, 'r') as f:
                    pending = json.load(f)
                
                for message in pending.get('messages', []):
                    if message.get('status') == 'approved':
                        handler.send_message(
                            to=message.get('to', ''),
                            message=message.get('message', '')
                        )
                        logger.info(f"✅ WhatsApp sent to: {message.get('to')}")
        
        except ImportError:
            logger.warning("WhatsAppHandler not available, skipping")
        except Exception as e:
            logger.error(f"Error processing WhatsApp: {e}")
    
    def process_banking(self):
        """Process banking/payment actions"""
        logger.info("🏦 Processing Banking...")
        
        # Import Odoo MCP if available
        try:
            from silver.mcp.odoo_mcp_client import OdooMCPClient
            
            client = OdooMCPClient()
            
            # Check for pending banking actions
            banking_pending = self.vault_path / 'Pending_Approval' / 'banking_actions.json'
            
            if banking_pending.exists():
                with open(banking_pending, 'r') as f:
                    actions = json.load(f)
                
                for action in actions.get('actions', []):
                    if action.get('status') == 'approved':
                        # Execute banking action
                        logger.info(f"🏦 Executing banking action: {action.get('type')}")
                        # TODO: Implement specific banking actions
        
        except ImportError:
            logger.debug("OdooMCPClient not available, skipping")
        except Exception as e:
            logger.error(f"Error processing banking: {e}")
    
    def update_dashboard(self):
        """Merge cloud updates into Dashboard.md"""
        try:
            dashboard_file = self.vault_dirs['dashboard'] / 'Dashboard.md'
            
            # Read current dashboard
            if dashboard_file.exists():
                with open(dashboard_file, 'r') as f:
                    content = f.read()
            else:
                content = "# AI Employee Dashboard\n\n"
            
            # Get cloud signals
            cloud_signal = self.vault_path / 'Updates' / 'cloud_status.json'
            
            if cloud_signal.exists():
                with open(cloud_signal, 'r') as f:
                    cloud_status = json.load(f)
                
                # Update dashboard with cloud status
                # TODO: Parse and merge properly
            
            # Check for cloud updates to merge
            updates_path = self.vault_path / 'Updates'
            
            if updates_path.exists():
                update_files = list(updates_path.glob('*.md'))
                
                for update_file in update_files:
                    with open(update_file, 'r') as f:
                        update_content = f.read()
                    
                    content += f"\n\n{update_content}\n"
                    
                    # Move update to done
                    update_file.rename(self.vault_dirs['done'] / update_file.name)
            
            # Write updated dashboard
            with open(dashboard_file, 'w') as f:
                f.write(content)
            
            logger.info("✅ Dashboard updated")
        
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")


def main():
    """Main entry point for Local Orchestrator"""
    import sys
    
    # Get vault path from environment or default
    vault_path = Path(os.environ.get('VAULT_PATH', '../vault'))
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    orchestrator = LocalOrchestrator(vault_path)
    
    logger.info("Starting Local Orchestrator (Final Actions Mode)...")
    logger.info("Press Ctrl+C to stop")
    
    orchestrator.start()


if __name__ == '__main__':
    main()
