# VERCEL DEPLOYMENT GUIDE - Dashboard Frontend

## Prerequisites
- Vercel account (free tier is sufficient)
- GitHub repo already pushed: https://github.com/Aneeq-Ahmed1/Personal_AI_Employee
- Backend API deployed (see `HUGGINGFACE_DEPLOYMENT.md`)

## Step-by-Step Deployment

### Option 1: Vercel CLI (Recommended for first-time setup)

```bash
# Install Vercel CLI globally
npm i -g vercel

# Navigate to dashboard directory
cd dashboard

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Option 2: Vercel Web Dashboard

1. Go to: https://vercel.com/new
2. Import your GitHub repository
3. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `dashboard`
   - **Build Command**: `next build` (default)
   - **Output Directory**: `.next` (default)

4. Set Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-space-name.hf.space
   ```
   (Replace with your actual Hugging Face Spaces URL after backend deployment)

5. Click "Deploy"

## Post-Deployment

1. **Get your Vercel URL**: `https://your-project-name.vercel.app`
2. **Update CORS in backend**: Add this URL to `api_server.py` CORS origins (already configured to accept from env var)
3. **Set environment variable in Vercel**:
   - Go to Vercel Dashboard → Project → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL` = your Hugging Face backend URL
   - Redeploy after setting

## Troubleshooting

### Build fails
- Check Node.js version (Vercel uses Node 18+ by default)
- Verify `dashboard/package.json` has correct build scripts
- Check for TypeScript errors: `cd dashboard && npm run build`

### API connection fails
- Ensure `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Verify backend CORS allows your Vercel domain
- Check browser console for CORS errors

### 404 on refresh
- This is normal for Next.js SPA mode
- Add `vercel.json` in dashboard root if needed:
  ```json
  {
    "rewrites": [{ "source": "/(.*)", "destination": "/" }]
  }
  ```

## Next Steps
After Vercel deployment, proceed to `HUGGINGFACE_DEPLOYMENT.md` for backend setup.
