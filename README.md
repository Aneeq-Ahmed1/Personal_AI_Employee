# Personal AI Employee 🤖

A multi-tier AI employee that automates email monitoring, social media posting, document processing, and business workflows - with human-in-the-loop approval system.

## 🏗️ Architecture

This project implements a **tiered architecture** with increasing levels of functionality:

### **Bronze Tier** - Basic File Watcher
- File system monitoring and triage
- Basic task execution
- Foundation layer for higher tiers

### **Silver Tier** - Email + Social Media Integration
- **4 Watchers:** Gmail, WhatsApp, LinkedIn, Filesystem
- **AI Reasoning Engine** with auto-failover (Gemini → OpenRouter)
- **Human-in-the-Loop Approval Workflow** (email + dashboard notifications)
- **10 Agent Skills:** email-send, file-triage, reasoning-engine, browser-automation, etc.
- **MCP Server** (port 8000)
- **Dashboard** (Next.js 15 on port 3000 + FastAPI backend)
- **Task Scheduling** (Windows Task Scheduler integration)

### **Gold Tier** - Browser Automation + Odoo Integration
- **Browser Automation** (Selenium) for social media posting:
  - Facebook, Instagram, Twitter/X, LinkedIn
  - No API keys required - uses real browser sessions
- **Odoo MCP Server** for business operations (port 5001)
- **Social Media MCP Server** (port 5002)
- **Ralph Wiggum Loop** - autonomous multi-step task execution
- **CEO Briefing Generator**
- **Audit Logging** system

### **Platinum Tier** - Always-On Cloud + Local Executive
- **Two-Agent Architecture:**
  - **Cloud Agent** (draft-only, 24/7 monitoring)
  - **Local Agent** (final actions with approval)
- **Vault Sync** with Git-based coordination
- **Claim-by-Move** workflow for task management
- **End-to-End Flow:** Email → Cloud Draft → Local Approval → Final Send → Done

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (3.14 has WhatsApp compatibility issues)
- Node.js 18+ (for Dashboard)
- Google Gemini API key (or OpenRouter key)
- Gmail App Password (for email sending)

### 1. Setup
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/personal-ai-employee.git
cd personal-ai-employee

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your credentials
```

### 2. Start All Tiers
```bash
# Start Silver Tier (Watchers + Dashboard)
start_silver_tier.bat

# Start Gold Tier (Browser Automation + Odoo)
start_gold_tier.bat

# Start Platinum Tier (Cloud + Local Agents)
start_platinum_all.bat
```

### 3. Access Dashboard
- **Dashboard:** http://localhost:3000
- **API Server:** http://localhost:8000
- **MCP Servers:** Ports 5000, 5001, 5002

## 📁 Project Structure

```
Personal_AI_Employee/
├── bronze/                    # Bronze Tier (Basic)
│   ├── skills/
│   ├── vault/
│   └── watcher.py
├── silver_gold_platinum/      # Silver + Gold + Platinum Tiers
│   ├── watchers/              # Gmail, WhatsApp, LinkedIn, Filesystem
│   ├── skills/                # 10+ Agent Skills
│   ├── cloud/                 # Platinum Cloud Agent
│   ├── local/                 # Platinum Local Agent
│   ├── shared/                # Vault Sync Logic
│   ├── mcp/                   # MCP Servers (Odoo, Social Media)
│   └── vault/                 # Task files
├── dashboard/                 # Next.js Dashboard
├── vault/                     # Shared Obsidian Vault
└── .env.example               # Environment template
```

## 🔐 Security

**NEVER commit `.env` file to GitHub!**

The `.gitignore` is configured to protect:
- `.env` and environment files
- `credentials.json` (Gmail OAuth)
- `token.pickle` (Gmail tokens)
- Browser session profiles
- Log files

Always use `.env.example` as template for your actual credentials.

## 📋 Features

### ✅ Implemented
- [x] 4 Watchers (Gmail, WhatsApp, LinkedIn, Filesystem)
- [x] AI Reasoning Engine with failover
- [x] Human-in-the-loop approval workflow
- [x] Browser automation (Facebook, Instagram, Twitter, LinkedIn)
- [x] Dashboard with real-time updates
- [x] 10+ Agent Skills
- [x] MCP Server integration
- [x] Cloud + Local agent architecture
- [x] Audit logging
- [x] Task scheduling

### 🚧 Optional Enhancements
- [ ] Odoo integration (requires local Odoo 19 installation)
- [ ] WhatsApp Business API (Twilio credentials needed)
- [ ] Production cloud deployment

## 📝 Configuration

See `.env.example` for all required environment variables:

**Required:**
- `GEMINI_API_KEY` or `OPENROUTER_API_KEY`
- `EMAIL_ADDRESS` + `EMAIL_PASSWORD` (Gmail App Password)

**Optional (for advanced features):**
- `TWILIO_*` (WhatsApp)
- `LINKEDIN_*` (LinkedIn API)
- `FACEBOOK_EMAIL/PASSWORD` (Browser automation)
- `INSTAGRAM_USERNAME/PASSWORD` (Browser automation)
- `ODOO_*` (Odoo integration)

## 🎯 Use Cases

1. **Email Monitoring** - Auto-detect important emails, draft responses, get approval before sending
2. **Social Media Posting** - Schedule posts, auto-post from dashboard
3. **Document Processing** - Triage files, generate summaries
4. **Business Workflows** - Odoo integration for accounting/invoicing
5. **Autonomous Tasks** - Ralph Wiggum Loop for multi-step operations

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - feel free to use for personal or commercial projects.

## 🙏 Acknowledgments

- Built with Gemini AI + OpenRouter failover
- Next.js 15 Dashboard with Tailwind CSS
- FastAPI backend
- Selenium browser automation
- Claude Code reasoning engine

---

**Need Help?** Check `Welcome.md` or create an issue on GitHub.
