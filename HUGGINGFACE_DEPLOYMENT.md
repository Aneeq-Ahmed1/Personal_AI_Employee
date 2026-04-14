# HUGGING FACE SPACES DEPLOYMENT GUIDE - Dashboard Backend API

## Prerequisites
- Hugging Face account (free tier)
- Docker support enabled in Hugging Face Spaces
- GitHub repo: https://github.com/Aneeq-Ahmed1/Personal_AI_Employee

## Step-by-Step Deployment

### Option 1: Hugging Face Web UI (Recommended)

1. **Create New Space**:
   - Go to: https://huggingface.co/new-space
   - Space name: `personal-ai-employee-api` (or your preferred name)
   - License: MIT (or your preference)
   - **Select "Docker" as Space SDK** (IMPORTANT!)
   - Visibility: Public (free) or Private

2. **Connect GitHub Repository**:
   - In your new Space, go to "Files and versions"
   - Click "Import from GitHub"
   - Select: `Aneeq-Ahmed1/Personal_AI_Employee`
   - Set the following in `huggingface.yaml`:
     ```yaml
     app_file: api_server.py
     python_version: 3.12
     build_command: pip install -r requirements.txt
     run_command: uvicorn api_server:app --host 0.0.0.0 --port 8000
     ```

3. **Configure Dockerfile**:
   - The space will use `Dockerfile.huggingface` from your repo
   - This Dockerfile:
     - Uses Python 3.12 slim image
     - Installs dependencies from `requirements.txt`
     - Copies `api_server.py` and runs with uvicorn on port 8000

4. **Set Environment Variables**:
   - In your Space, go to "Settings" → "Variables and Secrets"
   - Add these variables:
     ```
     FRONTEND_URL=https://your-project.vercel.app
     GMAIL_CLIENT_ID=your_gmail_client_id
     GMAIL_CLIENT_SECRET=your_gmail_client_secret
     GMAIL_REFRESH_TOKEN=your_gmail_refresh_token
     OPENROUTER_API_KEY=your_openrouter_api_key
     ODOO_URL=http://localhost:8069
     ODOO_DB=your_odoo_db
     ODOO_USERNAME=your_odoo_username
     ODOO_PASSWORD=your_odoo_password
     ```

5. **Deploy**:
   - Click "Restart Space" after configuring
   - Space will build and deploy automatically
   - Your API will be available at: `https://your-username-personal-ai-employee-api.hf.space`

### Option 2: Hugging Face Hub CLI

```bash
# Install Hugging Face Hub CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Create space repository
huggingface-cli repo create your-username/personal-ai-employee-api

# Clone and deploy
git clone https://huggingface.co/spaces/your-username/personal-ai-employee-api
cd personal-ai-employee-api

# Copy deployment files from your project
cp ../D:\Aneeq-AI\Personal_AI_Employee\Dockerfile.huggingface Dockerfile
cp ../D:\Aneeq-AI\Personal_AI_Employee\huggingface.yaml huggingface.yaml
cp -r ../D:\Aneeq-AI\Personal_AI_Employee\silver_gold_platinum\skills\dashboard-api\* .

# Commit and push
git add .
git commit -m "Deploy Personal AI Employee API"
git push
```

## Post-Deployment

1. **Test your API endpoint**:
   ```bash
   curl https://your-username-personal-ai-employee-api.hf.space/api/health
   ```

2. **Update Vercel Frontend**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Update `NEXT_PUBLIC_API_URL` to your Hugging Face Space URL
   - Redeploy Vercel app

3. **Verify CORS**:
   - The API should already allow your Vercel domain (configured in api_server.py)
   - Test from browser console to ensure no CORS errors

## Monitoring

- Check Space logs: https://huggingface.co/spaces/your-username/personal-ai-employee-api?logs=container
- Monitor API errors in the logs
- Check rate limits (Hugging Face free tier has limitations)

## Troubleshooting

### Space won't start
- Check Docker build logs
- Verify `Dockerfile.huggingface` is in repo root
- Ensure `requirements.txt` path is correct

### API returns 500 errors
- Check environment variables are set correctly
- Verify external service credentials (Gmail, OpenRouter, Odoo)
- Check Space container logs

### CORS errors from frontend
- Ensure `FRONTEND_URL` env var matches your Vercel URL
- Restart the Space after changing env vars

## Next Steps
After both deployments are complete:
1. Test end-to-end functionality from Vercel URL
2. Set up monitoring/alerting for both services
3. Configure custom domain (optional, paid feature)
4. Share the live URL with users!
