# Odoo 19 Local Setup Guide for Personal AI Employee

**For:** Windows Users with Odoo 19 installed locally  
**Date:** March 27, 2026  
**Status:** Step-by-step configuration guide

---

## Step 1: Find Your Odoo Admin Credentials

### Option A: Check Your Installation

When you installed Odoo 19 on Windows, you should have set up a master password and admin credentials.

**Check for the credentials file:**

1. Navigate to your Odoo installation folder (typically):
   ```
   C:\Program Files\Odoo 19\
   ```
   OR
   ```
   C:\Users\YourName\AppData\Local\Odoo\
   ```

2. Look for a file called `odoo.conf` or `odoo-server.conf`

3. Open it with Notepad and look for these lines:
   ```ini
   [options]
   admin_passwd = admin  ; This is your master password
   db_host = localhost
   db_port = 8069
   ```

### Option B: Access Odoo Web Interface

1. **Open your browser and go to:**
   ```
   http://localhost:8069
   ```

2. **If you see the Odoo login page:**
   - Click on **"Manage Databases"** or go to: `http://localhost:8069/web/database/manager`
   - You'll be asked for a **Master Password**
   - Try common passwords: `admin`, `admin`, `password`, `odoo`
   - If you don't remember it, see "Reset Master Password" below

3. **If you see a database selection:**
   - Select your database
   - Try logging in with:
     - Email: `admin` or `administrator` or your email
     - Password: `admin` or `password` or what you set during installation

### Option C: Reset Master Password (If You Forgot)

If you can't remember the master password:

1. **Stop the Odoo service:**
   - Press `Win + R`, type `services.msc`, press Enter
   - Find "Odoo" service
   - Right-click → Stop

2. **Edit the config file:**
   - Go to: `C:\Program Files\Odoo 19\server\odoo.conf`
   - OR: `C:\Users\YourName\AppData\Local\Odoo\odoo.conf`
   - Open with Notepad (as Administrator)

3. **Add or update this line:**
   ```ini
   [options]
   admin_passwd = admin123
   ```

4. **Save the file and restart Odoo service**

5. **Now your master password is:** `admin123`

---

## Step 2: Create a Database for AI Employee

### Access Database Manager

1. **Go to:** `http://localhost:8069/web/database/manager`

2. **Enter Master Password** (from Step 1)

3. **Click "Create Database"**

4. **Fill in the form:**
   ```
   Database Name: ai_employee
   Email: your-email@example.com
   Password: (create a password, e.g., AIEmployee@123)
   Language: English (US)
   Country: Pakistan (or your country)
   ```

5. **Click "Create Database"**

6. **Wait for creation** (takes 1-2 minutes)

7. **Login to your new database:**
   - Go to: `http://localhost:8069`
   - Select "ai_employee" database
   - Email: `admin` (or the email you entered)
   - Password: The password you created

---

## Step 3: Enable Developer Mode

Developer mode gives you access to technical settings and API configuration.

