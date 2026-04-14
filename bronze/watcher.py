import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import re
from datetime import datetime

# Set to keep track of processed files to prevent duplicates
processed_files = set()

class MarkdownHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Check if the created file is a markdown file in the Inbox folder
        if not event.is_directory and event.src_path.endswith('.md'):
            inbox_path = os.path.join(os.getcwd(), 'vault', 'Inbox')
            if event.src_path.startswith(inbox_path):
                self.process_markdown(event.src_path)

    def process_markdown(self, file_path):
        # Prevent duplicate processing
        if file_path in processed_files:
            return
            
        # Wait a moment to ensure the file is fully written
        time.sleep(0.5)
        
        try:
            # Read the content of the markdown file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add to processed set to prevent duplicate processing
            processed_files.add(file_path)
            
            # Extract title (first heading or filename)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            else:
                title = os.path.basename(file_path).replace('.md', '').replace('_', ' ').title()
            
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
            needs_action_path = os.path.join(os.getcwd(), 'vault', 'Needs_Action')
            new_filename = f"TODO_{os.path.basename(file_path)}"
            new_file_path = os.path.join(needs_action_path, new_filename)
            
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
            with open('watcher.log', 'a', encoding='utf-8') as log:
                log.write(f"[{timestamp}] Processed: {file_path} -> {new_file_path}\n")
                
            print(f"Processed: {file_path} -> {new_file_path}")
            
        except Exception as e:
            # Log errors
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_msg = f"[{timestamp}] Error processing {file_path}: {str(e)}\n"
            print(error_msg)
            with open('watcher.log', 'a', encoding='utf-8') as log:
                log.write(error_msg)

def main():
    # Set up the event handler and observer
    event_handler = MarkdownHandler()
    observer = Observer()
    
    # Watch the Inbox folder for new markdown files
    inbox_path = os.path.join(os.getcwd(), 'vault', 'Inbox')
    observer.schedule(event_handler, inbox_path, recursive=False)
    
    # Start the observer
    observer.start()
    print("Watching vault/Inbox for new markdown files...")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Stop the observer when interrupted
        observer.stop()
        print("\nStopping file watcher...")
    
    # Wait for the observer to finish
    observer.join()

if __name__ == "__main__":
    main()