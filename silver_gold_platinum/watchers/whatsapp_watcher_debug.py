"""
WhatsApp Watcher - DEBUG VERSION
Har step pe batayega kya ho raha hai.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from datetime import datetime
from pathlib import Path

# Configuration
SESSION_PATH = Path(__file__).parent / "whatsapp_session"
VAULT_PATH = Path(__file__).parent.parent / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
LOG_FILE = Path(__file__).parent / "whatsapp.log"

# Keywords for urgent messages
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'price', 'order', 'meeting', 'call']

# Track processed messages
processed_messages = set()

def log(msg):
    """Log message to console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} | {msg}")
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {msg}\n")
    except:
        pass

def create_task(contact_name, message_text):
    """Create task file in vault from WhatsApp message"""
    try:
        # Clean contact name for filename
        safe_name = re.sub(r'[^\w\s-]', '', contact_name)[:25].replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Check if urgent
        is_urgent = any(k in message_text.lower() for k in KEYWORDS)
        
        # Create filename
        filename = f"WA_{timestamp}_{safe_name}.md"
        filepath = INBOX_PATH / filename
        
        # Ensure directory exists
        INBOX_PATH.mkdir(parents=True, exist_ok=True)
        
        # Format content
        content = f"""# WhatsApp Message from {contact_name}

## Contact
{contact_name}

## Received
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Priority
{'🔴 HIGH' if is_urgent else '🟢 Normal'}

## Message
{message_text}

## Action Required
- [ ] Reply to {contact_name}
- [ ] Follow up if needed

---
*Imported by WhatsApp Watcher*
"""
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if is_urgent:
            print(f"\n🔥 URGENT from {contact_name}: {message_text[:60]}...")
        else:
            print(f"\n✅ New message from {contact_name}: {message_text[:60]}...")
        
        return True
        
    except Exception as e:
        log(f"❌ Error creating task: {e}")
        return False


def check_new_messages(driver):
    """Check WhatsApp for new messages - DEBUG VERSION"""
    print("\n" + "="*50)
    print("🔍 Checking for new messages...")
    
    try:
        # Check URL
        current_url = driver.current_url
        print(f"📌 Current URL: {current_url}")
        
        if "web.whatsapp.com" not in current_url:
            print("⚠️ Not on WhatsApp Web! Reloading...")
            driver.get('https://web.whatsapp.com')
            time.sleep(3)
            return
        
        # Find all chat items
        chats = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"]')
        print(f"📊 Found {len(chats)} chat(s)")
        
        if len(chats) == 0:
            print("⚠️ No chats found! Maybe need to wait...")
            return
        
        new_count = 0
        for i, chat in enumerate(chats[:10]):  # Check first 10 chats
            try:
                # Get chat name
                name_elem = chat.find_element(By.CSS_SELECTOR, 'span[title]')
                if not name_elem:
                    continue
                name = name_elem.get_attribute('title')
                
                # Skip system chats
                if name in ["Status", "Broadcast Lists", ""]:
                    continue
                
                # Get last message
                try:
                    msg_elem = chat.find_element(By.CSS_SELECTOR, 'span[aria-label]')
                    if not msg_elem:
                        continue
                    message = msg_elem.text.strip()
                except Exception as e:
                    print(f"  ⚠️ Could not get message from chat {i}: {e}")
                    continue
                
                if not message:
                    continue
                
                # Check for unread indicator
                is_unread = False
                try:
                    unread_badge = chat.find_element(By.CSS_SELECTOR, '[class*="unread"]')
                    is_unread = True
                    print(f"  🟢 UNREAD: {name}")
                except:
                    if 'unread' in chat.get_attribute('aria-label', '').lower():
                        is_unread = True
                        print(f"  🟢 UNREAD (aria): {name}")
                
                # Show message info
                print(f"  💬 {name}: {message[:50]}...{' [UNREAD]' if is_unread else ''}")
                
                # Create unique ID for message
                msg_id = f"{name}:{message[:30]}"
                
                # Skip if already processed
                if msg_id in processed_messages:
                    print(f"    ⏭️  Already processed, skipping")
                    continue
                
                # Process if unread or has keywords
                if is_unread or any(k in message.lower() for k in KEYWORDS):
                    log(f"📱 {name}: {message[:60]}...")
                    create_task(name, message)
                    processed_messages.add(msg_id)
                    new_count += 1
                else:
                    print(f"    ⏭️  Read message, skipping")
                    
            except Exception as e:
                print(f"  ❌ Error processing chat {i}: {e}")
                continue
        
        print(f"\n✨ Processed {new_count} new message(s)")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error checking messages: {e}")
        import traceback
        traceback.print_exc()