1. **Login to Odoo** (http://localhost:8069)

2. **Go to Settings:**
   - Click on **Settings** app (gear icon)

3. **Scroll to bottom** and click **"Activate the developer mode"**

   OR

   - Click on your username (top right)
   - Select **"About"**
   - Click **"Activate the developer mode"**

4. **You'll see a bug icon** (🐛) next to the Settings menu - this means developer mode is active

---

## Step 4: Create API User for AI Employee

For security, create a dedicated user for the AI Employee (don't use your admin account).

1. **Go to Settings → Users & Companies → Users**

2. **Click "Create"**

3. **Fill in the details:**
   ```
   Name: AI Employee
   Email: ai-employee@yourcompany.local
   User Type: Internal User
   ```

4. **Set Access Rights:**
   - Click on "Access Rights" tab
   - **Sales:** User: Own Documents Only (or Manager for full access)
   - **Invoicing:** User: Own Documents Only (or Manager)
   - **Inventory:** User: Own Documents Only (optional)
   
5. **Save**

6. **Set Password:**
   - Click "Action" (top left) → "Change Password"
   - Set password: `AIApiUser@123` (or your choice)
   - Click "Change Password"

7. **Note the credentials:**
   ```
   Database: ai_employee
   Username: ai-employee@yourcompany.local
   Password: AIApiUser@123
   ```

---

## Step 5: Generate API Key (Odoo 19+)

Odoo 19 supports API keys for better security than passwords.

### Option A: Generate API Key (Recommended)

1. **Click on your username** (top right) → **My Profile**

2. **Look for "API Keys" section**

3. **Click "Generate API Key"**

4. **Give it a name:** `AI Employee Integration`

5. **Copy the API Key** (it looks like):
   ```
   a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
   ```

6. **Save it securely** - you won't see it again!

### Option B: Use Password (If API Keys Not Available)

If your Odoo version doesn't show API Keys, use the user password instead.

---

## Step 6: Test Your Odoo Connection

### Test via Browser

1. **Go to:** `http://localhost:8069`
2. **Login with your AI Employee user credentials**
3. **If you can login successfully** - your Odoo is ready!

### Test via Python Script

Create a test file to verify the connection:

```python
# test_odoo_connection.py
import requests
import json

# Your Odoo Configuration
ODOO_URL = "http://localhost:8069"
ODOO_DB = "ai_employee"
ODOO_USERNAME = "ai-employee@yourcompany.local"
ODOO_PASSWORD = "AIApiUser@123"  # Or your API key

# Test connection
url = f"{ODOO_URL}/jsonrpc"

# Authentication payload
auth_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "login",
        "args": [ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD]
    },
    "id": 1
}

try:
    response = requests.post(url, json=auth_payload, timeout=10)
    result = response.json()
    
    if 'result' in result and result['result']:
        print("✅ SUCCESS! Odoo connection working!")
        print(f"User ID: {result['result']}")
    else:
        print("❌ FAILED! Check your credentials")
        print(f"Response: {result}")
        
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
```

**Run the test:**
```bash
python test_odoo_connection.py
```

---

## Step 7: Configure Your .env File

Now update your Personal AI Employee `.env` file:

```bash
# Navigate to your project
cd D:\Aneeq-AI\Personal_AI_Employee

# Open .env file in Notepad
notepad .env
```

**Add these lines:**

```env
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=ai-employee@yourcompany.local
ODOO_PASSWORD=AIApiUser@123
# If you generated an API key, use it here instead:
ODOO_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

**Save and close**

---

## Step 8: Start Odoo MCP Server

Now test the Odoo MCP Server I created for you:

```bash
# Navigate to MCP folder
cd D:\Aneeq-AI\Personal_AI_Employee\silver\mcp

# Start the Odoo MCP Server
python odoo_mcp_server.py
```

**You should see:**
```
Starting Odoo MCP Server...
Odoo URL: http://localhost:8069
Database: ai_employee
Username: ai-employee@yourcompany.local
 * Running on http://0.0.0.0:5001
```

**Test the connection:**

Open your browser and go to:
```
http://localhost:5001/test-connection
```

**Expected response:**
```json
{
  "status": "connected",
  "odoo_url": "http://localhost:8069",
  "database": "ai_employee",
  "message": "Successfully connected to Odoo"
}
```

---

## Step 9: Install Required Apps in Odoo

For full functionality, install these Odoo apps:

1. **Login to Odoo** (http://localhost:8069)

2. **Go to Apps** (puzzle piece icon)

3. **Search and install:**
   - **Invoicing** (for accounting)
   - **Sales** (for sales orders)
   - **Contacts** (for customer management)
   - **Products** (for product catalog)

4. **Click "Install"** for each app

---

## Step 10: Create Sample Data

### Create a Test Customer

1. **Go to Sales → Customers → Create**

2. **Fill in:**
   ```
   Company Name: Test Client
   Email: client@example.com
   Phone: +1234567890
   Address: 123 Test Street, City
   ```

3. **Save**

### Create a Test Product

1. **Go to Sales → Products → Create**

2. **Fill in:**
   ```
   Product Name: Consulting Service
   Product Type: Service
   Sales Price: 100.00
   ```

3. **Save**

### Create a Test Invoice

1. **Go to Invoicing → Customers → Create**

2. **Fill in:**
   - Customer: Select "Test Client"
   - Add a line: Select "Consulting Service", Quantity: 1

3. **Click "Confirm"**

4. **Your invoice is created!**

---

## Troubleshooting

### Issue: Can't Access localhost:8069

**Solution:**
1. Check if Odoo service is running:
   - Press `Win + R`, type `services.msc`
   - Find "Odoo" service
   - If stopped, right-click → Start

2. Check the port:
   - Open `odoo.conf`
   - Look for `http_port = 8069`
   - If different, use that port

### Issue: Login Fails

**Solution:**
1. Verify database name is correct: `ai_employee`
2. Try with `admin` user first
3. Reset password via database manager

### Issue: API Connection Fails

**Solution:**
1. Check Odoo is running: http://localhost:8069
2. Verify credentials in test script
3. Check firewall isn't blocking port 8069
4. Try disabling antivirus temporarily

### Issue: Developer Mode Not Showing

**Solution:**
1. Clear browser cache
2. Logout and login again
3. Go to: http://localhost:8069/web?debug=1

---

## Quick Reference: Your Odoo Credentials

Fill this in once you complete the setup:

```
Odoo URL: http://localhost:8069
Database Name: ai_employee
Master Password: _______________
Admin Email: _______________
Admin Password: _______________

AI Employee User:
Email: ai-employee@yourcompany.local
Password: _______________
API Key: _______________
```

---

## Next Steps After Configuration

1. ✅ Complete Odoo setup (this guide)
2. ✅ Update `.env` file with credentials
3. ✅ Test Odoo MCP Server connection
4. ✅ Run the Gold Tier dashboard
5. ✅ Test creating invoices via API
6. ✅ Integrate with Ralph Wiggum Loop

---

## Additional Resources

- **Odoo 19 Documentation:** https://www.odoo.com/documentation/19.0/
- **Odoo JSON-RPC API Reference:** https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **Odoo Community Forum:** https://www.odoo.com/forum/help-1

---

**Need Help?** Share your specific error message and I'll help you troubleshoot!
