"""
Silver Tier Filesystem Watcher
Watches Inbox for new files and moves them to Needs_Action.
Auto-triggers reasoning engine when files arrive in Needs_Action.
"""

import os
import time
import re
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Add silver skills to path for imports
sys.path.insert(0, str(PROJECT_ROOT / "silver" / "skills" / "reasoning-engine"))

# Configuration
VAULT_PATH = PROJECT_ROOT / "silver" / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOG_FILE = PROJECT_ROOT / "silver" / "watcher.log"

# Set to keep track of processed files to prevent duplicates
processed_files = set()

# Reasoning engine import (for auto-trigger)
reasoning_engine = None

def setup_logging():
    """Setup basic logging to file and console"""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()


def import_reasoning_engine():
    """Import the reasoning engine for auto-trigger capability"""
    global reasoning_engine
    try:
        # Use v2 which has OpenRouter fallback
        from reasoning_engine_v2 import process_single_task, initialize
        reasoning_engine = {
            'process_single_task': process_single_task,
            'initialize': initialize
        }
        # Initialize the reasoning engine (validates API key, tests connection)
        initialize()
        logger.info("Reasoning engine imported and initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to import reasoning engine: {type(e).__name__}: {str(e)}")
        logger.warning("Watcher will run without auto-reasoning trigger")
        reasoning_engine = None
        return False


class InboxHandler(FileSystemEventHandler):
    """Handles new markdown files in the Inbox folder"""
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            if str(event.src_path).startswith(str(INBOX_PATH)):
                self.process_markdown(event.src_path)

    def process_markdown(self, file_path):
        """Process a markdown file from the Inbox"""
        file_path = Path(file_path)
        
        if str(file_path) in processed_files:
            logger.info(f"File already processed, skipping: {file_path.name}")
            return

        # Wait a moment to ensure the file is fully written
        time.sleep(0.5)

        try:
            logger.info(f"File detected in Inbox: {file_path.name}")
            
            # Read the content of the markdown file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add to processed set to prevent duplicate processing
            processed_files.add(str(file_path))

            # Extract title (first heading or filename)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            else:
                title = file_path.stem.replace('_', ' ').title()

            # Generate a short summary (first 100 characters or first paragraph)
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            summary = ""
            for line in lines:
                if not line.startswith('#'):  # Skip headings
                    summary = line
                    break

            if len(summary) > 100:
                summary = summary[:97] + '...'

            # Create suggested next step
            suggested_step = "Review and prioritize this task."

            # Create new file in Needs_Action folder
            new_filename = f"TODO_{file_path.name}"
            new_file_path = NEEDS_ACTION_PATH / new_filename

            # Get current timestamp for ingestion
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Write the new markdown file with title, summary, and next step
            with open(new_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"## Summary\n{summary}\n\n")
                f.write(f"## Suggested Next Step\n{suggested_step}\n\n")
                f.write(f"## Ingestion Timestamp\n{timestamp}\n\n")
                f.write(f"## Original Content\n{content}")

            # Log the event
            logger.info(f"Processed: {file_path.name} -> {new_filename}")
            with open(LOG_FILE, 'a', encoding='utf-8') as log:
                log.write(f"[{timestamp}] Processed: {file_path} -> {new_file_path}\n")

            # STEP 4: AUTO-TRIGGER REASONING
            # When file is moved to Needs_Action, automatically trigger reasoning
            self.trigger_reasoning(new_file_path)

        except Exception as e:
            # Log errors
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_msg = f"Error processing {file_path}: {type(e).__name__}: {str(e)}"
            logger.error(error_msg)
            with open(LOG_FILE, 'a', encoding='utf-8') as log:
                log.write(f"[{timestamp}] ERROR: {error_msg}\n")

    def trigger_reasoning(self, file_path):
        """
        Auto-trigger reasoning engine when a file arrives in Needs_Action.
        This eliminates the need to manually run reasoning_loop.py
        """
        if reasoning_engine is None:
            logger.warning("Reasoning engine not available - skipping auto-trigger")
            logger.warning("Run reasoning_loop.py manually to generate plans")
            return
        
        try:
            logger.info("=" * 50)
            logger.info("AUTO-TRIGGER: Reasoning engine starting...")
            logger.info("=" * 50)
            
            # Call the reasoning engine to process this single file
            plan_path = reasoning_engine['process_single_task'](file_path)
            
            if plan_path:
                logger.info(f"AUTO-TRIGGER SUCCESS: Plan generated at {plan_path}")
            else:
                logger.info("AUTO-TRIGGER: No plan generated (may have been processed before)")
                
        except Exception as e:
            logger.error(f"AUTO-TRIGGER FAILED: {type(e).__name__}: {str(e)}")
            logger.error("You can run reasoning_loop.py manually to retry")


class NeedsActionHandler(FileSystemEventHandler):
    """
    Watches Needs_Action folder directly for any new files.
    This catches files added by other means (Gmail watcher, manual, etc.)
    """
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            if str(event.src_path).startswith(str(NEEDS_ACTION_PATH)):
                # Small delay to avoid duplicate triggering with InboxHandler
                time.sleep(0.2)
                if str(event.src_path) not in processed_files:
                    self.trigger_reasoning(event.src_path)
    
    def trigger_reasoning(self, file_path):
        """Trigger reasoning for files added directly to Needs_Action"""
        if reasoning_engine is None:
            return
        
        try:
            logger.info(f"Needs_Action watcher detected: {Path(file_path).name}")
            plan_path = reasoning_engine['process_single_task'](file_path)
            if plan_path:
                logger.info(f"Plan generated: {plan_path}")
        except Exception as e:
            logger.error(f"Error in Needs_Action trigger: {type(e).__name__}: {str(e)}")


def setup_directories():
    """Create required directories if they don't exist"""
    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)


def main():
    """Main function to start the filesystem watcher"""
    logger.info("=" * 60)
    logger.info("SILVER TIER FILESYSTEM WATCHER STARTING")
    logger.info("=" * 60)
    
    # Setup directories
    setup_directories()
    
    # Import and initialize reasoning engine
    import_reasoning_engine()
    
    # Set up observers
    observer = Observer()
    
    # Watch Inbox folder
    inbox_handler = InboxHandler()
    observer.schedule(inbox_handler, str(INBOX_PATH), recursive=False)
    logger.info(f"Watching Inbox: {INBOX_PATH}")
    
    # Watch Needs_Action folder (for files added by other watchers)
    needs_action_handler = NeedsActionHandler()
    observer.schedule(needs_action_handler, str(NEEDS_ACTION_PATH), recursive=False)
    logger.info(f"Watching Needs_Action: {NEEDS_ACTION_PATH}")
    
    # Start the observer
    observer.start()
    logger.info("Filesystem watcher started successfully")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer when interrupted
        observer.stop()
        logger.info("Stopping filesystem watcher...")

    # Wait for the observer to finish
    observer.join()
    logger.info("Filesystem watcher stopped")


if __name__ == "__main__":
    main()
