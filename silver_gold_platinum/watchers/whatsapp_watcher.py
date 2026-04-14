"""
WhatsApp Watcher - MANUAL DETECTION
Browser mein chat dikhai de toh 'Y' press karo
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import re
from datetime import datetime
from pathlib import Path
import threading

# Configuration
SESSION_PATH = Path(__file__).parent / "whatsapp_session"
VAULT_PATH = Path(__file__).parent.parent / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
LOG_FILE = Path(__file__).parent / "whatsapp.log"

KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'price', 'order', 'meeting', 'call']
processed_messages = set()

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} | {msg}")
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {msg}\n")
    except:
        pass

def create_task(contact_name, message_text):
    safe_name = re.sub(r'[^\w\s-]', '', contact_name)[:25].replace(' ', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    is_urgent = any(k in message_text.lower() for k in KEYWORDS)
    
    filename = f"WA_{timestamp}_{safe_name}.md"
    filepath = INBOX_PATH / filename
    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    
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

---
*Imported by WhatsApp Watcher*
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if is_urgent:
        print(f"\n🔥 URGENT from {contact_name}: {message_text[:60]}...")
    else:
        print(f"\n✅ New message from {contact_name}: {message_text[:60]}...")

def check_messages(driver):
    try:
        chats = driver.find_elements(By.CSS_SELECTOR, 'div[role="row"]')
        print(f"📊 Found {len(chats)} chats")
        
        new_count = 0
        for chat in chats[:10]:
            try:
                # Get name
                name_elem = chat.find_element(By.CSS_SELECTOR, 'span[title]')
                name = name_elem.get_attribute('title')
                
                if not name or name in ["Status", "Broadcast Lists"]:
                    continue
                
                # Get message from chat text
                try:
                    all_text = chat.text.strip()
                    lines = all_text.split('\n')
                    message = lines[-1] if len(lines) > 1 else all_text
                except:
                    continue
                
                if not message or len(message) < 2:
                    continue
                
                # Check unread
                is_unread = False
                try:
                    unread = chat.find_element(By.CSS_SELECTOR, 'span[class*="unread"]')
                    is_unread = True
                except:
                    pass
                
                msg_preview = message[:50].replace('\n', ' ')
                print(f"  💬 {name}: {msg_preview}{' [UNREAD]' if is_unread else ''}")
                
                msg_id = f"{name}:{message[:30]}"
                if msg_id in processed_messages:
                    print(f"    ⏭️  Already processed")
                    continue
                
                # ONLY process if UNREAD or has KEYWORDS
                if is_unread:
                    log(f"📱 {name}: {message[:60]}")
                    create_task(name, message)
                    processed_messages.add(msg_id)
                    new_count += 1
                    print(f"    ✅ UNREAD - Task created")
                elif any(k in message.lower() for k in KEYWORDS):
                    log(f"📱 {name}: {message[:60]}")
                    create_task(name, message)
                    processed_messages.add(msg_id)
                    new_count += 1
                    print(f"    ✅ KEYWORD - Task created")
                else:
                    print(f"    ⏭️  Read message, skipping")
                    
            except Exception as e:
                continue
        
        print(f"\n✨ New messages: {new_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def manual_login_wait(driver):
    """User manually confirms when logged in"""
    print()
    print("="*60)
    print("📱 WHATSAPP WEB LOADED")
    print("="*60)
    print()
    print("Agar browser mein WhatsApp Web dikh raha hai:")
    print("  1. QR Code scan karo (agar hai)")
    print("  2. Chat list dikhni chahiye")
    print()
    print("Jab ready ho, terminal mein 'Y' type karke Enter press karo")
    print()
    
    # Wait for user input
    while True:
        try:
            response = input("Ready? (Y/N): ").strip().lower()
            if response == 'y':
                print("\n✅ Starting watcher...")
                return True
            elif response == 'n':
                return False
        except:
            pass
        
        time.sleep(1)

def main():
    print()
    print("="*60)
    print("WHATSAPP WATCHER")
    print("="*60)

    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    INBOX_PATH.mkdir(parents=True, exist_ok=True)

    log("Starting...")

    # Chrome setup with stable flags
    chrome_options = Options()
    chrome_options.add_argument(f'--user-data-dir={SESSION_PATH}')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument('--window-size=1280,720')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print("▶ Opening Chrome...")
    
    try:
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    except Exception as e:
        print(f"❌ Chrome start error: {e}")
        print("Trying without webdriver-manager...")
        driver = webdriver.Chrome(options=chrome_options)

    print("▶ Going to WhatsApp Web...")
    driver.get('https://web.whatsapp.com')

    # Wait for user confirmation
    if not manual_login_wait(driver):
        print("❌ Cancelled!")
        driver.quit()
        return

    print()
    print("="*60)
    print("✅ WATCHER RUNNING - Check every 30s")
    print("="*60)
    print("Band karne: Ctrl+C")
    print("="*60)
    
    try:
        while True:
            check_messages(driver)
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n⏹️ Stopping...")
        driver.quit()

if __name__ == "__main__":
    main()
