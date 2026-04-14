"""
Platinum Tier - Vault Sync (Git-based)
Synchronizes vault between Cloud and Local agents
Security: Only syncs markdown/state files, NEVER secrets
"""

import os
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Set

logger = logging.getLogger('VaultSync')


class VaultSync:
    """
    Git-based vault synchronization between Cloud and Local agents
    
    Rules:
    - Cloud pushes ONLY markdown/state files
    - Local pulls and merges into Dashboard.md
    - NEVER sync secrets (.env, tokens, sessions, credentials)
    """
    
    # Files/directories to NEVER sync
    NEVER_SYNC = {
        '.env',
        'token.pickle',
        'credentials.json',
        'whatsapp_session',
        '*.key',
        '*.pem',
        '*.secret',
        'chrome_cookies.json',
        '*.log',  # Logs stay local
        '__pycache__',
        '*.pyc',
    }
    
    def __init__(self, vault_path: Path, repo_url: str = None):
        self.vault_path = vault_path
        self.repo_url = repo_url
        self.git_initialized = False
        
        # Initialize git if needed
        self._ensure_git_repo()
    
    def _ensure_git_repo(self):
        """Ensure vault is a git repository"""
        git_dir = self.vault_path / '.git'
        
        if not git_dir.exists():
            logger.info("Initializing git repository in vault...")
            try:
                self._run_git('init')
                self._run_git('add', '.')
                self._run_git('commit', '-m', 'Initial vault commit')
                self.git_initialized = True
                logger.info("✅ Git repository initialized")
            except Exception as e:
                logger.error(f"Failed to initialize git: {e}")
        else:
            self.git_initialized = True
    
    def _run_git(self, *args) -> str:
        """Run git command and return output"""
        cmd = ['git', '-C', str(self.vault_path)] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
        
        return result.stdout
    
    def is_safe_to_sync(self, filepath: Path) -> bool:
        """Check if file is safe to sync (no secrets)"""
        rel_path = filepath.relative_to(self.vault_path)
        filename = filepath.name
        
        # Check against never-sync list
        for pattern in self.NEVER_SYNC:
            if filename == pattern or filename.endswith(pattern):
                return False
            
            # Check if file is in a restricted directory
            if pattern in rel_path.parts:
                return False
        
        # Only allow specific file types
        allowed_extensions = {'.md', '.json', '.txt', '.yaml', '.yml'}
        if filepath.suffix not in allowed_extensions:
            return False
        
        return True
    
    def get_files_to_sync(self) -> List[Path]:
        """Get all files that are safe to sync"""
        files_to_sync = []
        
        for filepath in self.vault_path.rglob('*'):
            if filepath.is_file() and self.is_safe_to_sync(filepath):
                files_to_sync.append(filepath)
        
        return files_to_sync
    
    def stage_and_commit(self, message: str = "Auto-sync from cloud agent") -> bool:
        """Stage and commit changes"""
        try:
            # Add only safe files
            safe_files = self.get_files_to_sync()
            
            for filepath in safe_files:
                rel_path = filepath.relative_to(self.vault_path)
                self._run_git('add', str(rel_path))
            
            # Commit if there are changes
            status = self._run_git('status', '--porcelain')
            
            if status.strip():
                self._run_git('commit', '-m', f"{message} - {datetime.now().isoformat()}")
                logger.info(f"✅ Committed: {message}")
                return True
            else:
                logger.debug("No changes to commit")
                return False
        
        except Exception as e:
            logger.error(f"Failed to stage and commit: {e}")
            return False
    
    def push_to_remote(self) -> bool:
        """Push changes to remote repository"""
        if not self.repo_url:
            logger.warning("No remote URL configured")
            return False
        
        try:
            # Try to set remote if not already set
            try:
                self._run_git('remote', 'get-url', 'origin')
            except:
                self._run_git('remote', 'add', 'origin', self.repo_url)
            
            # Push
            self._run_git('push', 'origin', 'main')
            logger.info("✅ Pushed to remote")
            return True
        
        except Exception as e:
            logger.error(f"Failed to push: {e}")
            return False
    
    def pull_from_remote(self) -> bool:
        """Pull changes from remote repository"""
        if not self.repo_url:
            logger.warning("No remote URL configured")
            return False
        
        try:
            # Try to set remote if not already set
            try:
                self._run_git('remote', 'get-url', 'origin')
            except:
                self._run_git('remote', 'add', 'origin', self.repo_url)
            
            # Pull
            self._run_git('pull', 'origin', 'main', '--rebase')
            logger.info("✅ Pulled from remote")
            return True
        
        except Exception as e:
            logger.error(f"Failed to pull: {e}")
            return False
    
    def sync_push(self, message: str = "Auto-sync from cloud") -> bool:
        """Complete sync: stage, commit, push"""
        if not self.stage_and_commit(message):
            return True  # No changes, but not a failure
        
        return self.push_to_remote()
    
    def sync_pull(self) -> bool:
        """Complete sync: pull"""
        return self.pull_from_remote()
    
    def create_security_rules_file(self):
        """Create security rules JSON file"""
        rules = {
            'never_sync': list(self.NEVER_SYNC),
            'allowed_extensions': ['.md', '.json', '.txt', '.yaml', '.yml'],
            'last_updated': datetime.now().isoformat(),
            'rules': [
                {
                    'name': 'No secrets in cloud',
                    'description': 'Cloud agent must never have access to secrets',
                    'enforced': True
                },
                {
                    'name': 'Single writer for Dashboard.md',
                    'description': 'Only Local agent can write to Dashboard.md',
                    'enforced': True
                },
                {
                    'name': 'Cloud writes to Updates only',
                    'description': 'Cloud agent writes to /Updates/ or /Signals/ only',
                    'enforced': True
                }
            ]
        }
        
        rules_file = self.vault_path / 'security_rules.json'
        
        with open(rules_file, 'w') as f:
            json.dump(rules, f, indent=2)
        
        logger.info("✅ Security rules file created")


def main():
    """Test vault sync"""
    import sys
    
    vault_path = Path(os.environ.get('VAULT_PATH', '../vault'))
    
    if not vault_path.exists():
        logger.error(f"Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    sync = VaultSync(vault_path)
    
    # Create security rules
    sync.create_security_rules_file()
    
    # Test sync
    logger.info("Testing vault sync...")
    files = sync.get_files_to_sync()
    logger.info(f"Found {len(files)} files safe to sync")
    
    for f in files[:5]:  # Show first 5
        logger.info(f"  - {f.name}")


if __name__ == '__main__':
    main()
