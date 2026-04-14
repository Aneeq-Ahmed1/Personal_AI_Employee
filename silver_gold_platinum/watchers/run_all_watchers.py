"""
All Watchers Runner - Silver Tier
Pehle Gmail/FileSystem start, phir WhatsApp subprocess mein
"""

import sys
import threading
import time
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Watchers directory
WATCHERS_DIR = Path(__file__).parent

# Kaun se watchers enable hain
ENABLED_WATCHERS = {
    'whatsapp': True,   # WhatsApp Web watcher
    'gmail': True,      # Gmail watcher (needs credentials)
    'filesystem': True, # Filesystem watcher
    'linkedin': False,   # LinkedIn watcher (needs credentials)
}


def run_watcher(watcher_name, watcher_file, blocking=False):
    """Run a single watcher in a thread
    
    Args:
        watcher_name: Name of the watcher
        watcher_file: Path to watcher file
        blocking: If True, runs in main thread (for WhatsApp login)
    """
    print(f"\n{'='*60}")
    print(f"Starting {watcher_name.upper()} Watcher...")
    print(f"{'='*60}\n")

    try:
        # Import and run the watcher module
        import importlib.util
        spec = importlib.util.spec_from_file_location(watcher_name, watcher_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Call main function if exists
        if hasattr(module, 'main'):
            if blocking:
                # Run in main thread (blocking)
                module.main()
            else:
                # Run in current thread (for threading)
                module.main()
        else:
            print(f"Error: {watcher_file} has no main() function")
    except KeyboardInterrupt:
        print(f"\n{watcher_name} watcher stopped by user")
    except Exception as e:
        print(f"\n{watcher_name} watcher error: {type(e).__name__}: {str(e)}")


def run_whatsapp_login():
    """
    Run WhatsApp watcher and wait for login.
    Returns when user presses 'Y' and watcher starts monitoring.
    """
    whatsapp_file = WATCHERS_DIR / "whatsapp_watcher.py"
    
    # Import the module
    import importlib.util
    spec = importlib.util.spec_from_file_location("whatsapp", whatsapp_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Run main - yeh block karega jab tak user 'Y' na press kare
    # Lekin WhatsApp ka main loop bhi block karta hai...
    # Isliye humein WhatsApp ko thread mein run karna hoga
    
    # Start WhatsApp in a separate thread
    thread = threading.Thread(target=module.main, daemon=True)
    thread.start()
    
    # Wait for thread to initialize (browser open hone tak)
    print("⏳ Waiting for WhatsApp to load...")
    time.sleep(10)  # Give it time to open browser and show QR
    
    return thread


def main():
    print("\n" + "="*70)
    print("SILVER TIER - ALL WATCHERS RUNNER")
    print("="*70)
    print()

    # Enable/disable watchers
    print("Enabled Watchers:")
    for name, enabled in ENABLED_WATCHERS.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {name}")
    print()

    # Count enabled
    active_watchers = [k for k, v in ENABLED_WATCHERS.items() if v]
    print(f"Total Active: {len(active_watchers)}")
    print()

    if not active_watchers:
        print("⚠️  No watchers enabled!")
        print("Edit this file and set ENABLED_WATCHERS to True for watchers you want to run.")
        return

    print("="*70)
    print("STEP 1: Starting Gmail + Filesystem (Background)")
    print("="*70)
    print()

    # STEP 1: Start Gmail + Filesystem FIRST (background threads)
    background_watchers = ['gmail', 'filesystem']
    threads = []

    for watcher_name in background_watchers:
        if watcher_name not in active_watchers:
            continue
            
        watcher_file = WATCHERS_DIR / f"{watcher_name}_watcher.py"

        if not watcher_file.exists():
            print(f"⚠️  Warning: {watcher_file} not found, skipping...")
            continue

        thread = threading.Thread(
            target=run_watcher,
            args=(watcher_name, watcher_file),
            daemon=True
        )
        thread.start()
        threads.append(thread)
        print(f"✅ Started {watcher_name} watcher")
        time.sleep(1)

    print()
    print("="*70)
    print("STEP 2: Starting WhatsApp (Foreground - Needs Input)")
    print("="*70)
    print()

    # STEP 2: Start WhatsApp in SUBPROCESS (clean stdin/stdout)
    if 'whatsapp' in active_watchers:
        whatsapp_file = WATCHERS_DIR / "whatsapp_watcher.py"
        
        if whatsapp_file.exists():
            print("📱 Starting WhatsApp Watcher (separate process)...")
            print()
            
            # Run WhatsApp as subprocess - this will have clean input()
            whatsapp_process = subprocess.Popen(
                [sys.executable, str(whatsapp_file)],
                cwd=str(WATCHERS_DIR)
            )
            
            # Wait for WhatsApp process
            try:
                whatsapp_process.wait()
            except KeyboardInterrupt:
                whatsapp_process.terminate()
        else:
            print(f"⚠️  Warning: {whatsapp_file} not found, skipping WhatsApp...")

    # STEP 3: Keep background watchers running
    print()
    print("="*70)
    print("✅ WhatsApp process ended. Background watchers still running...")
    print("="*70)
    print()
    print("📧 Gmail: Checking every 60 seconds")
    print("📁 Filesystem: Watching folders")
    print()
    print("Band karne: Ctrl+C press karo")
    print("="*70)

    # Keep main thread alive for background watchers
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Stopping all watchers...")
        time.sleep(2)
        print("All watchers stopped.")


if __name__ == "__main__":
    main()
