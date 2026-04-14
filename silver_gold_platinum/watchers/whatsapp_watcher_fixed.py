"""
WhatsApp Watcher - FIXED Version
Browser STAYS OPEN. Session properly save hota hai.
QR code sirf FIRST TIME scan karna hai.
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
import json
from datetime import datetime
from pathlib import Path

# Configuration
SESSION_PATH = Path(__file__).parent.parent / "whatsapp_session"
VAULT_PATH = Path(__file__).parent.parent / "vault"
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOG_FILE = Path(__file__).parent.parent / "watcher_whatsapp.log"

KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'quote', 'price', 'order']
processed_messages = set()

def log(msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp} | {msg}")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp} | {msg}\n")

def create_task(contact_name, message_text):
    safe_name = re.sub(r'[^\w\s-]', '', contact_name)[:30].replace(' ', '_')
    is_urgent = any(k in message_text.lower() for k in KEYWORDS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"whatsapp_{timestamp}_{safe_name}.md"
    filepath = INBOX_PATH / filename

    INBOX_PATH.mkdir(parents=True, exist_ok=True)

    content = f"""# WhatsApp Message from {contact_name}

## Contact
{contact_name}

## Received
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Priority
{'high' if is_urgent else 'normal'}

## Message Content
{message_text}

## Actions
- [ ] Reply to {contact_name}
- [ ] Mark as done

---
*Keywords: {', '.join([k for k in KEYWORDS if k in message_text.lower()]) if is_urgent else 'none'}*
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    log(f"✅ Task created: {filename}")

    if is_urgent:
        NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)
        with open(NEEDS_ACTION_PATH / filename, 'w', encoding='utf-8') as f:
            f.write(content)
        log(f"🔥 URGENT: Also in Needs_Action")

def check_messages(driver):
    """Check WhatsApp for new messages"""
    try:
        # Check if still on WhatsApp Web
        if "web.whatsapp.com" not in driver.current_url:
            log("⚠️ Not on WhatsApp Web anymore. Reloading...")
            driver.get('https://web.whatsapp.com')
            time.sleep(5)
            return []

        # Find unread chats
        unread = driver.find_elements(By.CSS_SELECTOR, '[aria-label*="unread"]')[:10]
        log(f"Found {len(unread)} unread chat(s)")

        for chat in unread:
            try:
                name = chat.find_element(By.CSS_SELECTOR, 'span[title]').get_attribute('title')
                msg = chat.find_element(By.CSS_SELECTOR, 'span[aria-label]').text

                if not msg or name in ["Status", "Broadcast Lists"]:
                    continue

                msg_id = f"{name}:{msg[:50]}"
                if msg_id in processed_messages:
                    continue

                has_keyword = any(k in msg.lower() for k in KEYWORDS)
                if has_keyword or len(unread) <= 5:
                    log(f"📱 {name}: {msg[:80]}...")
                    create_task(name, msg)
                    processed_messages.add(msg_id)
            except Exception as e:
                log(f"Error extracting chat: {e}")
                continue
    except Exception as e:
        log(f"Error checking messages: {e}")
        # Try to recover
        try:
            driver.get('https://web.whatsapp.com')
            time.sleep(3)
        except:
            pass

def wait_for_login(driver, timeout=120):
    """Wait for user to scan QR code and login"""
    log("Waiting for WhatsApp login...")
    print()
    print("=" * 70)
    print("SCAN QR CODE NOW!")
    print("=" * 70)
    print()
    print("On your phone:")
    print("  1. Open WhatsApp")
    print("  2. Settings → Linked Devices")
    print("  3. Tap 'Link a Device'")
    print("  4. Scan QR code on screen")
    print()
    print(f"Waiting {timeout} seconds...")
    print()

    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]'))
        )
        log("✅ WhatsApp logged in successfully!")
        print()
        print("✅ SUCCESS! WhatsApp Web loaded!")
        print("✅ Session will be saved to:", SESSION_PATH)
        return True
    except Exception as e:
        log(f"⚠️ Login timeout: {e}")
        print()
        print("⚠️ QR code scan nahi hua.")
        return False

def main():
    print()
    print("=" * 70)
    print("WHATSAPP WATCHER - FIXED VERSION")
    print("=" * 70)
    print()

    # Setup directories
    SESSION_PATH.mkdir(parents=True, exist_ok=True)
    INBOX_PATH.mkdir(parents=True, exist_ok=True)
    NEEDS_ACTION_PATH.mkdir(parents=True, exist_ok=True)

    log("Starting WhatsApp Watcher (Fixed Version)...")
    print(f"Session Path: {SESSION_PATH}")
    print(f"Checking for saved session...")
    print()

    # Check if session exists
    session_file = SESSION_PATH / "Default" / "Web Data"
    has_session = session_file.exists()

    if has_session:
        print("✅ Saved session found! No QR code needed.")
        print()
    else:
        print("⚠️ No saved session found.")
        print("⚠️ You'll need to scan QR code THIS TIME ONLY.")
        print()

    # Setup Chrome with persistent profile
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f'--user-data-dir={SESSION_PATH}')
    chrome_options.add_argument('--profile-directory=Default')
    chrome_options.add_argument('--window-size=1280,720')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    print("▶ Opening Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    print("▶ Going to WhatsApp Web...")
    driver.get('https://web.whatsapp.com')

    # Wait for login (only if no saved session)
    if not has_session:
        if not wait_for_login(driver, timeout=120):
            print()
            print("⚠️ Login failed. Browser band ho jayega.")
            driver.quit()
            return
    else:
        # Give it time to load with saved session
        print("Loading with saved session...")
        time.sleep(10)
        # Check if actually logged in
        try:
            chat_list = driver.find_element(By.CSS_SELECTOR, '[data-testid="chat-list"]')
            log("✅ Loaded with saved session!")
        except:
            log("⚠️ Saved session invalid. Need to re-login.")
            if not wait_for_login(driver, timeout=120):
                driver.quit()
                return

    print()
    print("=" * 70)
    print("WATCHER RUNNING - Browser KO MAT BAND KARNA!")
    print("=" * 70)
    print()
    print("Yeh window KHULI RAHEGI.")
    print("Har 30 seconds mein messages check honge.")
    print()
    print("Jab band karna ho:")
    print("  → Browser window close kar do")
    print("  → Ya Ctrl+C press karo")
    print()
    print("Session saved to:", SESSION_PATH)
    print("Next time: No QR code needed!")
    print("=" * 70)
    print()

    # Main loop
    try:
        while True:
            time.sleep(30)
            check_messages(driver)
    except KeyboardInterrupt:
        print()
        log("Stopping watcher...")
        print("✅ Session saved. Next time no QR needed!")
        driver.quit()
        print("Watcher stopped.")

if __name__ == "__main__":
    main()