def is_logged_in(driver):
    """Check if WhatsApp Web is logged in"""
    try:
        chat_list = driver.find_element(By.CSS_SELECTOR, '[data-testid="chat-list"]')
        if chat_list:
            return True
    except:
        pass
    
    try:
        app = driver.find_element(By.CSS_SELECTOR, '#app')
        if app and 'data-testid' in app.get_attribute('outerHTML'):
            return True
    except:
        pass
    
    try:
        if 'web.whatsapp.com' in driver.current_url:
            try:
                qr = driver.find_element(By.CSS_SELECTOR, '[data-testid="qr"]')
                return False
            except:
                return True
    except:
        pass
    
    return False


def wait_for_login(driver, timeout=300):
    """Wait for user to scan QR and login"""
    print()
    print("="*70)
    print("📱 SCAN QR CODE NOW")
    print("="*70)
    print()
    print("Apne phone mein:")
    print("  1. WhatsApp kholo")
    print("  2. Settings (⚙️) → Linked Devices")
    print("  3. 'Link a Device' pe tap karo")
    print("  4. Screen pe QR code scan karo")
    print()
    print(f"⏱️  Time: {timeout} seconds ({timeout//60} minutes)")
    print()
    print("="*70)
    print()
    
    start_time = time.time()
    last_check = 0
    
    while time.time() - start_time < timeout:
        if is_logged_in(driver):
            print()
            print("✅ LOGIN SUCCESS! WhatsApp Web loaded!")
            print()
            log("WhatsApp logged in successfully!")
            return True
        
        elapsed = int(time.time() - start_time)
        if elapsed > 0 and elapsed % 10 == 0 and elapsed != last_check:
            remaining = timeout - elapsed
            print(f"⏳ Waiting... {remaining}s remaining")
            last_check = elapsed
        
        time.sleep(2)
    
    return False


def main():
    print()
    print("="*70)
    print("WHATSAPP WATCHER - DEBUG VERSION")
    print("="*70)
    print()
    
    # Setup directories
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    
    log("Starting WhatsApp Watcher...")
    log(f"Session: {SESSION_PATH}")
    log(f"Inbox: {INBOX_PATH}")
    print()
    
    # Setup Chrome with persistent profile
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f'--user-data-dir={SESSION_PATH}')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument('--window-size=1280,720')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Start Chrome
    print("▶ Opening Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("▶ Going to WhatsApp Web...")
    driver.get('https://web.whatsapp.com')
    
    # Wait for login
    logged_in = wait_for_login(driver, timeout=300)
    
    if not logged_in:
        print()
        print("❌ Login timeout! 5 minutes ho gaye.")
        print()
        driver.quit()
        return
    
    # Main loop
    print("="*70)
    print("✅ WATCHER RUNNING - CHECKING EVERY 30 SECONDS")
    print("="*70)
    print()
    print("💡 Browser KHULA rakhein, Ctrl+C se band karein")
    print()
    print("Session saved. Next time no QR needed!")
    print("="*70)
    print()
    
    try:
        while True:
            check_new_messages(driver)
            print("\n⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
    except KeyboardInterrupt:
        print()
        log("Stopping watcher...")
        print("✅ Session saved!")
        driver.quit()
        print("Watcher stopped.")


if __name__ == "__main__":
    main()
