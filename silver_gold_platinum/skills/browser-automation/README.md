# 🤖 Browser Automation Skill

**Gold Tier Feature - No API Keys Required!**

This skill uses Selenium WebDriver to automate social media posting, messaging, and email directly through browser automation. No API keys, no phone verification, no quotas!

---

## 🚀 Features

### Social Media Posting
- **Facebook** - Post text and images to your profile/page
- **Instagram** - Post images with captions (requires image file)
- **Twitter/X** - Post tweets (max 280 characters)
- **LinkedIn** - Post updates to your profile/company page

### Messaging
- **WhatsApp** - Send direct messages via WhatsApp Web
- **Gmail** - Send emails through Gmail web interface

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install selenium webdriver-manager
```

### 2. Configure Credentials

Add your login credentials to `.env` file:

```env
# Facebook
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password

# Instagram
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# Twitter/X
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password

# LinkedIn
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Gmail (optional - uses main EMAIL if not set)
GMAIL_EMAIL=your_email@gmail.com
GMAIL_PASSWORD=your_app_password

# WhatsApp (no credentials needed - uses QR code)
```

---

## 🎯 Usage

### Python API

```python
from silver.skills.browser_automation.browser_poster import BrowserSocialPoster

# Initialize poster
poster = BrowserSocialPoster(headless=False)

# Post to multiple platforms
result = poster.post_to_all(
    message="Hello from Browser Automation!",
    platforms=['facebook', 'twitter', 'linkedin'],
    image_path="C:/path/to/image.jpg"  # Optional, required for Instagram
)

print(result)

# Post to single platform
facebook_result = poster.post_to_facebook(
    message="Facebook post!",
    image_path="C:/path/to/image.jpg"
)

# Send WhatsApp message
whatsapp_result = poster.send_whatsapp_message(
    phone="+1234567890",
    message="Hello from AI Employee!"
)

# Send Gmail email
gmail_result = poster.send_gmail_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email sent via browser automation."
)

# Close browser
poster.close_driver()
```

### REST API (via Dashboard API)

#### Post to Social Media

```bash
curl -X POST http://localhost:8000/api/browser-automation/post \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello from Browser Automation!",
    "platforms": ["facebook", "twitter", "linkedin"],
    "image_path": "C:/path/to/image.jpg"
  }'
```

#### Post to Single Platform

```bash
curl -X POST http://localhost:8000/api/browser-automation/post/facebook \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Facebook post!",
    "image_path": "C:/path/to/image.jpg"
  }'
```

#### Send WhatsApp Message

```bash
curl -X POST http://localhost:8000/api/browser-automation/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+1234567890",
    "message": "Hello from AI Employee!"
  }'
```

#### Send Gmail Email

```bash
curl -X POST http://localhost:8000/api/browser-automation/gmail \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test Email",
    "body": "This is a test email."
  }'
```

---

## 🌐 Dashboard UI

Access the Browser Automation dashboard at:

```
http://localhost:3000/browser-automation
```

Features:
- ✅ Visual platform status indicators
- ✅ Multi-platform post composer
- ✅ WhatsApp message sender
- ✅ Gmail email composer
- ✅ Real-time results display
- ✅ Image upload support

---

## ⚠️ Important Notes

### First-Time Setup

1. **WhatsApp Web**: First time use requires manual QR code scan
   - Open WhatsApp on your phone
   - Go to Settings > Linked Devices
   - Scan the QR code shown in browser

2. **Two-Factor Authentication**: If you have 2FA enabled:
   - You may need to approve the login manually
   - Consider using app-specific passwords

3. **Browser Detection**: Some platforms may detect automated browsers
   - The script uses stealth mode to avoid detection
   - If issues occur, try running in non-headless mode

### Best Practices

1. **Rate Limiting**: Don't post too frequently
   - Wait at least 1-2 minutes between posts
   - Respect platform limits

2. **Image Requirements**:
   - Facebook: JPG, PNG (max 15MB)
   - Instagram: Square images work best (1080x1080)
   - Twitter: JPG, PNG, GIF (max 5MB)
   - LinkedIn: JPG, PNG (max 5MB)

3. **Character Limits**:
   - Twitter: 280 characters
   - LinkedIn: 3,000 characters
   - Facebook: 63,206 characters
   - Instagram: 2,200 characters

### Security

- **Never commit `.env` file** with real credentials
- Use **app-specific passwords** when possible
- Store credentials securely
- Enable two-factor authentication on all accounts

---

## 🐛 Troubleshooting

### "ChromeDriver not found"

```bash
pip install --upgrade webdriver-manager
```

### "Login failed" errors

1. Check credentials in `.env`
2. Try logging in manually to verify credentials
3. Some platforms may require CAPTCHA solving
4. Wait a few minutes and try again

### "Element not found" errors

- Platform UI may have changed
- Try running in non-headless mode to see what's happening
- Check screenshots in `vault/Browser_Automation_Screenshots/`

### WhatsApp QR Code not appearing

1. Clear browser cache
2. Restart the automation
3. Make sure you're not already logged in on another device

---

## 📁 Directory Structure

```
silver/skills/browser-automation/
├── __init__.py
├── browser_poster.py      # Main automation logic
└── README.md              # This file
```

### Generated Directories

```
silver/vault/
├── Browser_Automation_Screenshots/  # Debug screenshots
└── Browser_Automation_History/      # Post history (future)
```

---

## 🔧 Advanced Configuration

### Headless Mode

Run browser without GUI (faster, but less reliable):

```python
poster = BrowserSocialPoster(headless=True)
```

### Custom Timeouts

Modify in `browser_poster.py`:

```python
self.wait = WebDriverWait(self.driver, timeout=30)  # Change timeout
```

### Screenshots

Screenshots are automatically saved for debugging:

```
silver/vault/Browser_Automation_Screenshots/
├── facebook_login_error_20260329_143022.png
├── twitter_post_submitted_20260329_143145.png
└── whatsapp_send_error_20260329_143312.png
```

---

## 🎓 Example Use Cases

### 1. Cross-Platform Marketing Campaign

```python
# Post same message to all platforms
poster.post_to_all(
    message="🎉 New Product Launch! Check out our latest innovation.",
    platforms=['facebook', 'twitter', 'linkedin', 'instagram'],
    image_path="C:/marketing/product_launch.jpg"
)
```

### 2. Automated WhatsApp Notifications

```python
# Send appointment reminders
poster.send_whatsapp_message(
    phone="+1234567890",
    message="Reminder: Your appointment is tomorrow at 10 AM."
)
```

### 3. Email Newsletter

```python
# Send personalized emails
poster.send_gmail_email(
    to="client@example.com",
    subject="Monthly Update - March 2026",
    body="Dear Client,\n\nHere's your monthly update..."
)
```

---

## 📝 License

Part of the Personal AI Employee project - Gold Tier feature.

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review screenshots in vault directory
3. Check API logs in dashboard
4. Verify credentials are correct

---

**🎉 Happy Automating!**
