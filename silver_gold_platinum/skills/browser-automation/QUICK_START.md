# 🚀 Browser Automation - Quick Start Guide

**Get started with browser automation in 5 minutes!**

---

## ⚡ Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install selenium webdriver-manager
```

### Step 2: Configure Credentials

Open `.env` file and add your social media credentials:

```env
# Facebook
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password

# Twitter/X
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password

# LinkedIn
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Instagram (optional - requires image)
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Gmail (optional - uses main EMAIL if not set)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password
```

> ⚠️ **Security Tip**: Use app-specific passwords when possible!

### Step 3: Start Services

```bash
# Terminal 1: Start Dashboard API
cd silver/skills/dashboard-api
python api_server.py

# Terminal 2: Start Dashboard (optional - for UI)
cd dashboard
npm run dev
```

---

## 🎯 Usage Options

### Option A: Dashboard UI (Easiest)

1. Open browser: `http://localhost:3000/browser-automation`
2. Click **Social Media Post** tab
3. Type your message
4. Select platforms (Facebook, Twitter, LinkedIn)
5. Click **🚀 Post to Social Media**
6. Watch the results appear in real-time!

### Option B: Python Script

Create a file `post_to_social.py`:

```python
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent / "silver" / "skills"))

from browser_automation.browser_poster import BrowserSocialPoster

# Initialize
poster = BrowserSocialPoster(headless=False)

# Post to multiple platforms
result = poster.post_to_all(
    message="Hello from Browser Automation! 🎉",
    platforms=['facebook', 'twitter', 'linkedin'],
    image_path=None  # Optional: "C:/path/to/image.jpg"
)

print(f"Posted to {result['posted_to']} platforms")
print(f"Success: {result['success']}")

# Close browser
poster.close_driver()
```

Run it:
```bash
python post_to_social.py
```

### Option C: REST API

```bash
curl -X POST http://localhost:8000/api/browser-automation/post ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Hello from AI Employee!\", \"platforms\": [\"facebook\", \"twitter\"]}"
```

---

## 📱 Platform-Specific Examples

### Facebook Post

```python
poster.post_to_facebook(
    message="Check out our new product! 🚀",
    image_path="C:/images/product.jpg"  # Optional
)
```

### Twitter/X Post

```python
poster.post_to_twitter(
    text="Exciting news! Stay tuned... 🎯",
    image_path=None  # Optional
)
```

### LinkedIn Post

```python
poster.post_to_linkedin(
    text="Thrilled to announce our latest achievement! 💼",
    image_path=None  # Optional
)
```

### Instagram Post (Requires Image)

```python
poster.post_to_instagram(
    caption="Beautiful day for a post! 📷 #Instagram",
    image_path="C:/images/photo.jpg"  # Required
)
```

### WhatsApp Message

```python
poster.send_whatsapp_message(
    phone="+1234567890",
    message="Hello! This is an automated message."
)
```

### Gmail Email

```python
poster.send_gmail_email(
    to="client@example.com",
    subject="Meeting Reminder",
    body="Hi,\n\nJust reminding you about our meeting tomorrow at 10 AM.\n\nBest regards"
)
```

---

## ✅ Test Your Setup

Run the test script:

```bash
python silver\skills\browser-automation\test_browser_automation.py
```

Expected output:
```
✅ Browser poster initialized successfully
✅ Facebook post successful
⚠️  Some tests may be skipped due to missing credentials
```

---

## 🐛 Troubleshooting

### Problem: "Module not found"

**Solution**: Make sure Selenium is installed:
```bash
pip install selenium webdriver-manager
```

### Problem: "Login failed"

**Solutions**:
1. Check credentials in `.env`
2. Try logging in manually to verify they work
3. Some platforms may require CAPTCHA solving

### Problem: "ChromeDriver not found"

**Solution**: Install webdriver-manager:
```bash
pip install --upgrade webdriver-manager
```

### Problem: WhatsApp QR Code not appearing

**Solution**:
1. Open WhatsApp on your phone
2. Go to Settings > Linked Devices
3. Scan the QR code when it appears
4. Wait up to 30 seconds

---

## 📊 Dashboard UI Features

Access at: `http://localhost:3000/browser-automation`

### Features:
- ✅ Platform status indicators (shows which platforms are configured)
- ✅ Multi-platform post composer
- ✅ Character counter for Twitter
- ✅ Platform selection checkboxes
- ✅ Image path input (for Instagram)
- ✅ Real-time results display
- ✅ WhatsApp message sender
- ✅ Gmail email composer

---

## 🎓 Pro Tips

1. **First Run**: Run in non-headless mode to see what's happening
   ```python
   poster = BrowserSocialPoster(headless=False)
   ```

2. **Screenshots**: Check debug screenshots in:
   ```
   silver/vault/Browser_Automation_Screenshots/
   ```

3. **Rate Limiting**: Wait 1-2 minutes between posts to avoid detection

4. **Images**: Use square images (1080x1080) for best Instagram results

5. **Testing**: Test with dummy accounts first before using real accounts

---

## 📚 Additional Resources

- **Full Documentation**: `silver/skills/browser-automation/README.md`
- **Implementation Details**: `BROWSER_AUTOMATION_COMPLETE.md`
- **Test Suite**: `silver/skills/browser-automation/test_browser_automation.py`

---

## 🆘 Need Help?

1. Check the full README in `silver/skills/browser-automation/`
2. Review the troubleshooting section above
3. Check screenshots in vault directory
4. Verify credentials are correct in `.env`

---

**🎉 You're ready to automate!**

Start posting to social media without API keys, phone verification, or quotas!

---
