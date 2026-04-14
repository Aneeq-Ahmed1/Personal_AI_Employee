"""
Browser-based Social Media Poster
Uses Selenium to post directly to social media platforms without API keys.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import logging
from pathlib import Path
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('browser_poster')


class BrowserSocialPoster:
    """
    Browser-based social media poster using Selenium.
    No API keys required - posts directly through browser automation.
    """

    def __init__(self, headless: bool = False):
        """
        Initialize the browser poster.

        Args:
            headless: Run browser in headless mode (default: False for better reliability)
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.base_dir = Path(__file__).parent.parent.parent
        self.vault_dir = self.base_dir / 'vault'
        self.screenshots_dir = self.vault_dir / 'Browser_Automation_Screenshots'
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Chrome profile directory for persistent sessions
        self.chrome_profile_dir = self.vault_dir / 'Chrome_Profile'
        self.chrome_profile_dir.mkdir(parents=True, exist_ok=True)

        # Credentials from environment
        self.credentials = {
            'facebook': {
                'email': os.getenv('FACEBOOK_EMAIL', ''),
                'password': os.getenv('FACEBOOK_PASSWORD', ''),
            },
            'instagram': {
                'username': os.getenv('INSTAGRAM_USERNAME', ''),
                'password': os.getenv('INSTAGRAM_PASSWORD', ''),
            },
            'twitter': {
                'username': os.getenv('TWITTER_USERNAME', ''),
                'password': os.getenv('TWITTER_PASSWORD', ''),
            },
            'linkedin': {
                'email': os.getenv('LINKEDIN_EMAIL', ''),
                'password': os.getenv('LINKEDIN_PASSWORD', ''),
            },
            'whatsapp': {
                'phone': os.getenv('WHATSAPP_PHONE', ''),
            },
            'gmail': {
                'email': os.getenv('GMAIL_EMAIL', ''),
                'password': os.getenv('GMAIL_PASSWORD', ''),
            }
        }

    def setup_driver(self):
        """Setup Chrome WebDriver with optimal settings and persistent profile"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless=new')

        # Use persistent user profile for saved logins
        chrome_options.add_argument(f'--user-data-dir={str(self.chrome_profile_dir)}')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # User agent to avoid detection
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Additional anti-detection measures
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # Ignore certificate errors
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set additional properties to appear more human-like
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            '''
        })
        
        self.wait = WebDriverWait(self.driver, 30)

        logger.info("✅ Chrome WebDriver initialized with anti-detection measures")

    def close_driver(self):
        """Close the browser"""
        if self.driver:
            # Keep browser open for manual verification if needed
            logger.info("Browser session complete. Keeping browser open for 10 seconds for verification...")
            time.sleep(10)  # Wait 10 seconds before closing
            self.driver.quit()
            logger.info("Browser closed")

    def take_screenshot(self, platform: str, action: str):
        """Take a screenshot for debugging"""
        try:
            if not self.driver:
                return None
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{platform}_{action}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            self.driver.save_screenshot(str(filepath))
            logger.debug(f"Screenshot saved: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.warning(f"Could not take screenshot: {str(e)}")
            return None

    def login_facebook(self):
        """Login to Facebook with persistent session"""
        if not self.credentials['facebook']['email'] or not self.credentials['facebook']['password']:
            logger.warning("Facebook credentials not configured. Manual login required.")
            # Still allow manual login
        else:
            logger.info("Facebook credentials found, attempting login...")

        logger.info("Navigating to Facebook...")
        self.driver.get('https://www.facebook.com')
        time.sleep(5)  # Wait longer for page load

        try:
            # Check if already logged in by looking for profile/menu elements
            for i in range(3):  # Check 3 times with delays
                try:
                    profile_menu = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Menu'], [aria-label*='profile'], div[role='button'][aria-label*='account']")
                    if profile_menu.is_displayed():
                        logger.info("✅ Already logged in to Facebook! (Session persisted)")
                        return True
                except:
                    pass
                time.sleep(2)

            # Accept cookies if prompted
            try:
                cookie_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Allow') or contains(text(), 'Accept') or contains(text(), 'Allow all')]")
                if cookie_btn.is_displayed():
                    cookie_btn.click()
                    logger.info("Cookies accepted")
                    time.sleep(2)
            except:
                pass

            # Only login if credentials are available
            if self.credentials['facebook']['email'] and self.credentials['facebook']['password']:
                # Login form
                logger.info("Logging into Facebook...")
                try:
                    email_input = self.wait.until(
                        EC.presence_of_element_located((By.ID, 'email'))
                    )
                    email_input.send_keys(self.credentials['facebook']['email'])

                    password_input = self.driver.find_element(By.ID, 'pass')
                    password_input.send_keys(self.credentials['facebook']['password'])
                    password_input.send_keys(Keys.RETURN)

                    # Wait for login to complete - check for various success indicators
                    logger.info("Waiting for login to complete (up to 30 seconds)...")
                    for i in range(10):  # Check every 3 seconds for up to 30 seconds
                        time.sleep(3)
                        try:
                            # Check for profile menu (logged in)
                            profile_menu = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Menu'], [aria-label*='profile']")
                            if profile_menu.is_displayed():
                                logger.info("✅ Facebook login successful!")
                                return True
                        except:
                            pass

                    logger.info("Facebook login process complete")
                    return True

                except Exception as e:
                    logger.error(f"Facebook login error: {str(e)}")
                    self.take_screenshot('facebook', 'login_error')
                    logger.info("📝 Please login manually in the browser window. Session will be saved for next time.")
            else:
                logger.info("📝 No credentials configured. Please login manually in the browser window.")
                logger.info("💡 Your login will be saved for future posts!")

            return True

        except Exception as e:
            logger.error(f"Facebook login failed: {str(e)}")
            self.take_screenshot('facebook', 'login_error')
            return False

    def _handle_facebook_post_button(self, auto_post: bool, message: str) -> dict:
        """
        Handle Facebook POST button clicking (extracted method).
        
        Facebook now has a TWO-STEP posting flow:
        Step 1: Click "Next" button (if present)
        Step 2: Click "Post" button on the review screen

        Args:
            auto_post: If True, auto-click Post button. If False, wait for manual confirm.
            message: The posted message (for logging)

        Returns:
            dict: Post result
        """
        try:
            if auto_post:
                # FULLY AUTOMATIC MODE: Handle TWO-STEP Facebook posting flow
                logger.info("🤖 AUTO MODE: Starting Facebook posting flow...")

                # CRITICAL: Wait for modal to be fully loaded
                time.sleep(3)
                self.take_screenshot('facebook', 'before_post_button')

                # === STEP 1: Check if "Next" button exists (new Facebook UI) ===
                logger.info("📍 STEP 1: Looking for 'Next' button (new Facebook UI)...")
                
                next_btn = None
                all_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR, 
                    "div[role='dialog'] button, div[role='dialog'] div[role='button']"
                )
                
                for btn in all_buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            text = btn.text.strip().lower()
                            aria = (btn.get_attribute('aria-label') or '').lower()
                            
                            # Look for exact "Next" text
                            if text == 'next' or aria == 'next':
                                next_btn = btn
                                logger.info(f"✅ Found NEXT button: '{btn.text}'")
                                break
                    except:
                        pass
                
                # Click Next button if found
                if next_btn:
                    logger.info("🖱️  Clicking NEXT button (step 1 of 2)...")
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(5)  # Wait for next screen to load
                    
                    self.take_screenshot('facebook', 'next_clicked')
                    logger.info("✅ NEXT button clicked, waiting for Post button...")
                    
                    # Wait for the review screen to load
                    time.sleep(3)
                else:
                    logger.info("ℹ️  No 'Next' button found (old Facebook UI or already on review screen)")

                # === STEP 2: Find and click POST button ===
                logger.info("📍 STEP 2: Finding POST button...")
                
                post_btn = None
                max_wait_attempts = 8

                for attempt in range(max_wait_attempts):
                    try:
                        # Get all buttons again (UI may have changed)
                        all_buttons = self.driver.find_elements(
                            By.CSS_SELECTOR, 
                            "div[role='dialog'] button, div[role='dialog'] div[role='button']"
                        )
                        
                        for btn in all_buttons:
                            try:
                                if btn.is_displayed() and btn.is_enabled():
                                    text = btn.text.strip()
                                    aria_label = btn.get_attribute('aria-label') or ''
                                    
                                    # Look for exact "Post" or "Share" text
                                    if text.lower() in ['post', 'share'] or aria_label.lower() in ['post', 'share']:
                                        post_btn = btn
                                        logger.info(f"✅ Found POST button: '{text}' (aria: '{aria_label}')")
                                        break
                            except:
                                pass
                        
                        if post_btn:
                            break
                        
                        logger.info(f"Attempt {attempt + 1}/{max_wait_attempts}: Post button not found yet, waiting...")
                        time.sleep(2)
                        
                    except Exception as search_err:
                        logger.debug(f"Attempt {attempt + 1} failed: {str(search_err)}")
                        time.sleep(2)

                # Fallback: Try XPATH selectors if button search fails
                if not post_btn:
                    logger.info("Trying XPATH selectors for POST button...")
                    post_selectors = [
                        "//div[@role='dialog']//div[@role='button' and not(contains(@aria-disabled, 'true')) and (contains(text(), 'Post') or contains(text(), 'Share'))]",
                        "//div[@role='dialog']//button[contains(@aria-label, 'Post') or contains(@aria-label, 'Share')]",
                        "//button[not(@disabled) and contains(text(), 'Post') or contains(text(), 'Share')]",
                    ]

                    for idx, selector in enumerate(post_selectors, 1):
                        try:
                            buttons = self.driver.find_elements(By.XPATH, selector)
                            logger.info(f"Selector {idx} found {len(buttons)} buttons")
                            
                            for btn in buttons:
                                if btn.is_displayed() and btn.is_enabled():
                                    aria_disabled = btn.get_attribute('aria-disabled')
                                    if not aria_disabled or aria_disabled == 'false':
                                        post_btn = btn
                                        logger.info(f"✅ Found POST button via XPATH (selector {idx})")
                                        break
                            
                            if post_btn:
                                break
                        except Exception as xpath_err:
                            logger.debug(f"XPATH selector {idx} failed: {str(xpath_err)}")

                # Final fallback: JavaScript-based detection
                if not post_btn:
                    logger.info("Final attempt: JavaScript-based Post button detection...")
                    try:
                        js_buttons = self.driver.execute_script("""
                            var buttons = [];
                            var allBtns = document.querySelectorAll('div[role="dialog"] button, div[role="dialog"] div[role="button"]');
                            for (var btn of allBtns) {
                                var text = (btn.innerText || '').trim();
                                var ariaLabel = btn.getAttribute('aria-label') || '';
                                var rect = btn.getBoundingClientRect();
                                
                                if ((text === 'Post' || text === 'Share' || 
                                     ariaLabel === 'Post' || ariaLabel === 'Share') &&
                                    rect.width > 50 && rect.height > 30 &&
                                    btn.offsetParent !== null) {
                                    buttons.push(btn);
                                }
                            }
                            return buttons;
                        """)
                        
                        if js_buttons and len(js_buttons) > 0:
                            logger.info(f"✅ Found {len(js_buttons)} Post button(s) via JavaScript")
                            # Try to select the first one via normal search again
                            time.sleep(1)
                            all_buttons = self.driver.find_elements(
                                By.CSS_SELECTOR, 
                                "div[role='dialog'] button, div[role='dialog'] div[role='button']"
                            )
                            for btn in all_buttons:
                                if btn.is_displayed() and btn.is_enabled():
                                    text = btn.text.strip().lower()
                                    if text in ['post', 'share']:
                                        post_btn = btn
                                        logger.info("✅ Found POST button (final attempt)")
                                        break
                    except Exception as js_err:
                        logger.debug(f"JavaScript detection failed: {str(js_err)}")

                if post_btn:
                    # Scroll into view and click
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", post_btn)
                    time.sleep(1)

                    # Use JavaScript click for more reliability
                    self.driver.execute_script("arguments[0].click();", post_btn)
                    logger.info("✅ POST button clicked!")

                    # Wait for post to complete
                    time.sleep(5)
                    self.take_screenshot('facebook', 'post_clicked')

                    # Verify post was successful
                    logger.info("Verifying post submission...")
                    try:
                        # Look for success indicators
                        success_indicators = [
                            "//*[contains(text(), 'shared')]",
                            "//*[contains(text(), 'Posted')]",
                            "//*[contains(text(), 'Your post')]",
                        ]

                        for indicator in success_indicators:
                            if self.driver.find_elements(By.XPATH, indicator):
                                logger.info(f"✅ Post success confirmed with: '{indicator}'!")
                                break
                    except:
                        pass

                    logger.info("✅ Facebook post submitted!")
                    return {
                        'success': True,
                        'platform': 'facebook',
                        'message': 'Post submitted successfully',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    logger.error("❌ POST button not found after all attempts")
                    self.take_screenshot('facebook', 'no_post_button')
                    
                    # FALLBACK: Try Ctrl+Enter keyboard shortcut (Facebook supports this)
                    logger.info("🔄 FALLBACK: Attempting Ctrl+Enter keyboard shortcut...")
                    try:
                        from selenium.webdriver.common.action_chains import ActionChains
                        from selenium.webdriver.common.keys import Keys
                        
                        # Try to find ANY text area in the dialog
                        text_areas = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] div[contenteditable='true'], div[role='dialog'] textarea, div[role='dialog'] div[data-contents='true'] div")
                        
                        if text_areas:
                            text_area = text_areas[0]
                            text_area.click()
                            time.sleep(1)
                            
                            # Send Ctrl+Enter
                            ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(Keys.ENTER).key_up(Keys.CONTROL).perform()
                            logger.info("✅ Ctrl+Enter sent! Post should be submitting...")
                            
                            time.sleep(3)
                            self.take_screenshot('facebook', 'ctrl_enter_sent')
                            
                            # Check if dialog closed (post successful)
                            dialogs = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog']")
                            if not dialogs:
                                logger.info("✅ Dialog closed - Post successful via Ctrl+Enter!")
                                return {
                                    'success': True,
                                    'platform': 'facebook',
                                    'message': 'Post submitted via Ctrl+Enter shortcut',
                                    'timestamp': datetime.now().isoformat()
                                }
                            else:
                                logger.warning("⚠️ Dialog still open - Ctrl+Enter may not have worked")
                                
                                # FINAL FALLBACK: Try to find Post button by text content
                                logger.info("🔧 FINAL FALLBACK: Searching for ANY Post/Share button...")
                                try:
                                    all_buttons = self.driver.execute_script("""
                                        var buttons = [];
                                        var allBtns = document.querySelectorAll('div[role="dialog"] button, div[role="dialog"] div[role="button"]');
                                        for (var btn of allBtns) {
                                            var text = (btn.innerText || btn.textContent || '').toLowerCase();
                                            var rect = btn.getBoundingClientRect();
                                            if ((text.includes('post') || text.includes('share')) && rect.width > 50) {
                                                buttons.push({
                                                    tag: btn.tagName,
                                                    text: text.substring(0, 50),
                                                    visible: btn.offsetParent !== null,
                                                    width: rect.width
                                                });
                                            }
                                        }
                                        return buttons;
                                    """)
                                    
                                    if all_buttons:
                                        logger.info(f"✅ Found {len(all_buttons)} potential Post buttons: {all_buttons}")
                                        
                                        # Click the widest one (likely the main Post button)
                                        widest_btn = max(all_buttons, key=lambda x: x['width'])
                                        logger.info(f"Clicking widest button: {widest_btn}")
                                        
                                        # Find and click it
                                        btn_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] div[role='button']")
                                        for btn in btn_elements:
                                            btn_text = (btn.text or '').lower()
                                            if ('post' in btn_text or 'share' in btn_text) and btn.is_displayed():
                                                self.driver.execute_script("arguments[0].click();", btn)
                                                logger.info("✅ Post button clicked via fallback!")
                                                time.sleep(3)
                                                self.take_screenshot('facebook', 'post_clicked_fallback')
                                                
                                                return {
                                                    'success': True,
                                                    'platform': 'facebook',
                                                    'message': 'Post submitted via fallback detection',
                                                    'timestamp': datetime.now().isoformat()
                                                }
                                    else:
                                        logger.warning("⚠️ No Post/Share buttons found in dialog")
                                except Exception as btn_err:
                                    logger.error(f"Button detection failed: {btn_err}")
                        else:
                            logger.warning("⚠️ No text area found for Ctrl+Enter fallback")
                    except Exception as fallback_err:
                        logger.error(f"❌ Ctrl+Enter fallback failed: {fallback_err}")

                    # Return partial success - text was entered but post not clicked
                    return {
                        'success': False,
                        'platform': 'facebook',
                        'error': 'POST button not found - you may need to click it manually',
                        'partial': True,
                        'message_entered': True
                    }
            else:
                # HITL MODE: Wait for user to manually click Post
                logger.info("\n" + "="*60)
                logger.info("👤 HITL MODE: Manual Post Confirmation")
                logger.info("="*60)
                logger.info("✅ AI content has been pasted into Facebook post field")
                logger.info("📝 Please review the content in the browser window")
                logger.info("🖱️  Click the 'Post' button manually when ready")
                logger.info("⏳ Waiting 60 seconds for manual confirmation...")
                logger.info("="*60 + "\n")

                self.take_screenshot('facebook', 'ready_for_manual_post')

                # Wait for user to manually post (60 seconds max)
                wait_time = 0
                max_wait = 60  # seconds

                while wait_time < max_wait:
                    time.sleep(5)
                    wait_time += 5

                    # Check if post was successful (look for feed elements or success indicators)
                    try:
                        # Look for elements that appear after posting
                        success_indicators = [
                            "//*[contains(text(), 'Your post has been shared')]",
                            "//*[contains(text(), 'Posted')]",
                            "//*[contains(text(), 'was shared')]",
                        ]
                        for indicator in success_indicators:
                            if self.driver.find_elements(By.XPATH, indicator):
                                logger.info("✅ Manual post detected!")
                                self.take_screenshot('facebook', 'manual_post_success')
                                return {
                                    'success': True,
                                    'platform': 'facebook',
                                    'message': 'Post confirmed by user',
                                    'mode': 'HITL',
                                    'timestamp': datetime.now().isoformat()
                                }
                    except:
                        pass

                # Timeout - user didn't post
                logger.warning("⏰ Timeout: User didn't click Post button within 60 seconds")
                self.take_screenshot('facebook', 'manual_post_timeout')
                return {
                    'success': False,
                    'platform': 'facebook',
                    'error': 'Timeout: User did not confirm post within 60 seconds',
                    'mode': 'HITL',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"POST button handling failed: {str(e)}")
            self.take_screenshot('facebook', 'post_button_error')
            return {
                'success': False,
                'platform': 'facebook',
                'error': f'POST button handling failed: {str(e)}'
            }

    def post_to_facebook(self, message: str, image_path: str = None, auto_post: bool = True) -> dict:
        """
        Post to Facebook through browser automation.
        Version 7: With HITL (Human-in-the-Loop) mode
        
        Modes:
        - auto_post=True: Fully automatic (finds and clicks Post button)
        - auto_post=False: HITL mode (pastes content, waits for user to click Post)

        Args:
            message: Post text
            image_path: Optional path to image file
            auto_post: If False, wait for user to manually click Post button

        Returns:
            dict: Post result
        """
        try:
            if not self.driver:
                self.setup_driver()

            self.login_facebook()

            # Navigate to Facebook home
            logger.info("Navigating to Facebook home...")
            self.driver.get('https://www.facebook.com')
            time.sleep(5)

            self.take_screenshot('facebook', 'home_loaded')
            logger.info("✅ Facebook home loaded")

            # Step 1: Click on "What's on your mind?" to open composer modal
            logger.info("Opening post composer...")
            composer_clicked = False

            # CRITICAL: Facebook pe multiple "Post" buttons hote hain (existing posts ke)
            # Sirf TOP composer button pe click karna hai
            # Strategy: Specific selectors use karo jo sirf composer ko match karein
            
            methods_tried = []

            # Method 1: CSS Selector - Most Specific (Facebook's actual composer structure)
            try:
                logger.info("Method 1: Trying SPECIFIC composer button selector...")
                
                # Facebook composer button has VERY specific structure
                # It's ALWAYS in a div with specific classes near the top of feed
                composer_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.x1n2onr6.x1n3bz8f.x47corl.x1ye8g25.xud65wk.x1q0q8m5.x15z7jvv.x16n37ed.x1n25116.x1r0x85q.x1fqp7bg.x1ypdohk.x78zum5.x1lq5wgf.xgflcyi.x889kno.x1c4vz4f.x150jy0e.x178xt8z.x13vifvy.x10l6tqk.x17z2mba.x1g3eztr.x15k900w.x1c64z2h.x1g022ox"
                )
                
                if composer_buttons and composer_buttons[0].is_displayed():
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", composer_buttons[0])
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", composer_buttons[0])
                    composer_clicked = True
                    methods_tried.append("FB Native Class")
                    logger.info("✅ Composer opened via Facebook native classes")
                    time.sleep(3)
                    self.take_screenshot('facebook', 'composer_clicked_native')
                    
            except Exception as e1:
                logger.warning(f"Method 1 (FB Classes) failed: {str(e1)}")
                methods_tried.append(f"FB Classes failed: {str(e1)}")

            # Method 2: Text-based detection (MOST RELIABLE - debug proven)
            if not composer_clicked:
                try:
                    logger.info("Method 2: Trying text-based detection (debug proven)...")
                    
                    # Debug se prove hua ke composer button ka text "What's on your mind, <name>?" hota hai
                    # Yeh UNIQUE hai - kisi aur button ka text aisa nahi hota
                    script = """
                    var allButtons = document.querySelectorAll('div[role="button"], button, span[role="button"]');
                    
                    for (var btn of allButtons) {
                        var text = btn.innerText || btn.textContent || '';
                        var rect = btn.getBoundingClientRect();
                        
                        // COMPOSER BUTTON:
                        // - Text MUST contain "mind" (case insensitive)
                        // - MUST be wide (>200px)
                        // - MUST be in top 600px
                        // - MUST NOT be inside an <article> (user posts)
                        if (text.toLowerCase().includes('mind') && 
                            rect.width > 200 && 
                            rect.top < 600 &&
                            !btn.closest('article')) {
                            
                            btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                            btn.click();
                            console.log('✅ Composer clicked via text detection');
                            console.log('   Text:', text);
                            console.log('   Size:', rect.width, 'x', rect.height);
                            return true;
                        }
                    }
                    return false;
                    """
                    
                    result = self.driver.execute_script(script)
                    if result:
                        composer_clicked = True
                        methods_tried.append("Text Detection")
                        logger.info("✅ Composer opened via text detection (MOST RELIABLE)")
                        time.sleep(3)
                        self.take_screenshot('facebook', 'composer_clicked_text')
                        
                except Exception as e2:
                    logger.warning(f"Method 2 (Text Detection) failed: {str(e2)}")
                    methods_tried.append(f"Text Detection failed: {str(e2)}")

            # Method 3: Aria-label with position filter (top section only)
            if not composer_clicked:
                try:
                    logger.info("Method 3: Trying aria-label with position filter...")
                    
                    # Composer button ALWAYS has specific aria-label
                    # AND it's ALWAYS near the top of the page
                    script = """
                    var buttons = document.querySelectorAll("div[role='button'][aria-label*='post'], div[role='button'][aria-label*='Post']");
                    
                    for (var btn of buttons) {
                        var rect = btn.getBoundingClientRect();
                        
                        // Composer button is ALWAYS in top 400px of page
                        // Existing posts ke buttons neeche hote hain
                        if (rect.top < 400 && rect.width > 100 && rect.height > 40) {
                            // Check if it contains "mind" text
                            if (btn.innerText.includes('mind') || btn.innerText.includes('Post')) {
                                btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                                btn.click();
                                return true;
                            }
                        }
                    }
                    return false;
                    """
                    
                    result = self.driver.execute_script(script)
                    if result:
                        composer_clicked = True
                        methods_tried.append("Position Filter")
                        logger.info("✅ Composer opened via position filter")
                        time.sleep(3)
                        self.take_screenshot('facebook', 'composer_clicked_position')
                        
                except Exception as e3:
                    logger.warning(f"Method 3 (Position) failed: {str(e3)}")
                    methods_tried.append(f"Position failed: {str(e3)}")

            # Method 4: Direct text with parent structure check
            if not composer_clicked:
                try:
                    logger.info("Method 4: Trying structured XPath (composer-specific)...")
                    
                    # Composer button has specific parent structure
                    # It's inside a div that's NOT inside an article or post
                    xpath = """
                        //div[@role='button' and .//span[contains(text(), "mind")]]
                        [not(ancestor::div[@aria-label*='post'] or ancestor::article)]
                    """
                    
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    
                    if elements and elements[0].is_displayed():
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", elements[0])
                        composer_clicked = True
                        methods_tried.append("Structured XPath")
                        logger.info("✅ Composer opened via structured XPath")
                        time.sleep(3)
                        self.take_screenshot('facebook', 'composer_clicked_xpath')
                        
                except Exception as e4:
                    logger.warning(f"Method 4 (Structured XPath) failed: {str(e4)}")
                    methods_tried.append(f"XPath failed: {str(e4)}")

            # Method 5: Last resort - JavaScript with strict filters
            if not composer_clicked:
                try:
                    logger.info("Method 5: Last resort - JavaScript with relaxed filters...")
                    
                    # CRITICAL FIX: Facebook composer button ab "post" container mein hai
                    # isInPost check hata diya composer ke liye
                    script = """
                    // Find ALL buttons with 'mind' or 'Post' text
                    var allButtons = document.querySelectorAll('div[role="button"], button, span[role="button"]');
                    
                    for (var btn of allButtons) {
                        var text = btn.innerText || btn.textContent || '';
                        var placeholder = btn.getAttribute('placeholder') || '';
                        var rect = btn.getBoundingClientRect();
                        
                        // COMPOSER BUTTON DETECTION:
                        // 1. Must be in top 600px (composer is at top)
                        // 2. Must be at least 200px wide (composer is wide)
                        // 3. Must contain "mind" OR have placeholder
                        // 4. Must NOT be inside an article (user posts)
                        // NOTE: isInPost check removed - composer is now in a "post" container
                        if (rect.top < 600 && 
                            rect.width > 200 && 
                            (text.includes('mind') || placeholder.includes('mind')) &&
                            !btn.closest('article')) {
                            
                            btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                            btn.click();
                            console.log('✅ Composer button clicked:', btn);
                            console.log('   Text:', text);
                            console.log('   Position:', rect.top, 'x', rect.left);
                            console.log('   Size:', rect.width, 'x', rect.height);
                            return true;
                        }
                    }
                    
                    console.log('❌ No composer button found with relaxed filters');
                    return false;
                    """
                    
                    result = self.driver.execute_script(script)
                    if result:
                        composer_clicked = True
                        methods_tried.append("Relaxed JS")
                        logger.info("✅ Composer opened via relaxed JavaScript filters")
                        time.sleep(3)
                        self.take_screenshot('facebook', 'composer_clicked_relaxed')
                        
                except Exception as e5:
                    logger.warning(f"Method 5 (Relaxed JS) failed: {str(e5)}")
                    methods_tried.append(f"Relaxed JS failed: {str(e5)}")

            # Wait for modal to open
            logger.info("Waiting for composer modal to open...")
            time.sleep(5)  # Increased wait time
            
            # Check if page reloaded (Facebook sometimes reloads after composer click)
            try:
                current_url = self.driver.current_url
                if "facebook.com" not in current_url:
                    logger.warning("Page redirected, navigating back to Facebook...")
                    self.driver.get("https://www.facebook.com")
                    time.sleep(3)
            except Exception as url_err:
                logger.warning(f"URL check failed: {str(url_err)}")
            
            # Take screenshot to verify modal is open
            self.take_screenshot('facebook', 'after_composer_click')
            
            # Verify modal is actually open
            modal_open = False
            try:
                modal_indicators = [
                    (By.CSS_SELECTOR, "div[role='dialog']"),
                    (By.CSS_SELECTOR, "div[aria-label*='post']"),
                    (By.CSS_SELECTOR, "div[contenteditable='true']"),
                ]
                for by_type, selector in modal_indicators:
                    elements = self.driver.find_elements(by_type, selector)
                    if elements:
                        logger.info(f"✅ Modal detected via: {selector}")
                        modal_open = True
                        break
            except Exception as modal_err:
                logger.warning(f"Modal check failed: {str(modal_err)}")
            
            if not composer_clicked:
                logger.error("❌ Composer button click FAILED after all 5 methods!")
                logger.error(f"Methods tried: {', '.join(methods_tried)}")
                self.take_screenshot('facebook', 'composer_failed_all')
                return {
                    'success': False,
                    'platform': 'facebook',
                    'error': 'Composer button click failed - Facebook may have changed UI'
                }
            
            if not modal_open:
                logger.warning("⚠️ Modal may not be open - but will try to continue...")
                self.take_screenshot('facebook', 'modal_status_unknown')

            # Step 2: Enter message using JavaScript (MOST RELIABLE)
            logger.info("Entering message using JavaScript...")

            # First verify driver is still connected
            try:
                self.driver.current_url
                logger.info("✅ Driver connection verified")
            except Exception as driver_err:
                logger.error(f"Driver disconnected: {str(driver_err)}")
                logger.info("Attempting to recover driver...")
                try:
                    # Try to reinitialize driver
                    self.driver.quit()
                    time.sleep(2)
                    self.setup_driver()
                    self.driver.get("https://www.facebook.com")
                    time.sleep(5)
                    logger.info("✅ Driver recovered, re-attempting composer click...")

                    # Click composer again
                    composer_script = """
                    var elements = document.evaluate(
                        "//*[contains(text(), 'mind') or contains(text(), 'Post')]",
                        document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null
                    );
                    for (var i = 0; i < elements.snapshotLength; i++) {
                        var el = elements.snapshotItem(i);
                        if (el.offsetParent !== null && el.offsetWidth > 50) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                    """
                    self.driver.execute_script(composer_script)
                    time.sleep(3)
                except Exception as recover_err:
                    logger.error(f"Driver recovery failed: {str(recover_err)}")
                    return {
                        'success': False,
                        'platform': 'facebook',
                        'error': f'Driver disconnected and recovery failed: {str(recover_err)}'
                    }

            try:
                # CRITICAL: Wait for modal AND contenteditable div with explicit waits
                logger.info("Waiting for text input area...")
                
                # Wait for dialog to appear first
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='dialog']"))
                )
                logger.info("✅ Modal dialog found")
                time.sleep(2)
                
                # Wait for contenteditable div with multiple retries
                text_input = None
                max_retries = 5
                
                for retry in range(max_retries):
                    try:
                        logger.info(f"Attempt {retry + 1}/{max_retries} to find text input...")
                        
                        # Method A: Wait for contenteditable div inside dialog
                        text_elements = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='dialog'] div[contenteditable='true']"))
                        )
                        
                        if text_elements:
                            for el in text_elements:
                                if el.is_displayed() and el.is_enabled():
                                    text_input = el
                                    logger.info(f"✅ Found text input in dialog (attempt {retry + 1})")
                                    break
                        
                        if text_input:
                            break
                            
                    except Exception as wait_err:
                        logger.warning(f"Attempt {retry + 1} failed: {str(wait_err)}")
                        time.sleep(2)
                
                # Fallback: Search all contenteditable divs if dialog search failed
                if not text_input:
                    logger.info("Searching all contenteditable divs as fallback...")
                    all_text_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
                    logger.info(f"Found {len(all_text_elements)} contenteditable divs")
                    
                    for el in all_text_elements:
                        if el.is_displayed() and el.is_enabled():
                            text_input = el
                            logger.info("✅ Found text input (fallback)")
                            break
                
                if text_input is None:
                    logger.error("❌ No visible contenteditable div found after all attempts")
                    self.take_screenshot('facebook', 'no_text_input')
                    return {
                        'success': False,
                        'platform': 'facebook',
                        'error': 'No text input area found - Facebook UI may have changed'
                    }

                # === CRITICAL FIX #1 (2026-04-04): Use send_keys() as PRIMARY method ===
                # REASON: JavaScript innerText doesn't trigger React's event system properly
                # send_keys() simulates real keyboard input - 100% reliable for Facebook
                logger.info("Injecting message using send_keys() (MOST RELIABLE METHOD)...")

                # Step 1: Scroll into view and focus
                self.driver.execute_script("arguments[0].scrollIntoView(true);", text_input)
                time.sleep(1)

                # Step 2: Click to focus
                text_input.click()
                time.sleep(1)

                # Step 3: Clear existing content
                try:
                    text_input.send_keys(Keys.CONTROL + "a")
                    time.sleep(0.5)
                    text_input.send_keys(Keys.DELETE)
                    time.sleep(0.5)
                    logger.info("✅ Cleared existing content")
                except Exception as clear_err:
                    logger.debug(f"Clear attempt failed: {clear_err}")

                # Step 4: Type message using send_keys (character-by-character simulation)
                message_text = message[:500]  # Facebook limit
                logger.info(f"Typing message ({len(message_text)} chars)...")

                injection_success = False

                # PRIMARY METHOD: send_keys() - simulates real typing
                try:
                    text_input.send_keys(message_text)
                    logger.info("✅ Message typed using send_keys()")
                    time.sleep(2)

                    # Verify text was entered
                    actual_text = text_input.text
                    if actual_text and len(actual_text.strip()) > 10:
                        logger.info(f"✅ Text verified: {len(actual_text.strip())} chars in field")
                        injection_success = True
                    else:
                        logger.warning(f"⚠️ Send_keys verification weak ({len(actual_text.strip()) if actual_text else 0} chars)")

                except Exception as send_err:
                    logger.warning(f"send_keys() failed: {send_err}")

                # FALLBACK METHOD: JavaScript with React event simulation
                if not injection_success:
                    logger.info("Trying JavaScript fallback with React events...")
                    try:
                        self.driver.execute_script("""
                            var element = arguments[0];
                            var text = arguments[1];

                            // Clear and set
                            element.innerText = '';
                            element.innerText = text;
                            element.focus();

                            // Trigger React 16+ synthetic events
                            var inputEvent = new InputEvent('input', {
                                bubbles: true,
                                cancelable: true,
                                inputType: 'insertText',
                                data: text
                            });
                            element.dispatchEvent(inputEvent);

                            var changeEvent = new Event('change', {
                                bubbles: true,
                                cancelable: true
                            });
                            element.dispatchEvent(changeEvent);

                            console.log('✅ React events triggered');
                        """, text_input, message_text)
                        logger.info("✅ JavaScript + React events complete")
                        time.sleep(2)
                        injection_success = True

                    except Exception as js_err:
                        logger.error(f"❌ Both text injection methods failed: {js_err}")

                # Step 5: Wait for Post button to potentially enable
                logger.info("Waiting 3 seconds for Post button to enable...")
                time.sleep(3)

                # Verify Post button status
                try:
                    post_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Post') or contains(text(), 'Share')]")
                    logger.info(f"Found {len(post_buttons)} Post/Share buttons")

                    for idx, btn in enumerate(post_buttons[:3], 1):
                        try:
                            btn_text = btn.text.strip()
                            is_enabled = btn.is_enabled()
                            is_displayed = btn.is_displayed()
                            logger.info(f"Button {idx}: '{btn_text}' | Enabled: {is_enabled} | Displayed: {is_displayed}")
                        except Exception as btn_err:
                            logger.debug(f"Button {idx} check failed: {btn_err}")
                except Exception as check_err:
                    logger.debug(f"Post button check failed: {check_err}")

            except Exception as e:
                logger.error(f"Message injection failed: {str(e)}")
                self.take_screenshot('facebook', 'message_injection_error')
                import traceback
                logger.error(traceback.format_exc())
                return {
                    'success': False,
                    'platform': 'facebook',
                    'error': f'Message entry failed: {str(e)}'
                }

            # Step 3: Handle POST button
            return self._handle_facebook_post_button(auto_post, message)

        except Exception as e:
            logger.error(f"Facebook post failed: {str(e)}")
            self.take_screenshot('facebook', 'error')
            return {
                'success': False,
                'platform': 'facebook',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def login_instagram(self):
        """Login to Instagram with enhanced error handling"""
        if not self.credentials['instagram']['username'] or not self.credentials['instagram']['password']:
            logger.warning("⚠️  Instagram credentials not configured - waiting for manual login")
            # Allow manual login instead of raising exception
        else:
            logger.info("Instagram credentials found, attempting login...")

        logger.info("Navigating to Instagram...")
        
        # Navigate to Instagram with timeout handling
        try:
            self.driver.set_page_load_timeout(30)
            self.driver.get('https://www.instagram.com')
            logger.info("✅ Navigation command sent to Instagram")
        except Exception as nav_err:
            logger.error(f"❌ Navigation failed: {nav_err}")
            self.take_screenshot('instagram', 'navigation_error')
            return False

        try:
            # Wait for page to fully load (up to 20 seconds)
            logger.info("Waiting for Instagram to load (up to 20 seconds)...")
            page_loaded = False

            for i in range(20):
                try:
                    current_url = self.driver.current_url
                except:
                    logger.warning(f"  [{i}s] Cannot get current URL")
                    time.sleep(1)
                    continue
                
                if i == 0 or i % 5 == 0:
                    logger.info(f"  [{i}s] Current URL: {current_url}")

                # Check for redirects or error pages
                if 'challenge' in current_url.lower():
                    logger.error("⚠️  Instagram challenge page detected")
                    self.take_screenshot('instagram', 'challenge_page')
                    logger.info("⏸️  Waiting 60 seconds for manual challenge completion...")
                    for wait in range(60, 0, -1):
                        if 'challenge' not in self.driver.current_url.lower():
                            logger.info("✅ Challenge completed!")
                            break
                        if wait % 10 == 0:
                            logger.info(f"  {wait}s remaining...")
                        time.sleep(1)

                if 'checkpoint' in current_url.lower():
                    logger.error("⚠️  Instagram checkpoint page detected")
                    self.take_screenshot('instagram', 'checkpoint_page')
                    logger.info("⏸️  Waiting 60 seconds for manual checkpoint completion...")
                    for wait in range(60, 0, -1):
                        if 'checkpoint' not in self.driver.current_url.lower():
                            logger.info("✅ Checkpoint completed!")
                            break
                        if wait % 10 == 0:
                            logger.info(f"  {wait}s remaining...")
                        time.sleep(1)

                # Check if page is actually loading (not blank)
                if current_url in ['about:blank', 'chrome://newtab/', 'chrome://newtab']:
                    logger.warning(f"  [{i}s] Page not loading - still on browser default page")
                    time.sleep(1)
                    continue

                # Check if login form is present
                try:
                    username_field = self.driver.find_element(By.NAME, 'username')
                    if username_field.is_displayed():
                        logger.info("✅ Instagram login form loaded")
                        page_loaded = True
                        break
                except:
                    pass

                # Check if already logged in (home page loaded)
                if 'instagram.com' in current_url and 'login' not in current_url.lower() and 'signup' not in current_url.lower():
                    logger.info(f"✅ Already on Instagram home page: {current_url}")
                    self.take_screenshot('instagram', 'already_logged_in')
                    return True

                time.sleep(1)

            # Check if we're on Instagram at all after waiting
            try:
                final_url = self.driver.current_url
                if 'instagram.com' not in final_url:
                    logger.error(f"❌ Instagram did not load. Current URL: {final_url}")
                    self.take_screenshot('instagram', 'page_not_loaded')
                    logger.info("⏸️  Waiting 30 seconds for manual intervention...")
                    for wait in range(30, 0, -1):
                        if 'instagram.com' in self.driver.current_url:
                            logger.info("✅ Instagram loaded during wait!")
                            page_loaded = True
                            break
                        if wait % 10 == 0:
                            logger.info(f"  {wait}s remaining...")
                        time.sleep(1)
                    
                    if 'instagram.com' not in self.driver.current_url:
                        logger.error("❌ Instagram failed to load after manual wait")
                        return False
            except Exception as url_err:
                logger.error(f"❌ Cannot get current URL: {url_err}")
                return False

            if not page_loaded:
                logger.warning("⚠️  Login form not detected after 20 seconds")
                self.take_screenshot('instagram', 'login_form_not_found')
                logger.info("⏸️  Waiting 30 seconds for manual intervention...")
                for wait in range(30, 0, -1):
                    try:
                        current_url = self.driver.current_url
                        if 'instagram.com' in current_url and 'login' not in current_url.lower():
                            logger.info("✅ Logged in during manual wait!")
                            return True
                    except:
                        pass
                    if wait % 10 == 0:
                        logger.info(f"  {wait}s remaining...")
                    time.sleep(1)

            # Handle cookie/consent dialogs
            try:
                logger.info("Checking for consent dialogs...")
                consent_selectors = [
                    "//button[contains(text(), 'Allow')]",
                    "//button[contains(text(), 'Accept')]",
                    "//button[contains(text(), 'Allow all')]",
                    "//button[contains(text(), 'Accept All')]",
                ]

                for selector in consent_selectors:
                    try:
                        consent_btn = self.driver.find_element(By.XPATH, selector)
                        if consent_btn.is_displayed():
                            logger.info("Accepting consent dialog")
                            consent_btn.click()
                            time.sleep(2)
                            break
                    except:
                        continue
            except Exception as consent_err:
                logger.debug(f"Consent dialog check failed: {consent_err}")

            # Check if already logged in
            try:
                current_url = self.driver.current_url
                if 'accounts/login' not in current_url.lower() and 'accounts/signup' not in current_url.lower():
                    logger.info("✅ Already logged in to Instagram!")
                    return True
            except:
                pass

            # If credentials are configured, try automatic login
            if self.credentials['instagram']['username'] and self.credentials['instagram']['password']:
                # Enter credentials
                logger.info("Entering Instagram credentials...")
                
                try:
                    username_input = self.wait.until(
                        EC.presence_of_element_located((By.NAME, 'username'))
                    )
                    username_input.send_keys(self.credentials['instagram']['username'])

                    password_input = self.driver.find_element(By.NAME, 'password')
                    password_input.send_keys(self.credentials['instagram']['password'])
                    password_input.send_keys(Keys.RETURN)

                    # Wait for login to complete (up to 20 seconds)
                    logger.info("Waiting for Instagram login to complete (up to 20 seconds)...")

                    for i in range(20):
                        try:
                            current_url = self.driver.current_url
                        except:
                            time.sleep(1)
                            continue

                        # Check for successful login
                        if 'login' not in current_url.lower() and 'signup' not in current_url.lower():
                            logger.info("✅ Instagram login successful!")
                            self.take_screenshot('instagram', 'login_success')
                            return True

                        # Check for error message
                        try:
                            error_msg = self.driver.find_element(By.XPATH, "//div[contains(text(), 'incorrect') or contains(text(), 'not found')]")
                            if error_msg.is_displayed():
                                logger.error("❌ Instagram login failed: Incorrect username or password")
                                self.take_screenshot('instagram', 'login_failed')
                                return False
                        except:
                            pass

                        time.sleep(1)

                    # Login timeout
                    logger.warning("⏰ Instagram login timeout")
                    self.take_screenshot('instagram', 'login_timeout')
                    return False
                except Exception as login_err:
                    logger.error(f"❌ Login form interaction failed: {login_err}")
                    self.take_screenshot('instagram', 'login_form_error')
                    # Fall through to manual login wait
            else:
                logger.info("ℹ️  No credentials configured - waiting for manual login")

            # Wait for manual login if automatic failed or not configured
            logger.info("⏸️  Waiting 90 seconds for manual login...")
            manual_login_success = False
            
            for wait in range(90, 0, -1):
                try:
                    current_url = self.driver.current_url
                    if 'instagram.com' in current_url and 'login' not in current_url.lower() and 'signup' not in current_url.lower():
                        logger.info(f"✅ Manual login detected! URL: {current_url}")
                        self.take_screenshot('instagram', 'manual_login_success')
                        manual_login_success = True
                        break
                except:
                    pass
                
                if wait % 10 == 0:
                    logger.info(f"  {wait}s remaining for manual login...")
                time.sleep(1)
            
            if manual_login_success:
                return True
            else:
                logger.warning("⚠️  Manual login timeout or not detected")
                return False

        except Exception as e:
            logger.error(f"Instagram login failed: {str(e)}")
            self.take_screenshot('instagram', 'login_error')
            return False

    def post_to_instagram(self, caption: str, image_path: str = None) -> dict:
        """
        Post to Instagram through browser automation.
        FIXED: Proper login detection + post creation flow

        Args:
            caption: Post caption/text
            image_path: Optional path to image file

        Returns:
            dict: Post result
        """
        try:
            if not self.driver:
                self.setup_driver()

            # STEP 1: Navigate to Instagram
            logger.info("=" * 80)
            logger.info("STEP 1: Navigate to Instagram")
            logger.info("=" * 80)
            
            try:
                self.driver.set_page_load_timeout(30)
                self.driver.get('https://www.instagram.com')
                logger.info("✅ Instagram navigation successful")
            except Exception as nav_err:
                logger.error(f"❌ Navigation failed: {nav_err}")
                return {'success': False, 'error': f'Instagram navigation failed: {nav_err}'}
            
            # STEP 2: Wait for login (manual or auto)
            logger.info("=" * 80)
            logger.info("STEP 2: Wait for Login (90 seconds for manual)")
            logger.info("=" * 80)
            
            # Check credentials
            username = self.credentials['instagram']['username']
            password = self.credentials['instagram']['password']
            credentials_configured = (
                username and 
                password and 
                username != 'your_instagram_username' and 
                password != 'your_instagram_password'
            )
            
            # If credentials configured, try auto-login
            if credentials_configured:
                logger.info("✅ Credentials configured, attempting auto-login...")
                login_success = self.login_instagram()
                if not login_success:
                    logger.warning("⚠️  Auto-login failed, waiting for manual login...")
                    credentials_configured = False  # Fall through to manual wait
            else:
                logger.info("⚠️  No credentials - will wait for manual login")
            
            # If auto-login failed or no credentials, wait for manual login
            if not credentials_configured:
                logger.info("⏸️  Waiting 90 seconds for MANUAL login...")
                logger.info("👉  Please login in the browser window!")
                
                manual_login_detected = False
                for wait in range(90, 0, -1):
                    try:
                        current_url = self.driver.current_url
                        
                        # Check if login page
                        is_login_page = (
                            'login' in current_url.lower() or 
                            'accounts/login' in current_url.lower()
                        )
                        
                        # Check if past login page (home/feed)
                        is_logged_in = (
                            'instagram.com' in current_url and
                            not is_login_page and
                            'signup' not in current_url.lower() and
                            'challenge' not in current_url.lower()
                        )
                        
                        if wait % 10 == 0 or wait == 1:
                            logger.info(f"  [{wait}s] URL: {current_url} | {'✅ Logged in!' if is_logged_in else '⏳ Waiting...'}")
                        
                        if is_logged_in:
                            logger.info(f"✅ MANUAL LOGIN DETECTED! URL: {current_url}")
                            self.take_screenshot('instagram', 'manual_login_success')
                            manual_login_detected = True
                            break
                    except Exception as url_err:
                        logger.warning(f"  [{wait}s] URL check error: {url_err}")
                    
                    time.sleep(1)
                
                if not manual_login_detected:
                    logger.warning("⚠️  Manual login timeout or not detected, continuing anyway...")
                    self.take_screenshot('instagram', 'login_timeout_continuing')
            
            # STEP 3: Wait for page to stabilize after login
            logger.info("=" * 80)
            logger.info("STEP 3: Stabilize After Login")
            logger.info("=" * 80)
            
            logger.info("⏳ Waiting 5 seconds for page to stabilize...")
            time.sleep(5)
            
            # Check current URL
            try:
                current_url = self.driver.current_url
                logger.info(f"📍 Current URL after wait: {current_url}")
                logger.info(f"📍 Page title: {self.driver.title}")
                
                # If still on login page, navigate to home
                if 'login' in current_url.lower() or 'accounts' in current_url.lower():
                    logger.info("⚠️  Still on login page, navigating to home...")
                    self.driver.get('https://www.instagram.com')
                    time.sleep(5)
                    logger.info(f"📍 New URL: {self.driver.current_url}")
            except Exception as url_err:
                logger.warning(f"⚠️  URL check error: {url_err}")
            
            self.take_screenshot('instagram', 'after_login_stabilized')
            logger.info("✅ Page stabilized")
            
            # STEP 4: Check if we need to dismiss "Save Info" or "Turn on Notifications"
            logger.info("=" * 80)
            logger.info("STEP 4: Dismiss Popups (if any)")
            logger.info("=" * 80)
            
            try:
                # Try to dismiss common Instagram popups
                popup_selectors = [
                    "button[aria-label='Close']",
                    "div[role='dialog'] button",
                    "//*[text()='Not Now']",
                    "//*[text()='Cancel']",
                ]
                
                for selector in popup_selectors:
                    try:
                        if selector.startswith('//'):
                            popup_btn = self.driver.find_element(By.XPATH, selector)
                        else:
                            popup_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if popup_btn.is_displayed():
                            logger.info(f"✅ Found popup, dismissing...")
                            popup_btn.click()
                            time.sleep(2)
                            logger.info("✅ Popup dismissed")
                            break
                    except:
                        continue
            except Exception as popup_err:
                logger.debug(f"No popups found or error: {popup_err}")
            
            self.take_screenshot('instagram', 'popups_dismissed')

            # STEP 5: Find and Click Create Post button
            logger.info("=" * 80)
            logger.info("STEP 5: Find Create Post Button")
            logger.info("=" * 80)
            
            create_clicked = False
            
            # Method 1: SVG aria-label="New post"
            try:
                logger.info("Method 1: SVG 'New post' button...")
                svg_buttons = self.driver.find_elements(By.CSS_SELECTOR, "svg[aria-label='New post']")
                logger.info(f"  Found {len(svg_buttons)} SVG buttons")
                
                if svg_buttons:
                    # Click parent of SVG
                    parent = svg_buttons[0].find_element(By.XPATH, "..")
                    self.driver.execute_script("arguments[0].click();", parent)
                    create_clicked = True
                    logger.info("✅ Create button clicked via SVG")
                    time.sleep(3)
                    self.take_screenshot('instagram', 'create_clicked')
            except Exception as e1:
                logger.warning(f"  Method 1 failed: {e1}")
            
            # Method 2: Link to /create/
            if not create_clicked:
                try:
                    logger.info("Method 2: /create/ link...")
                    create_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href='/create/']")
                    logger.info(f"  Found {len(create_links)} create links")
                    
                    if create_links:
                        self.driver.execute_script("arguments[0].click();", create_links[0])
                        create_clicked = True
                        logger.info("✅ Create button clicked via link")
                        time.sleep(3)
                        self.take_screenshot('instagram', 'create_clicked_link')
                except Exception as e2:
                    logger.warning(f"  Method 2 failed: {e2}")
            
            # Method 3: JavaScript detection
            if not create_clicked:
                try:
                    logger.info("Method 3: JavaScript detection...")
                    result = self.driver.execute_script("""
                        var allButtons = document.querySelectorAll('div[role="button"], button, a[role="menuitem"]');
                        for (var btn of allButtons) {
                            var text = (btn.innerText || btn.textContent || '').toLowerCase();
                            var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                            var rect = btn.getBoundingClientRect();
                            
                            if ((text.includes('new') && text.includes('post')) ||
                                (text.includes('create')) ||
                                (ariaLabel.includes('new post')) ||
                                text === '+') {
                                if (rect.top < 300 && rect.width > 20) {
                                    btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                                    btn.click();
                                    return true;
                                }
                            }
                        }
                        return false;
                    """)
                    
                    if result:
                        create_clicked = True
                        logger.info("✅ Create button clicked via JavaScript")
                        time.sleep(3)
                        self.take_screenshot('instagram', 'create_clicked_js')
                except Exception as e3:
                    logger.warning(f"  Method 3 failed: {e3}")
            
            if not create_clicked:
                logger.error("❌ Create button NOT FOUND after all methods!")
                self.take_screenshot('instagram', 'create_button_not_found')
                return {
                    'success': False,
                    'platform': 'instagram',
                    'error': 'Create button not found - please check if logged in'
                }
            
            # STEP 6: Wait for creation dialog
            logger.info("=" * 80)
            logger.info("STEP 6: Wait for Creation Dialog")
            logger.info("=" * 80)

            logger.info("⏳ Waiting for dialog to appear...")
            time.sleep(5)  # Wait longer for dialog to fully load
            self.take_screenshot('instagram', 'creation_dialog_waiting')
            
            # STEP 6.5: Handle Image Upload (Instagram requires at least one image)
            logger.info("=" * 80)
            logger.info("STEP 6.5: Handle Image Upload")
            logger.info("=" * 80)
            
            image_uploaded = False
            
            # Check if we have a real image
            if image_path and os.path.exists(image_path):
                logger.info(f"✅ Image provided: {image_path}")
            else:
                logger.info("ℹ️  No image provided, creating a simple colored background...")
                # Create a simple test image
                try:
                    from PIL import Image, ImageDraw, ImageFont
                    
                    test_image_dir = self.vault_dir / "Instagram_Posts"
                    test_image_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create colored background image
                    width, height = 1080, 1080
                    img = Image.new('RGB', (width, height), color=(99, 102, 241))  # Indigo color
                    draw = ImageDraw.Draw(img)
                    
                    # Add simple text
                    try:
                        font = ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
                    
                    # Draw text in center
                    text = "AI Generated Post"
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    text_x = (width - text_width) // 2
                    text_y = (height - text_height) // 2
                    
                    draw.text((text_x, text_y), text, fill='white', font=font)
                    
                    # Save with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    image_path = str(test_image_dir / f"instagram_post_{timestamp}.png")
                    img.save(image_path)
                    logger.info(f"✅ Test image created: {image_path}")
                except Exception as img_err:
                    logger.warning(f"⚠️  Could not create test image: {img_err}")
                    logger.warning("ℹ️  Will try to skip image upload")
            
            # Upload image if we have one
            if image_path and os.path.exists(image_path):
                logger.info(f"📤 Uploading image: {image_path}")
                
                try:
                    # Find file input
                    file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                    logger.info(f"  Found {len(file_inputs)} file input(s)")
                    
                    if file_inputs:
                        # Send file path to first file input
                        abs_path = os.path.abspath(image_path)
                        logger.info(f"  📁 Sending file: {abs_path}")
                        file_inputs[0].send_keys(abs_path)
                        logger.info("  ✅ File input sent!")
                        
                        # Wait for image to load and process
                        logger.info("  ⏳ Waiting for image processing (10 seconds)...")
                        time.sleep(10)
                        
                        self.take_screenshot('instagram', 'image_uploaded')
                        logger.info("  ✅ Image uploaded successfully!")
                        image_uploaded = True
                        
                        # Check if there's a "Next" button (Instagram multi-step flow)
                        try:
                            logger.info("  🔍 Looking for Next button...")
                            
                            # Method 1: Look for "Next" button by text
                            next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next') or contains(text(), 'next')]")
                            logger.info(f"  Found {len(next_buttons)} Next button(s)")
                            
                            if next_buttons:
                                # Click the last "Next" button (usually the one at bottom)
                                for btn in reversed(next_buttons):
                                    try:
                                        if btn.is_displayed() and btn.is_enabled():
                                            logger.info(f"  ✅ Clicking Next button...")
                                            self.driver.execute_script("arguments[0].click();", btn)
                                            time.sleep(5)  # Wait for next step
                                            self.take_screenshot('instagram', 'after_next_click')
                                            logger.info("  ✅ Next button clicked!")
                                            break
                                    except Exception as btn_err:
                                        logger.debug(f"  Button click error: {btn_err}")
                                        continue
                            else:
                                logger.info("  ℹ️  No Next button found (may be single-step)")
                        except Exception as next_err:
                            logger.warning(f"  ⚠️  Next button search failed: {next_err}")
                    else:
                        logger.warning("  ⚠️  No file input found - image upload may have failed")
                        
                        # Try to find upload area and click it
                        try:
                            upload_areas = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog'] input[type='file']")
                            if upload_areas:
                                logger.info(f"  Found {len(upload_areas)} upload areas")
                                upload_areas[0].send_keys(os.path.abspath(image_path))
                                time.sleep(10)
                                image_uploaded = True
                                self.take_screenshot('instagram', 'image_uploaded_alt')
                                logger.info("  ✅ Image uploaded via alternative method!")
                        except Exception as alt_err:
                            logger.warning(f"  ⚠️  Alternative upload failed: {alt_err}")
                except Exception as upload_err:
                    logger.error(f"  ❌ Image upload failed: {upload_err}")
                    self.take_screenshot('instagram', 'image_upload_error')
            else:
                logger.warning("⚠️  No image available - Instagram may not allow text-only posts")
                logger.info("ℹ️  Will try to continue anyway...")
            
            # Wait for image processing to complete
            if image_uploaded:
                logger.info("⏳ Waiting 3 seconds for UI to stabilize...")
                time.sleep(3)
                self.take_screenshot('instagram', 'before_caption_entry')

            # STEP 7: Enter caption
            logger.info("=" * 80)
            logger.info("STEP 7: Enter Caption")
            logger.info("=" * 80)

            logger.info(f"📝 Caption length: {len(caption)} characters")
            logger.info(f"📝 Caption preview: {caption[:100]}...")

            # Find caption input with multiple methods
            caption_found = False
            
            # Method 1: Instagram's caption textarea (most common)
            try:
                logger.info("Method 1: Looking for textarea in caption area...")
                # Instagram caption is usually in a textarea with specific attributes
                textareas = self.driver.find_elements(By.CSS_SELECTOR, "textarea")
                logger.info(f"  Found {len(textareas)} textarea elements")
                
                for textarea in textareas:
                    try:
                        if textarea.is_displayed():
                            rect = textarea.rect
                            # Caption textarea is usually large and in center
                            if rect['width'] > 100 and rect['height'] > 50:
                                logger.info(f"  ✅ Found caption textarea (size: {rect['width']}x{rect['height']})")
                                textarea.click()
                                time.sleep(1)
                                
                                # Clear using JavaScript (more reliable)
                                self.driver.execute_script("arguments[0].value = '';", textarea)
                                time.sleep(0.5)
                                
                                # Type caption
                                logger.info(f"  ⌨️  Typing caption ({len(caption)} chars)...")
                                textarea.send_keys(caption)
                                time.sleep(2)
                                
                                # Verify
                                actual_text = textarea.get_attribute('value') or textarea.text
                                if actual_text and len(actual_text.strip()) > 10:
                                    logger.info(f"  ✅ Caption verified: {len(actual_text.strip())} chars")
                                    caption_found = True
                                    break
                                else:
                                    logger.warning(f"  ⚠️  Caption verification weak, trying JavaScript...")
                                    # Fallback: Set value via JavaScript
                                    self.driver.execute_script(f"arguments[0].value = arguments[1];", textarea, caption)
                                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", textarea)
                                    time.sleep(1)
                                    caption_found = True
                                    logger.info(f"  ✅ Caption set via JavaScript!")
                                    break
                    except Exception as textarea_err:
                        logger.debug(f"  Textarea error: {textarea_err}")
                        continue
            except Exception as e1:
                logger.warning(f"  Method 1 failed: {e1}")
            
            # Method 2: Contenteditable div (Instagram sometimes uses this)
            if not caption_found:
                try:
                    logger.info("Method 2: Looking for contenteditable div...")
                    editable_divs = self.driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
                    logger.info(f"  Found {len(editable_divs)} contenteditable divs")
                    
                    for div in editable_divs:
                        try:
                            if div.is_displayed():
                                rect = div.rect
                                if rect['width'] > 100 and rect['height'] > 30:
                                    logger.info(f"  ✅ Found caption div (size: {rect['width']}x{rect['height']})")
                                    
                                    # Click to focus
                                    div.click()
                                    time.sleep(1)
                                    
                                    # Clear using JavaScript
                                    self.driver.execute_script("arguments[0].innerHTML = '';", div)
                                    time.sleep(0.5)
                                    
                                    # Type using send_keys
                                    logger.info(f"  ⌨️  Typing caption...")
                                    div.send_keys(caption)
                                    time.sleep(2)
                                    
                                    caption_found = True
                                    logger.info(f"  ✅ Caption entered via div!")
                                    break
                        except Exception as div_err:
                            logger.debug(f"  Div error: {div_err}")
                            continue
                except Exception as e2:
                    logger.warning(f"  Method 2 failed: {e2}")
            
            # Method 3: JavaScript-based caption injection (most reliable fallback)
            if not caption_found:
                try:
                    logger.info("Method 3: JavaScript caption injection...")
                    result = self.driver.execute_script(f"""
                        // Find all textareas and contenteditable divs
                        var textareas = document.querySelectorAll('textarea');
                        var editables = document.querySelectorAll('div[contenteditable="true"]');
                        
                        // Try textareas first
                        for (var i = 0; i < textareas.length; i++) {{
                            var ta = textareas[i];
                            var rect = ta.getBoundingClientRect();
                            if (rect.width > 100 && rect.height > 50) {{
                                ta.value = `{caption}`;
                                ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                console.log('✅ Caption set via JavaScript on textarea');
                                return true;
                            }}
                        }}
                        
                        // Try contenteditable divs
                        for (var i = 0; i < editables.length; i++) {{
                            var ed = editables[i];
                            var rect = ed.getBoundingClientRect();
                            if (rect.width > 100 && rect.height > 30) {{
                                ed.innerText = `{caption}`;
                                ed.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                console.log('✅ Caption set via JavaScript on div');
                                return true;
                            }}
                        }}
                        
                        return false;
                    """)
                    
                    if result:
                        caption_found = True
                        logger.info(f"  ✅ JavaScript caption injection successful!")
                        time.sleep(2)
                    else:
                        logger.warning("  ⚠️  No suitable caption input found via JavaScript")
                except Exception as e3:
                    logger.warning(f"  Method 3 failed: {e3}")
            
            # Method 4: Clipboard paste (ultimate fallback)
            if not caption_found:
                try:
                    logger.info("Method 4: Clipboard paste method...")
                    import pyperclip
                    
                    # Copy caption to clipboard
                    pyperclip.copy(caption)
                    logger.info(f"  📋 Caption copied to clipboard ({len(caption)} chars)")
                    
                    # Find any clickable input area in the dialog
                    clickables = self.driver.find_elements(By.CSS_SELECTOR, "textarea, input[type='text'], div[contenteditable='true']")
                    
                    if clickables:
                        # Click the first visible one
                        for elem in clickables:
                            if elem.is_displayed():
                                elem.click()
                                time.sleep(0.5)
                                
                                # Paste from clipboard (Ctrl+V)
                                from selenium.webdriver.common.keys import Keys
                                elem.send_keys(Keys.CONTROL + 'v')
                                time.sleep(2)
                                
                                caption_found = True
                                logger.info(f"  ✅ Caption pasted via Ctrl+V!")
                                break
                    else:
                        logger.warning("  ⚠️  No input elements found for clipboard paste")
                except ImportError:
                    logger.warning("  ⚠️  pyperclip not installed, skipping clipboard method")
                except Exception as e4:
                    logger.warning(f"  Method 4 failed: {e4}")
            
            # Final status for caption
            if caption_found:
                self.take_screenshot('instagram', 'caption_entered')
                logger.info("✅ STEP 7 COMPLETE: Caption entered successfully!")
            else:
                logger.warning("⚠️  STEP 7: Caption input NOT found after all methods!")
                logger.warning("💡 The post will be created but caption may be empty")
                self.take_screenshot('instagram', 'caption_not_found')
            
            # STEP 8: Share the post
            logger.info("=" * 80)
            logger.info("STEP 8: Share Post")
            logger.info("=" * 80)
            
            share_clicked = False
            
            try:
                # Try multiple methods to find Share button
                share_selectors = [
                    "div[role='dialog'] button[type='submit']",
                    "div[role='dialog'] button:contains('Share')",
                    "div[role='dialog'] div[role='button']:contains('Share')",
                    "//*[text()='Share']",
                    "//*[text()='Post']",
                ]
                
                for selector in share_selectors:
                    try:
                        if selector.startswith('//'):
                            share_btn = self.driver.find_element(By.XPATH, selector)
                        else:
                            share_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                        
                        if share_btn.is_displayed() and share_btn.is_enabled():
                            logger.info(f"  ✅ Found share button, clicking...")
                            self.driver.execute_script("arguments[0].click();", share_btn)
                            share_clicked = True
                            logger.info("✅ Share button clicked!")
                            time.sleep(3)
                            self.take_screenshot('instagram', 'share_clicked')
                            break
                    except:
                        continue
                
                # If not found, try JavaScript
                if not share_clicked:
                    result = self.driver.execute_script("""
                        var buttons = document.querySelectorAll('div[role="dialog"] button, button');
                        for (var btn of buttons) {
                            var text = (btn.innerText || '').toLowerCase();
                            if (text.includes('share') || text.includes('post')) {
                                if (btn.isDisplayed && btn.isDisplayed()) {
                                    btn.click();
                                    return true;
                                }
                            }
                        }
                        return false;
                    """)
                    
                    if result:
                        share_clicked = True
                        logger.info("✅ Share button clicked via JavaScript")
                        time.sleep(3)
                        self.take_screenshot('instagram', 'share_clicked_js')
            
            except Exception as e:
                logger.error(f"❌ Share button failed: {e}")
            
            # STEP 9: Final status
            logger.info("=" * 80)
            logger.info("STEP 9: Final Status")
            logger.info("=" * 80)
            
            if share_clicked:
                logger.info("✅ Instagram post submitted!")
                self.take_screenshot('instagram', 'post_submitted')
                
                return {
                    'success': True,
                    'platform': 'instagram',
                    'message': 'Instagram post submitted successfully',
                    'caption': caption,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning("⚠️  Share button not clicked - post may not be submitted")
                self.take_screenshot('instagram', 'share_not_clicked')
                
                return {
                    'success': False,
                    'platform': 'instagram',
                    'error': 'Could not find or click Share button',
                    'caption': caption
                }

        except Exception as e:
            logger.error(f"❌ Instagram post failed: {str(e)}")
            self.take_screenshot('instagram', 'post_error')
            import traceback
            logger.error(traceback.format_exc())
            
            return {
                'success': False,
                'platform': 'instagram',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

            # Method 1: SVG aria-label="New post" (MOST RELIABLE)
            try:
                logger.info("Method 1: Looking for SVG 'New post' button...")
                svg_buttons = self.driver.find_elements(By.CSS_SELECTOR, "svg[aria-label='New post']")
                logger.info(f"Found {len(svg_buttons)} SVG buttons")

                if svg_buttons:
                    # Click parent of SVG
                    parent = svg_buttons[0].find_element(By.XPATH, "..")
                    self.driver.execute_script("arguments[0].click();", parent)
                    create_clicked = True
                    logger.info("✅ Create button clicked via SVG")
                    time.sleep(3)
                    self.take_screenshot('instagram', 'create_clicked')
            except Exception as e1:
                logger.warning(f"Method 1 failed: {e1}")

            # Method 2: Link to /create/
            if not create_clicked:
                try:
                    logger.info("Method 2: Looking for /create/ link...")
                    create_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href='/create/']")
                    logger.info(f"Found {len(create_links)} create links")

                    if create_links:
                        create_links[0].click()
                        create_clicked = True
                        logger.info("✅ Create button clicked via link")
                        time.sleep(3)
                        self.take_screenshot('instagram', 'create_clicked_link')
                except Exception as e2:
                    logger.warning(f"Method 2 failed: {e2}")

            # Method 3: JavaScript-based detection
            if not create_clicked:
                try:
                    logger.info("Method 3: JavaScript detection...")
                    result = self.driver.execute_script("""
                        // Find all buttons with "new" or "create" text
                        var allButtons = document.querySelectorAll('div[role="button"], button, a[role="menuitem"]');
                        
                        for (var btn of allButtons) {
                            var text = (btn.innerText || btn.textContent || '').toLowerCase();
                            var ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                            var rect = btn.getBoundingClientRect();
                            
                            // Look for "new post", "create", or "+" symbol
                            if ((text.includes('new') && text.includes('post')) ||
                                (text.includes('create')) ||
                                (ariaLabel.includes('new post')) ||
                                text === '+' ||
                                (rect.width > 30 && rect.width < 60 && ariaLabel === '' && text === '')) {
                                
                                // Only click if it's in top navigation (not footer)
                                if (rect.top < 200 && rect.width > 20) {
                                    btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                                    btn.click();
                                    console.log('✅ Create button clicked:', text || ariaLabel);
                                    return true;
                                }
                            }
                        }
                        return false;
                    """)

                    if result:
                        create_clicked = True
                        logger.info("✅ Create button clicked via JavaScript")
                        time.sleep(3)
                        self.take_screenshot('instagram', 'create_clicked_js')
                except Exception as e3:
                    logger.warning(f"Method 3 failed: {e3}")

            if not create_clicked:
                logger.error("❌ Create button click FAILED after all methods")
                self.take_screenshot('instagram', 'create_failed')
                return {
                    'success': False,
                    'platform': 'instagram',
                    'error': 'Create button not found - Instagram UI may have changed'
                }

            # STEP 4: Wait for creation dialog to appear
            logger.info("Waiting for creation dialog...")
            time.sleep(3)

            # STEP 5: Upload image IF provided
            if image_path and os.path.exists(image_path):
                logger.info(f"Uploading image: {image_path}")

                # Wait for file input
                file_inputs = []
                for i in range(10):
                    file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                    if file_inputs:
                        break
                    time.sleep(1)

                if file_inputs:
                    file_inputs[0].send_keys(os.path.abspath(image_path))
                    logger.info("✅ Image uploaded")
                    time.sleep(5)

                    # Click Next (Instagram has multi-step flow)
                    next_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Next')]")
                    if next_buttons:
                        next_buttons[-1].click()
                        logger.info("✅ Next clicked")
                        time.sleep(3)
                else:
                    logger.warning("⚠️ No file input found, skipping image upload")
            else:
                logger.info("ℹ️  No image provided, continuing with text-only post")

            # STEP 6: Enter caption (SAME AS FACEBOOK - using send_keys)
            logger.info("Entering caption using send_keys()...")

            # Find caption input
            caption_input = None
            try:
                # Instagram uses textarea or contenteditable div
                inputs = self.driver.find_elements(By.CSS_SELECTOR, "textarea, div[contenteditable='true']")
                logger.info(f"Found {len(inputs)} potential caption inputs")

                for inp in inputs:
                    try:
                        if inp.is_displayed():
                            caption_input = inp
                            logger.info("✅ Found caption input")
                            break
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Caption input search failed: {e}")

            if caption_input:
                # Clear and enter caption using send_keys (same as Facebook)
                try:
                    caption_input.click()
                    time.sleep(1)

                    # Clear existing
                    try:
                        caption_input.send_keys(Keys.CONTROL + "a")
                        time.sleep(0.5)
                        caption_input.send_keys(Keys.DELETE)
                    except:
                        pass

                    # Enter caption
                    caption_text = caption[:2200]  # Instagram limit
                    logger.info(f"Typing caption ({len(caption_text)} chars)...")
                    caption_input.send_keys(caption_text)
                    time.sleep(2)

                    # Verify
                    actual = caption_input.text
                    if actual and len(actual.strip()) > 10:
                        logger.info(f"✅ Caption verified: {len(actual.strip())} chars")
                    else:
                        logger.warning(f"⚠️ Caption verification weak")

                    self.take_screenshot('instagram', 'caption_entered')
                except Exception as caption_err:
                    logger.warning(f"Caption entry failed: {caption_err}")
            else:
                logger.warning("⚠️ No caption input found - continuing anyway")

            # STEP 7: Click Share button
            logger.info("Looking for Share button...")
            share_clicked = False

            try:
                # Wait a bit for UI to settle
                time.sleep(2)

                # Find Share button
                share_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Share') or contains(text(), 'Post')]")
                logger.info(f"Found {len(share_buttons)} Share/Post buttons")

                for btn in share_buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            text = btn.text.strip()
                            if text in ['Share', 'Post', 'Share now']:
                                self.driver.execute_script("arguments[0].click();", btn)
                                share_clicked = True
                                logger.info(f"✅ Share button clicked: '{text}'")
                                break
                    except:
                        pass
            except Exception as e:
                logger.warning(f"Share button search failed: {e}")

            if share_clicked:
                # Wait for post to complete
                time.sleep(5)
                self.take_screenshot('instagram', 'post_submitted')

                logger.info("✅ Instagram post submitted successfully!")
                return {
                    'success': True,
                    'platform': 'instagram',
                    'message': 'Post submitted successfully',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning("⚠️ Share button not found - post may need manual completion")
                self.take_screenshot('instagram', 'share_not_found')

                # Return partial success
                return {
                    'success': True,
                    'platform': 'instagram',
                    'message': 'Caption entered but Share button not found - you may need to click it manually',
                    'partial': True,
                    'timestamp': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Instagram post failed: {str(e)}")
            self.take_screenshot('instagram', 'post_error')
            return {
                'success': False,
                'platform': 'instagram',
                'error': str(e)
            }

    def login_twitter(self):
        """Login to Twitter/X"""
        if not self.credentials['twitter']['username'] or not self.credentials['twitter']['password']:
            raise Exception("Twitter credentials not configured in .env")

        logger.info("Logging into Twitter/X...")
        self.driver.get('https://twitter.com/login')
        
        try:
            time.sleep(3)
            
            # Enter username/email
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[autocomplete='username']"))
            )
            username_input.send_keys(self.credentials['twitter']['username'])
            
            # Click Next
            next_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' and contains(text(), 'Next')]")
            if next_buttons:
                next_buttons[0].click()
                time.sleep(2)
            
            # Enter password
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_input.send_keys(self.credentials['twitter']['password'])
            
            # Click Log In
            login_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' and contains(text(), 'Log in')]")
            if login_buttons:
                login_buttons[0].click()
                time.sleep(3)
            
            logger.info("Twitter login successful")
            return True
            
        except Exception as e:
            logger.error(f"Twitter login failed: {str(e)}")
            self.take_screenshot('twitter', 'login_error')
            return False

    def post_to_twitter(self, text: str, image_path: str = None) -> dict:
        """
        Post to Twitter/X through browser automation.

        Args:
            text: Tweet text (max 280 characters)
            image_path: Optional path to image file

        Returns:
            dict: Post result
        """
        try:
            if not self.driver:
                self.setup_driver()

            if len(text) > 280:
                return {'success': False, 'error': 'Tweet text must be 280 characters or less'}

            self.login_twitter()
            
            # Navigate to home
            logger.info("Creating tweet...")
            self.driver.get('https://twitter.com/home')
            time.sleep(3)
            
            # Find tweet input
            try:
                tweet_input = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-contents='true']"))
                )
                tweet_input.send_keys(text)
                logger.info("Tweet text entered")
            except Exception as e:
                logger.error(f"Could not find tweet input: {str(e)}")
                return {'success': False, 'error': 'Could not find tweet input field'}

            # Upload image if provided
            if image_path and os.path.exists(image_path):
                logger.info(f"Uploading image: {image_path}")
                try:
                    # Find media upload button
                    media_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' and contains(@aria-label, 'media')]")
                    if media_buttons:
                        media_buttons[0].click()
                        time.sleep(2)
                        
                        # Find file input
                        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        if file_inputs:
                            file_inputs[0].send_keys(os.path.abspath(image_path))
                            time.sleep(3)
                            logger.info("Image uploaded")
                except Exception as e:
                    logger.warning(f"Could not upload image: {str(e)}")

            # Click Post/Tweet button
            post_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button' and contains(text(), 'Post') or contains(text(), 'Tweet')]")
            if post_buttons:
                for btn in reversed(post_buttons):
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        logger.info("Tweet button clicked")
                        break
            
            time.sleep(3)
            self.take_screenshot('twitter', 'post_submitted')
            
            logger.info("Tweet posted successfully")
            return {
                'success': True,
                'platform': 'twitter',
                'message': 'Tweet posted successfully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twitter post failed: {str(e)}")
            self.take_screenshot('twitter', 'post_error')
            return {
                'success': False,
                'platform': 'twitter',
                'error': str(e)
            }

    def login_linkedin(self):
        """Login to LinkedIn"""
        if not self.credentials['linkedin']['email'] or not self.credentials['linkedin']['password']:
            raise Exception("LinkedIn credentials not configured in .env")

        logger.info("Logging into LinkedIn...")
        self.driver.get('https://www.linkedin.com/login')
        
        try:
            time.sleep(3)
            
            # Enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, 'username'))
            )
            email_input.send_keys(self.credentials['linkedin']['email'])
            
            # Enter password
            password_input = self.driver.find_element(By.ID, 'password')
            password_input.send_keys(self.credentials['linkedin']['password'])
            
            # Click Sign In
            sign_in_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            sign_in_btn.click()
            
            time.sleep(5)
            
            # Skip any verification dialogs
            try:
                skip_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Skip')]")
                if skip_btn.is_displayed():
                    skip_btn.click()
                    time.sleep(2)
            except:
                pass
            
            logger.info("LinkedIn login successful")
            return True
            
        except Exception as e:
            logger.error(f"LinkedIn login failed: {str(e)}")
            self.take_screenshot('linkedin', 'login_error')
            return False

    def post_to_linkedin(self, text: str, image_path: str = None) -> dict:
        """
        Post to LinkedIn through browser automation.

        Args:
            text: Post text
            image_path: Optional path to image file

        Returns:
            dict: Post result
        """
        try:
            if not self.driver:
                self.setup_driver()

            self.login_linkedin()
            
            # Navigate to home
            logger.info("Creating LinkedIn post...")
            self.driver.get('https://www.linkedin.com/feed')
            time.sleep(3)
            
            # Click to start post
            try:
                start_post = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Start a post') or contains(text(), 'Share')]"))
                )
                start_post.click()
                time.sleep(2)
            except Exception as e:
                logger.warning(f"Could not find start post button: {str(e)}")

            # Find text area and enter post content
            text_areas = self.driver.find_elements(By.CSS_SELECTOR, "div[contenteditable='true']")
            if text_areas:
                text_areas[0].send_keys(text)
                logger.info("Post text entered")
            else:
                return {'success': False, 'error': 'Could not find post text area'}

            # Upload image if provided
            if image_path and os.path.exists(image_path):
                logger.info(f"Uploading image: {image_path}")
                try:
                    # Find media button
                    media_buttons = self.driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'media') or contains(@aria-label, 'photo')]")
                    if media_buttons:
                        media_buttons[0].click()
                        time.sleep(2)
                        
                        # Find file input
                        file_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
                        if file_inputs:
                            file_inputs[0].send_keys(os.path.abspath(image_path))
                            time.sleep(3)
                            logger.info("Image uploaded")
                except Exception as e:
                    logger.warning(f"Could not upload image: {str(e)}")

            # Click Post button
            post_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Post')]")
            if post_buttons:
                for btn in post_buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        logger.info("Post button clicked")
                        break
            
            time.sleep(3)
            self.take_screenshot('linkedin', 'post_submitted')
            
            logger.info("LinkedIn post submitted successfully")
            return {
                'success': True,
                'platform': 'linkedin',
                'message': 'Post submitted successfully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"LinkedIn post failed: {str(e)}")
            self.take_screenshot('linkedin', 'post_error')
            return {
                'success': False,
                'platform': 'linkedin',
                'error': str(e)
            }

    def send_whatsapp_message(self, phone: str, message: str) -> dict:
        """
        Send WhatsApp message through browser automation.

        Args:
            phone: Phone number with country code (e.g., +1234567890)
            message: Message to send

        Returns:
            dict: Message result
        """
        try:
            if not self.driver:
                self.setup_driver()

            logger.info(f"Sending WhatsApp message to {phone}...")
            
            # Use WhatsApp Web with direct link
            self.driver.get(f'https://web.whatsapp.com')
            time.sleep(5)
            
            # Wait for QR code scan (user needs to scan manually on first login)
            logger.info("Please scan QR code if not already logged in...")
            time.sleep(10)  # Give time for QR scan
            
            # Search for contact
            try:
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='3']"))
                )
                search_box.click()
                search_box.send_keys(phone)
                time.sleep(2)
                
                # Press Enter to select contact
                search_box.send_keys(Keys.RETURN)
                time.sleep(2)
                
                # Type message
                message_box = self.driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                message_box.send_keys(message)
                time.sleep(1)
                
                # Send message
                message_box.send_keys(Keys.RETURN)
                time.sleep(2)
                
                logger.info(f"WhatsApp message sent to {phone}")
                return {
                    'success': True,
                    'platform': 'whatsapp',
                    'recipient': phone,
                    'message': 'Message sent successfully',
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"WhatsApp message failed: {str(e)}")
                self.take_screenshot('whatsapp', 'send_error')
                return {
                    'success': False,
                    'platform': 'whatsapp',
                    'error': str(e)
                }
            
        except Exception as e:
            logger.error(f"WhatsApp automation failed: {str(e)}")
            return {
                'success': False,
                'platform': 'whatsapp',
                'error': str(e)
            }

    def send_gmail_email(self, to: str, subject: str, body: str) -> dict:
        """
        Send email through Gmail browser automation.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            dict: Email result
        """
        try:
            if not self.driver:
                self.setup_driver()

            logger.info(f"Sending Gmail to {to}...")
            self.driver.get('https://mail.google.com')
            time.sleep(3)
            
            # Click Compose
            try:
                compose_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Compose')]"))
                )
                compose_btn.click()
                time.sleep(2)
            except Exception as e:
                logger.error(f"Could not find compose button: {str(e)}")
                return {'success': False, 'error': 'Could not find compose button'}

            # Wait for compose window
            time.sleep(2)
            
            # Find and fill "To" field
            to_fields = self.driver.find_elements(By.CSS_SELECTOR, "textarea[name='to']")
            if to_fields:
                to_fields[0].send_keys(to)
            else:
                return {'success': False, 'error': 'Could not find To field'}

            # Find and fill Subject field
            subject_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[name='subjectbox']")
            if subject_fields:
                subject_fields[0].send_keys(subject)
            else:
                # Try alternative selector
                inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[aria-label]")
                for inp in inputs:
                    if 'subject' in inp.get_attribute('aria-label').lower():
                        inp.send_keys(subject)
                        break

            # Find and fill email body
            body_fields = self.driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Message Body']")
            if body_fields:
                body_fields[0].send_keys(body)
            else:
                return {'success': False, 'error': 'Could not find email body field'}

            time.sleep(2)
            
            # Click Send button
            send_buttons = self.driver.find_elements(By.XPATH, "//div[contains(@aria-label, 'Send') or contains(text(), 'Send')]")
            if send_buttons:
                send_buttons[0].click()
                logger.info("Send button clicked")
            
            time.sleep(3)
            self.take_screenshot('gmail', 'email_sent')
            
            logger.info(f"Gmail sent to {to}")
            return {
                'success': True,
                'platform': 'gmail',
                'recipient': to,
                'subject': subject,
                'message': 'Email sent successfully',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Gmail automation failed: {str(e)}")
            self.take_screenshot('gmail', 'send_error')
            return {
                'success': False,
                'platform': 'gmail',
                'error': str(e)
            }

    def post_to_all(self, message: str, platforms: list = None, image_path: str = None) -> dict:
        """
        Post to all specified platforms.

        Args:
            message: Message to post
            platforms: List of platforms ['facebook', 'instagram', 'twitter', 'linkedin']
            image_path: Optional image path

        Returns:
            dict: Combined results from all platforms
        """
        if platforms is None:
            platforms = ['facebook', 'twitter', 'linkedin']

        results = {
            'success': [],
            'failed': []
        }

        try:
            for platform in platforms:
                logger.info(f"Posting to {platform}...")
                
                if platform == 'facebook':
                    result = self.post_to_facebook(message, image_path)
                elif platform == 'instagram':
                    if not image_path:
                        result = {'success': False, 'platform': 'instagram', 'error': 'Image required for Instagram'}
                    else:
                        result = self.post_to_instagram(message, image_path)
                elif platform == 'twitter':
                    result = self.post_to_twitter(message, image_path)
                elif platform == 'linkedin':
                    result = self.post_to_linkedin(message, image_path)
                else:
                    result = {'success': False, 'platform': platform, 'error': 'Unknown platform'}

                if result.get('success'):
                    results['success'].append(result)
                else:
                    results['failed'].append(result)

        finally:
            self.close_driver()

        return {
            'success': len(results['failed']) == 0,
            'posted_to': len(results['success']),
            'failed_on': len(results['failed']),
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
