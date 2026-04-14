"""
Platinum Tier - Claim-by-Move Rule Implementation
First agent to move item from Needs_Action to In_Progress/<agent>/ owns it
"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

logger = logging.getLogger('ClaimByMove')


class TaskClaimManager:
    """
    Implements claim-by-move rule for task ownership
    
    Rules:
    1. Tasks start in /Needs_Action/<domain>/
    2. First agent to move to /In_Progress/<agent>/ claims ownership
    3. Single-writer rule prevents conflicts
    4. All moves are logged for audit trail
    """
    
    def __init__(self, vault_path: Path, agent_name: str):
        self.vault_path = vault_path
        self.agent_name = agent_name  # 'cloud' or 'local'
        
        self.needs_action_path = vault_path / 'Needs_Action'
        self.in_progress_path = vault_path / 'In_Progress' / agent_name
        self.done_path = vault_path / 'Done'
        self.audit_path = vault_path / 'Updates' / 'audit_log'
        
        # Ensure directories exist
        for path in [self.needs_action_path, self.in_progress_path, self.done_path, self.audit_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def claim_task(self, task_file: Path, reason: str = "") -> bool:
        """
        Attempt to claim a task by moving it to this agent's In_Progress
        
        Returns True if successful, False if already claimed
        """
        if not task_file.exists():
            logger.warning(f"Task file not found: {task_file}")
            return False
        
        # Check if already claimed
        if self.is_already_claimed(task_file):
            logger.info(f"Task already claimed: {task_file.name}")
            return False
        
        # Check if this agent should handle this task type
        if not self.should_handle(task_file):
            logger.debug(f"Task not suitable for {self.agent_name}: {task_file.name}")
            return False
        
        try:
            # Move to In_Progress/<agent>/
            dest = self.in_progress_path / task_file.name
            task_file.rename(dest)
            
            # Update task metadata with claim info
            self._update_claim_metadata(dest, reason)
            
            # Log the claim
            self._log_claim(task_file.name, reason)
            
            logger.info(f"✅ Claimed task: {task_file.name} (agent: {self.agent_name})")
            return True
        
        except Exception as e:
            logger.error(f"Failed to claim task {task_file.name}: {e}")
            return False
    
    def is_already_claimed(self, task_file: Path) -> bool:
        """Check if task is already claimed by another agent"""
        try:
            # Check if file has assignment metadata
            metadata = self._read_task_metadata(task_file)
            
            if metadata and 'assigned_to' in metadata:
                assigned_agent = metadata.get('assigned_to')
                return assigned_agent != self.agent_name
            
            # Check if file is in another agent's In_Progress
            for agent_dir in (self.vault_path / 'In_Progress').iterdir():
                if agent_dir.is_dir() and agent_dir.name != self.agent_name:
                    if (agent_dir / task_file.name).exists():
                        return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error checking claim status: {e}")
            return False
    
    def should_handle(self, task_file: Path) -> bool:
        """Determine if this agent should handle this task type"""
        filename = task_file.name.lower()
        
        if self.agent_name == 'cloud':
            # Cloud handles: email drafts, social media drafts, LinkedIn
            return any(keyword in filename for keyword in [
                'email', 'social', 'linkedin', 'draft', 'schedule'
            ])
        
        elif self.agent_name == 'local':
            # Local handles: approvals, WhatsApp, banking, final sends
            return any(keyword in filename for keyword in [
                'approval', 'whatsapp', 'bank', 'payment', 'send', 'post'
            ])
        
        return False
    
    def release_task(self, task_file: Path, reason: str = "") -> bool:
        """
        Release a claimed task back to Needs_Action
        
        Use when agent cannot complete the task
        """
        if not task_file.exists():
            return False
        
        try:
            # Move back to Needs_Action
            dest = self.needs_action_path / task_file.name
            task_file.rename(dest)
            
            # Update metadata
            metadata = self._read_task_metadata(dest)
            
            if metadata:
                metadata['released_by'] = self.agent_name
                metadata['released_at'] = datetime.now().isoformat()
                metadata['release_reason'] = reason
                metadata['status'] = 'unassigned'
                
                with open(dest, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            logger.info(f"🔄 Released task: {task_file.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to release task: {e}")
            return False
    
    def complete_task(self, task_file: Path, result: Dict = None) -> bool:
        """
        Mark task as complete and move to Done
        """
        if not task_file.exists():
            return False
        
        try:
            # Move to Done
            dest = self.done_path / task_file.name
            task_file.rename(dest)
            
            # Update metadata
            metadata = self._read_task_metadata(dest)
            
            if metadata:
                metadata['completed_by'] = self.agent_name
                metadata['completed_at'] = datetime.now().isoformat()
                metadata['status'] = 'completed'
                
                if result:
                    metadata['result'] = result
                
                with open(dest, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            logger.info(f"✅ Completed task: {task_file.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
            return False
    
    def _update_claim_metadata(self, task_file: Path, reason: str):
        """Update task file with claim metadata"""
        metadata = self._read_task_metadata(task_file)
        
        if not metadata:
            # Create new metadata
            metadata = {}
        
        metadata['claimed_by'] = self.agent_name
        metadata['claimed_at'] = datetime.now().isoformat()
        metadata['claim_reason'] = reason
        metadata['status'] = 'in_progress'
        metadata['assigned_to'] = self.agent_name
        
        with open(task_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _read_task_metadata(self, task_file: Path) -> Optional[Dict]:
        """Read task metadata from file"""
        try:
            if task_file.suffix == '.json':
                with open(task_file, 'r') as f:
                    return json.load(f)
            
            elif task_file.suffix == '.md':
                # Parse markdown frontmatter
                with open(task_file, 'r') as f:
                    content = f.read()
                
                if content.startswith('---'):
                    # Has YAML frontmatter
                    import re
                    match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        # Simple key: value parsing
                        metadata = {}
                        for line in match.group(1).split('\n'):
                            if ':' in line:
                                key, value = line.split(':', 1)
                                metadata[key.strip()] = value.strip()
                        return metadata
            
            return None
        
        except Exception as e:
            logger.error(f"Error reading metadata from {task_file}: {e}")
            return None
    
    def _log_claim(self, task_name: str, reason: str):
        """Log claim to audit trail"""
        audit_file = self.audit_path / f"claims_{datetime.now().strftime('%Y%m')}.json"
        
        # Load or create audit log
        if audit_file.exists():
            with open(audit_file, 'r') as f:
                audit_log = json.load(f)
        else:
            audit_log = {'claims': []}
        
        # Add claim entry
        audit_log['claims'].append({
            'task': task_name,
            'claimed_by': self.agent_name,
            'claimed_at': datetime.now().isoformat(),
            'reason': reason
        })
        
        # Save audit log
        with open(audit_file, 'w') as f:
            json.dump(audit_log, f, indent=2)
    
    def get_unclaimed_tasks(self) -> list:
        """Get all unclaimed tasks from Needs_Action"""
        if not self.needs_action_path.exists():
            return []
        
        unclaimed = []
        
        for task_file in self.needs_action_path.rglob('*'):
            if task_file.is_file() and not self.is_already_claimed(task_file):
                if self.should_handle(task_file):
                    unclaimed.append(task_file)
        
        return unclaimed


def main():
    """Test claim-by-move"""
    import sys
    
    vault_path = Path(os.environ.get('VAULT_PATH', '../vault'))
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Create claim manager for cloud agent
    cloud_manager = TaskClaimManager(vault_path, 'cloud')
    
    # Get unclaimed tasks
    tasks = cloud_manager.get_unclaimed_tasks()
    
    logger.info(f"Found {len(tasks)} unclaimed tasks")
    
    for task in tasks:
        logger.info(f"  - {task.name}")


if __name__ == '__main__':
    main()
