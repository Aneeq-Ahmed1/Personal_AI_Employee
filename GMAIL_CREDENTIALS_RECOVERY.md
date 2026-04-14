# 🔐 Gmail Credentials Recovery Guide

## `credentials.json` File Kaise Milegi:

### **Option 1: Google Cloud Console Se Download Karo**

1. **Google Cloud Console** jao: https://console.cloud.google.com
2. Apna project select karo (jahan se Gmail API enable kiya tha)
3. **APIs & Services → Credentials** jao
4. **OAuth 2.0 Client ID** download karo
5. File ko `credentials.json` rename karo
6. Is folder mein paste karo:
   ```
   D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum\credentials.json
   ```

### **Option 2: Agar Pehle Download Kiya Tha**

Check these locations:
- `Downloads/` folder
- `Desktop/`
- Email attachments (agar Google ne email kiya tha)
- Old backups

### **Steps to Create New OAuth Credentials:**

1. **Google Cloud Console** → https://console.cloud.google.com
2. New project create karo ya existing select karo
3. **Gmail API** enable karo
4. **OAuth consent screen** configure karo
5. **Credentials → Create Credentials → OAuth Client ID**
6. Application type: **Desktop app**
7. Download JSON file
8. Rename to `credentials.json`
9. Move to: `D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum\`

---

## `token.pickle` File Kaise Milegi:

**Good News:** `token.pickle` file **automatically generate** hogi jab aap Gmail auth run karoge!

### **Steps:**

1. `credentials.json` file place karo (upar se)
2. Gmail auth script run karo:
   ```bash
   cd D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum
   python watchers/gmail_watcher.py
   ```
3. Browser open hoga - Google se login karo
4. Permissions allow karo
5. `token.pickle` file automatically create ho jayegi!

### **Alternative - Test Gmail Auth:**

```bash
cd D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum
python -c "from google.oauth2.credentials import Credentials; print('Gmail auth ready')"
```

---

## Quick Fix Commands:

```bash
# Check if credentials.json exists
dir "D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum\credentials.json"

# Check if token.pickle exists
dir "D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum\token.pickle"

# If missing, download credentials.json from Google Cloud Console
# Then run Gmail watcher to auto-generate token.pickle
```

---

## ⚠️ Important:

- **`credentials.json`** = Google se download karna padega (one-time)
- **`token.pickle`** = Automatically ban jayega jab first time Gmail run karoge
- Dono files `.gitignore` mein hain - GitHub pe **NAHI** jayengi ✅

---

**Need Help?** Check `silver_gold_platinum/watchers/gmail_watcher.py` for auth code!
