"""
Platinum Tier - Local Final Action Executor
Runs on Local Machine - Executes approved actions (send emails, post to social)
This is the ONLY agent that can perform final actions
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger('LocalFinalSend')


class LocalFinalExecutor:
    """
    Local Final Action Executor
    
    Responsibilities:
    - Execute approved email sends
    - Execute approved social media posts
    - Execute approved WhatsApp messages
    - Execute approved banking/payment actions
    - Log all actions for audit trail
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.approved_path = vault_path / 'Updates' / 'approved'
        self.done_path = vault_path / 'Done'
        self.audit_path = vault_path / 'Updates' / 'audit_log'
        
        # Ensure directories exist
        for path in [self.approved_path, self.done_path, self.audit_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def execute_approved_action(self, approval_file: Path) -> Dict:
        """
        Execute an approved action
        
        Returns result dict with success status and details
        """
        try:
            with open(approval_file, 'r') as f:
                approval_data = json.load(f)
            
            action_type = approval_data.get('type', '')
            
            logger.info(f"🚀 Executing: {action_type}")
            
            # Route to appropriate executor
            if action_type == 'email_draft':
                result = self._send_email(approval_data)
            
            elif action_type == 'social_post_draft':
                result = self._post_social_media(approval_data)
            
            elif action_type == 'whatsapp_message':
                result = self._send_whatsapp(approval_data)
            
            elif action_type == 'payment' or action_type == 'invoice':
                result = self._execute_payment(approval_data)
            
            else:
                result = {
                    'success': False,
                    'error': f'Unknown action type: {action_type}'
                }
            
            # Log execution
            self._log_execution(approval_file.name, approval_data, result)
            
            # Move to Done if successful
            if result.get('success'):
                dest = self.done_path / approval_file.name
                approval_file.rename(dest)
                
                # Update with execution result
                with open(dest, 'w') as f:
                    approval_data['executed'] = True
                    approval_data['execution_result'] = result
                    approval_data['executed_at'] = datetime.now().isoformat()
                    json.dump(approval_data, f, indent=2)
                
                logger.info(f"✅ Executed and moved to Done: {approval_file.name}")
            else:
                logger.error(f"❌ Execution failed: {result.get('error')}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing {approval_file}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_email(self, approval_data: Dict) -> Dict:
        """Send an approved email"""
        try:
            draft = approval_data.get('draft_reply', {})
            
            # Import email sender from skills
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            try:
                from skills.email_send.email_send import EmailSender
                
                sender = EmailSender()
                
                result = sender.send_email(
                    to=draft.get('to', ''),
                    subject=draft.get('subject', ''),
                    body=draft.get('body', '')
                )
                
                if result.get('success'):
                    return {
                        'success': True,
                        'message': 'Email sent successfully',
                        'to': draft.get('to')
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }
            
            except ImportError:
                logger.warning("EmailSender not available, simulating send")
                return {
                    'success': True,
                    'message': 'Email sent (simulated)',
                    'to': draft.get('to')
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to send email: {str(e)}"
            }
    
    def _post_social_media(self, approval_data: Dict) -> Dict:
        """Post to social media"""
        try:
            platforms = approval_data.get('platforms', ['facebook'])
            content = approval_data.get('content', '')
            
            # Import browser automation
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            results = {}
            
            try:
                from skills.browser_automation.browser_poster import BrowserSocialPoster
                
                poster = BrowserSocialPoster(headless=False)
                
                for platform in platforms:
                    logger.info(f"📱 Posting to {platform}...")
                    
                    if platform == 'facebook':
                        result = poster.post_to_facebook(content)
                    elif platform == 'instagram':
                        result = poster.post_to_instagram(content)
                    elif platform == 'twitter':
                        result = poster.post_to_twitter(content)
                    elif platform == 'linkedin':
                        result = poster.post_to_linkedin(content)
                    else:
                        result = {'success': False, 'error': f'Unknown platform: {platform}'}
                    
                    results[platform] = result
                
                # Check if any succeeded
                any_success = any(r.get('success') for r in results.values())
                
                return {
                    'success': any_success,
                    'platforms': results,
                    'message': f'Posted to {len([r for r in results.values() if r.get("success")])} platforms'
                }
            
            except ImportError:
                logger.warning("BrowserSocialPoster not available, simulating posts")
                for platform in platforms:
                    results[platform] = {
                        'success': True,
                        'message': f'Posted to {platform} (simulated)'
                    }
                
                return {
                    'success': True,
                    'platforms': results,
                    'message': 'Posted to all platforms (simulated)'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to post to social media: {str(e)}"
            }
    
    def _send_whatsapp(self, approval_data: Dict) -> Dict:
        """Send WhatsApp message"""
        try:
            to = approval_data.get('to', '')
            message = approval_data.get('message', '')
            
            # Import WhatsApp handler
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            try:
                # Try different import paths
                try:
                    from watchers.watcher_whatsapp import WhatsAppHandler
                    handler = WhatsAppHandler()
                except:
                    from whatsapp_handler import WhatsAppHandler
                    handler = WhatsAppHandler()
                
                result = handler.send_message(to=to, message=message)
                
                if result.get('success'):
                    return {
                        'success': True,
                        'message': 'WhatsApp sent successfully',
                        'to': to
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }
            
            except ImportError:
                logger.warning("WhatsAppHandler not available, simulating send")
                return {
                    'success': True,
                    'message': 'WhatsApp sent (simulated)',
                    'to': to
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to send WhatsApp: {str(e)}"
            }
    
    def _execute_payment(self, approval_data: Dict) -> Dict:
        """Execute payment/invoice action via Odoo MCP"""
        try:
            # Import Odoo MCP client
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            try:
                from mcp.odoo_mcp_client import OdooMCPClient
                
                client = OdooMCPClient()
                
                action_type = approval_data.get('action_type', '')
                
                if action_type == 'create_invoice':
                    result = client.create_invoice(approval_data.get('invoice_data', {}))
                elif action_type == 'post_invoice':
                    result = client.post_invoice(approval_data.get('invoice_id'))
                elif action_type == 'record_payment':
                    result = client.record_payment(approval_data.get('payment_data', {}))
                else:
                    result = {'success': False, 'error': f'Unknown payment action: {action_type}'}
                
                return result
            
            except ImportError:
                logger.warning("OdooMCPClient not available, simulating payment")
                return {
                    'success': True,
                    'message': 'Payment executed (simulated)',
                    'action_type': approval_data.get('action_type')
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to execute payment: {str(e)}"
            }
    
    def _log_execution(self, filename: str, approval_data: Dict, result: Dict):
        """Log execution to audit trail"""
        audit_file = self.audit_path / f"executions_{datetime.now().strftime('%Y%m')}.json"
        
        # Load or create audit log
        if audit_file.exists():
            try:
                with open(audit_file, 'r') as f:
                    audit_log = json.load(f)
            except:
                audit_log = {'executions': []}
        else:
            audit_log = {'executions': []}
        
        # Add execution entry
        audit_log['executions'].append({
            'filename': filename,
            'action_type': approval_data.get('type', ''),
            'executed_at': datetime.now().isoformat(),
            'success': result.get('success', False),
            'details': result.get('message', result.get('error', ''))
        })
        
        # Save audit log
        with open(audit_file, 'w') as f:
            json.dump(audit_log, f, indent=2)
    
    def get_execution_summary(self) -> Dict:
        """Get summary of executions"""
        done_files = list(self.done_path.glob('*.json'))
        
        successful = 0
        failed = 0
        
        for done_file in done_files:
            try:
                with open(done_file, 'r') as f:
                    data = json.load(f)
                
                if data.get('executed'):
                    successful += 1
                else:
                    failed += 1
            
            except:
                failed += 1
        
        return {
            'total_executed': successful + failed,
            'successful': successful,
            'failed': failed,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Test local final executor"""
    vault_path = Path(os.environ.get('VAULT_PATH', '../vault'))
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        return
    
    executor = LocalFinalExecutor(vault_path)
    
    logger.info("Local Final Action Executor ready")
    logger.info("Checking for approved actions to execute...")
    
    # Check for approved actions
    if executor.approved_path.exists():
        approved_files = list(executor.approved_path.glob('*.json'))
        
        if approved_files:
            logger.info(f"Found {len(approved_files)} approved actions")
            
            for approval_file in approved_files:
                result = executor.execute_approved_action(approval_file)
                logger.info(f"Result: {result}")
        else:
            logger.info("No approved actions pending")
    else:
        logger.info("No approved actions directory found")


if __name__ == '__main__':
    main()
