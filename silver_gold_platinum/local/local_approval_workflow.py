"""
Platinum Tier - Local Approval Workflow Manager
Handles human-in-the-loop approvals for cloud agent drafts
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger('ApprovalWorkflow')


class ApprovalWorkflowManager:
    """
    Manages approval workflow for Local agent
    
    Features:
    - Auto-approve low-risk actions
    - Flag high-risk for manual review
    - Track approval history
    - Generate approval notifications
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.pending_path = vault_path / 'Pending_Approval'
        self.approved_path = vault_path / 'Updates' / 'approved'
        self.rejected_path = vault_path / 'Updates' / 'rejected'
        self.audit_path = vault_path / 'Updates' / 'audit_log'
        
        # Ensure directories exist
        for path in [self.pending_path, self.approved_path, self.rejected_path, self.audit_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Approval rules
        self.auto_approve_types = {
            'email_draft': True,
            'social_post_draft': True,
            'ceo_briefing': True,
            'whatsapp_message': False,  # Requires manual review
            'payment': False,  # Always requires manual review
            'invoice': False,  # Always requires manual review
        }
    
    def get_pending_approvals(self) -> List[Dict]:
        """Get all pending approvals"""
        if not self.pending_path.exists():
            return []
        
        approvals = []
        
        for approval_file in self.pending_path.glob('*.json'):
            try:
                with open(approval_file, 'r') as f:
                    data = json.load(f)
                
                approvals.append({
                    'file': str(approval_file),
                    'filename': approval_file.name,
                    'data': data
                })
            
            except Exception as e:
                logger.error(f"Error reading approval file {approval_file}: {e}")
        
        return approvals
    
    def approve_action(self, approval_file: Path, approver: str = 'local_user') -> bool:
        """Approve a pending action"""
        try:
            with open(approval_file, 'r') as f:
                data = json.load(f)
            
            # Update status
            data['status'] = 'approved'
            data['approved_by'] = approver
            data['approved_at'] = datetime.now().isoformat()
            
            # Move to approved
            dest = self.approved_path / approval_file.name
            
            with open(dest, 'w') as f:
                json.dump(data, f, indent=2)
            
            approval_file.unlink()  # Remove from pending
            
            logger.info(f"✅ Approved: {approval_file.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to approve {approval_file}: {e}")
            return False
    
    def reject_action(self, approval_file: Path, reason: str, rejector: str = 'local_user') -> bool:
        """Reject a pending action"""
        try:
            with open(approval_file, 'r') as f:
                data = json.load(f)
            
            # Update status
            data['status'] = 'rejected'
            data['rejected_by'] = rejector
            data['rejected_at'] = datetime.now().isoformat()
            data['rejection_reason'] = reason
            
            # Move to rejected
            dest = self.rejected_path / approval_file.name
            
            with open(dest, 'w') as f:
                json.dump(data, f, indent=2)
            
            approval_file.unlink()  # Remove from pending
            
            logger.info(f"❌ Rejected: {approval_file.name} - {reason}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to reject {approval_file}: {e}")
            return False
    
    def auto_approve_if_safe(self) -> List[Path]:
        """
        Auto-approve safe actions
        Returns list of auto-approved files
        """
        auto_approved = []
        
        for approval_file in self.pending_path.glob('*.json'):
            try:
                with open(approval_file, 'r') as f:
                    data = json.load(f)
                
                action_type = data.get('type', '')
                
                if self.auto_approve_types.get(action_type, False):
                    if self.approve_action(approval_file, approver='auto_approve'):
                        auto_approved.append(approval_file)
                        logger.info(f"🤖 Auto-approved: {action_type}")
            
            except Exception as e:
                logger.error(f"Error in auto-approve: {e}")
        
        return auto_approved
    
    def requires_manual_review(self, approval_data: Dict) -> bool:
        """Check if action requires manual review"""
        action_type = approval_data.get('type', '')
        
        # Check auto-approve rules
        if self.auto_approve_types.get(action_type, False):
            return False
        
        # Check risk level
        risk_level = approval_data.get('risk_level', 'low')
        
        if risk_level in ['high', 'critical']:
            return True
        
        # Check if it involves money
        if 'payment' in action_type or 'invoice' in action_type:
            return True
        
        return False
    
    def generate_approval_summary(self) -> Dict:
        """Generate summary of approval status"""
        pending = len(list(self.pending_path.glob('*.json')))
        approved = len(list(self.approved_path.glob('*.json')))
        rejected = len(list(self.rejected_path.glob('*.json')))
        
        return {
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'total_processed': approved + rejected,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """Test approval workflow"""
    vault_path = Path(os.environ.get('VAULT_PATH', '../vault'))
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        return
    
    manager = ApprovalWorkflowManager(vault_path)
    
    # Auto-approve safe actions
    auto_approved = manager.auto_approve_if_safe()
    
    logger.info(f"Auto-approved {len(auto_approved)} actions")
    
    # Get pending
    pending = manager.get_pending_approvals()
    
    logger.info(f"{len(pending)} actions still pending approval")
    
    for p in pending:
        logger.info(f"  - {p['filename']}: {p['data'].get('type', 'unknown')}")


if __name__ == '__main__':
    main()
