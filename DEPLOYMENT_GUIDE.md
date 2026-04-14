# 🚀 Deployment Guide - GitHub + Vercel

## ✅ Pre-Push Verification (COMPLETE)

### Credentials Status:
- ✅ `.env` file DELETED (contains real API keys)
- ✅ `credentials.json` DELETED (Gmail OAuth)
- ✅ `token.pickle` DELETED (Gmail tokens)
- ✅ `.gitignore` properly configured
- ✅ `.env.example` created as template

### Files Safe to Push:
- ✅ No hardcoded API keys in Python files
- ✅ No hardcoded API keys in TypeScript/JavaScript files
- ✅ No credentials in markdown files
- ✅ Test files deleted
- ✅ Log files ignored

---

## 📦 Step 1: Push to GitHub

```bash
# Navigate to project
cd D:\Aneeq-AI\Personal_AI_Employee

# Initialize git (if not done)
git init

# Add all files
git add .

# Check what will be committed
git status

# Commit
git commit -m "feat: Personal AI Employee - Complete Multi-Tier System

- Bronze/Silver/Gold/Platinum Tiers
- Email/WhatsApp/LinkedIn/Filesystem Watchers
- Browser Automation (Facebook/Instagram/Twitter)
- Dashboard (Next.js 15 + FastAPI)
- Human-in-the-Loop Approval Workflow
- Cloud + Local Agent Architecture
"

# Create GitHub repo first, then:
git remote add origin https://github.com/YOUR_USERNAME/personal-ai-employee.git
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Deploy Frontend to Vercel

### Option A: Vercel Dashboard (Easiest)

1. Go to https://vercel.com
2. Click **"New Project"**
3. Import your GitHub repo
4. Configure:
   - **Root Directory:** `dashboard`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`
5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_URL:8000
   ```
6. Click **Deploy**

### Option B: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from dashboard folder
cd D:\Aneeq-AI\Personal_AI_Employee\dashboard
vercel

# Follow prompts
# - Set up and deploy? Y
# - Which scope? (select your account)
# - Link to existing project? N
# - Project name: personal-ai-employee
# - Directory: ./
# - Override settings? N

# Production deploy
vercel --prod
```

---

## 🔧 Step 3: Deploy Backend API (FastAPI)

Vercel sirf **frontend** (static files) host karta hai. Backend API ke liye options:

### Option 1: Railway (Recommended - Free)
1. Go to https://railway.app
2. Create new project
3. Deploy from GitHub
4. Set environment variables:
   ```
   GEMINI_API_KEY=your_key
   OPENROUTER_API_KEY=your_key
   EMAIL_ADDRESS=your_email
   EMAIL_PASSWORD=your_app_password
   ```
5. Railway will give you backend URL: `https://your-app.railway.app`

### Option 2: Render (Free)
1. Go to https://render.com
2. New Web Service
3. Connect GitHub repo
4. Root Directory: `silver_gold_platinum/skills/dashboard-api`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

### Option 3: Keep Local (Development Only)
Agar sirf testing ke liye chahiye:
```bash
# Start local API
cd D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum\skills\dashboard-api
python api_server.py
```

Then update Vercel env variable:
```
NEXT_PUBLIC_API_URL=http://YOUR_LOCAL_IP:8000
```

---

## 🔗 Step 4: Connect Frontend + Backend

### In Vercel Dashboard:
1. Go to **Settings → Environment Variables**
2. Add:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app/ws
   ```
3. Redeploy

### In `dashboard/.env.production` (Alternative):
```env
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
NEXT_PUBLIC_WS_URL=wss://your-backend.railway.app/ws
```

---

## ⚠️ Important Notes

### 1. **Never Commit `.env`**
```bash
# Always check before push
git ls-files | grep ".env"
# Should only show: .env.example
```

### 2. **CORS Issues**
Backend mein CORS allow karna hoga for Vercel domain:
```python
# In api_server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://personal-ai-employee.vercel.app"],  # Your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. **WebSocket Connection**
Vercel se WebSocket ke liye `wss://` use karna hoga (not `ws://`)

### 4. **API Keys Management**
Backend (Railway/Render) mein set karein:
- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY`
- `EMAIL_ADDRESS`
- `EMAIL_PASSWORD`
- `TWILIO_*` (for WhatsApp)
- `LINKEDIN_*` (for LinkedIn)

Frontend (Vercel) mein sirf:
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_WS_URL`

---

## 🎯 Quick Deploy Checklist

- [ ] `.env` file deleted
- [ ] `credentials.json` deleted
- [ ] `token.pickle` deleted
- [ ] `.gitignore` configured
- [ ] `.env.example` created
- [ ] GitHub repo created
- [ ] Files pushed to GitHub
- [ ] Vercel account created
- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway/Render
- [ ] Environment variables set in both
- [ ] CORS configured in backend
- [ ] Frontend connected to backend
- [ ] Tested dashboard URL

---

## 🆘 Troubleshooting

### Dashboard shows blank page?
```bash
cd dashboard
npm install
npm run build
# Check for errors
```

### API not connecting?
1. Check CORS settings
2. Verify `NEXT_PUBLIC_API_URL` is correct
3. Check backend is running

### WebSocket not connecting?
1. Use `wss://` not `ws://` for production
2. Check firewall settings
3. Verify backend supports WebSocket

### API keys leak?
**IMMEDIATE ACTION:**
1. Revoke all exposed keys
2. Generate new keys
3. Update `.env` (never commit)
4. Push commit with new `.gitignore`

---

## 📚 Resources

- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Next.js Deployment: https://nextjs.org/docs/app/building-your-application/deploying

---

**Need Help?** Create an issue on GitHub!
