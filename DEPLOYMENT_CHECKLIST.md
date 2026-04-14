# DEPLOYMENT CHECKLIST - Personal AI Employee

## ✅ Pre-Deployment Verification (COMPLETE)

- [x] Files committed to GitHub:
  - [x] `Dockerfile.huggingface`
  - [x] `huggingface.yaml`
  - [x] `api_server.py` (with CORS fix)
  
- [x] Dashboard builds successfully (Next.js 15.5.14)
- [x] No TypeScript errors
- [x] No build errors
- [x] Git working tree clean

---

## 🚀 Deployment Steps

### Step 1: Deploy Backend to Hugging Face Spaces

**Actions:**
1. Go to: https://huggingface.co/new-space
2. Create Space with these settings:
   - **Name**: `personal-ai-employee-api`
   - **SDK**: Docker (IMPORTANT!)
   - **Visibility**: Public (free tier)
   
3. Import from GitHub:
   - Repo: `Aneeq-Ahmed1/Personal_AI_Employee`
   - The Space will use `Dockerfile.huggingface` and `huggingface.yaml`

4. Set Environment Variables in Space Settings:
   ```
   FRONTEND_URL=https://your-project.vercel.app (set after Step 2)
   GMAIL_CLIENT_ID=your_client_id
   GMAIL_CLIENT_SECRET=your_client_secret
   GMAIL_REFRESH_TOKEN=your_refresh_token
   OPENROUTER_API_KEY=your_openrouter_key
   ```

5. Restart Space and wait for deployment (~2-5 minutes)

6. Test API health check:
   ```
   curl https://your-username-personal-ai-employee-api.hf.space/api/health
   ```

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete

**Backend URL:** `https://__________.hf.space` (fill in after deployment)

---

### Step 2: Deploy Frontend to Vercel

**Option A: Using Script (Recommended)**
```bash
deploy_to_vercel.bat
```

**Option B: Manual CLI**
```bash
cd dashboard
vercel login
vercel --prod
```

**Option C: Web Dashboard**
1. Go to: https://vercel.com/new
2. Import GitHub repo: `Aneeq-Ahmed1/Personal_AI_Employee`
3. Configure:
   - **Root Directory**: `dashboard`
   - **Framework**: Next.js
   - **Build Command**: `next build` (default)

4. Set Environment Variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-username-personal-ai-employee-api.hf.space
   ```

5. Deploy and get URL:
   ```
   https://__________.vercel.app (fill in after deployment)
   ```

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete

**Frontend URL:** `https://__________.vercel.app` (fill in after deployment)

---

### Step 3: Connect Frontend ↔ Backend

**Actions:**
1. Copy Backend URL from Step 1
2. In Vercel Dashboard → Your Project → Settings → Environment Variables
3. Set: `NEXT_PUBLIC_API_URL` = `https://your-username-personal-ai-employee-api.hf.space`
4. Redeploy Vercel app (Vercel will auto-redeploy on env var change)

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Step 4: Update Backend CORS

**Actions:**
1. In Hugging Face Space → Settings → Variables and Secrets
2. Set: `FRONTEND_URL` = `https://your-project.vercel.app`
3. Restart Space

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Step 5: End-to-End Testing

**Test from Vercel URL:**
- [ ] Dashboard loads at `https://your-project.vercel.app`
- [ ] Stats card shows data (Inbox, Needs Action, Completed, Plans)
- [ ] Tasks list populates
- [ ] Activity feed shows recent events
- [ ] Approve/Reject buttons work
- [ ] Browser automation tab works
- [ ] Gold Tier features visible
- [ ] Platinum Tier status shows correctly

**Test API directly:**
- [ ] `https://your-space.hf.space/api/health` returns 200
- [ ] `https://your-space.hf.space/api/tasks` returns task list
- [ ] `https://your-space.hf.space/api/stats` returns statistics

**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

## 🎯 Post-Deployment

### Monitoring
- [ ] Set up Hugging Face Space monitoring
- [ ] Set up Vercel analytics
- [ ] Check logs for errors

### Documentation
- [ ] Update README.md with live URLs
- [ ] Share deployment URLs with team
- [ ] Create user guide

### Optional Enhancements
- [ ] Custom domain for Vercel (paid)
- [ ] Custom domain for Hugging Face Space (paid)
- [ ] Set up CI/CD pipeline
- [ ] Add rate limiting to API

---

## 📞 Troubleshooting

### Dashboard shows blank page
- Check browser console for errors
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Redeploy Vercel app

### API returns 500 errors
- Check Hugging Face Space logs
- Verify all environment variables are set
- Check external service credentials

### CORS errors
- Ensure both FRONTEND_URL and CORS origins match
- Restart both services after changing URLs
- Check browser console for specific CORS messages

### Build failures
- Frontend: `cd dashboard && npm run build` (test locally first)
- Backend: Check `Dockerfile.huggingface` and `requirements.txt` paths

---

## 📊 Deployment Timeline

| Step | Estimated Time | Actual Time |
|------|---------------|-------------|
| Backend (Hugging Face) | 10-15 min | _____ min |
| Frontend (Vercel) | 5-10 min | _____ min |
| Connection & Testing | 10 min | _____ min |
| **Total** | **25-35 min** | _____ min |

---

## ✅ Final Verification

When all steps are complete:
- [ ] Both services deployed and running
- [ ] Frontend ↔ Backend communication working
- [ ] No console errors in browser
- [ ] All features accessible from Vercel URL
- [ ] Deployment checklist fully complete

**Deployment Date:** ____________  
**Deployed By:** ____________  
**Notes:** ____________
