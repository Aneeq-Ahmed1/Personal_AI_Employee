# 🏆 Gold Tier - Personal AI Employee

**Complete Implementation:** March 27, 2026

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Obsidian Vault (configured)
- API Keys (see Configuration section)

### Start All Gold Tier Services

```bash
# Windows
start_gold_tier.bat

# Manual start (individual services)
# See "Starting Services" section below
```

### Access Dashboards

- **Silver Tier Dashboard:** http://localhost:3000
- **Gold Tier Dashboard:** http://localhost:3000/gold-tier
- **API Documentation:** http://localhost:8000/docs

---

## What's New in Gold Tier

### 1. 🔄 Ralph Wiggum Loop (Autonomous Execution)

The autonomy engine that enables multi-step task execution without constant human intervention.

**Features:**
- Continuous vault scanning (30s interval)
- AI-powered task analysis
- Auto-approval for low-risk actions
- Plan generation and execution
- Learning from feedback
- Consecutive failure detection

**Usage:**
```bash
# Run in autonomous mode (continuous)
cd silver
python ralph_wiggum_loop.py

# Run single iteration
python ralph_wiggum_loop.py --once

# Check status
python ralph_wiggum_loop.py --status

# Custom interval (60 seconds)
python ralph_wiggum_loop.py --interval 60
```

**Loop Cycle:**
1. Scan Inbox & Needs_Action folders
2. Analyze each task with AI reasoning
3. Create execution plan (Plan.md)
4. Auto-execute approved actions via MCP servers
5. Move completed tasks to Completed folder
6. Log all actions to audit trail
7. Learn from results for better decisions
8. Repeat

---

### 2. 📊 CEO Briefing Generator

Automated executive briefing generation with AI analysis.

**Features:**
- Daily briefings (every morning)
- Weekly briefings (every Monday)
- AI-powered insights
- Dashboard stats integration
- Email delivery option
- Markdown export

**Usage:**
```bash
# Generate daily briefing
cd silver/skills/ceo-briefing
python ceo_briefing.py --type daily

# Generate weekly briefing
python ceo_briefing.py --type weekly

# Send via email
python ceo_briefing.py --type daily --send-email --recipient ceo@company.com

# View briefing history
python ceo_briefing.py --history
```

**Briefing Content:**
- Executive Summary
- Key Metrics & KPIs
- Completed Work Highlights
- Pending Decisions/Approvals
- AI Strategic Recommendations

---

### 3. 📝 Audit Logging System

Centralized compliance and security logging for all AI actions.

**Features:**
- Action tracking
- Security event logging
- Error logging with stack traces
- Compliance reporting (daily/weekly/monthly)
- Query & filtering
- Export (JSON/CSV)
- Automatic cleanup (90-day retention)
- File compression

**Usage:**
```bash
# Query logs (last 7 days)
cd silver
python audit_logger.py --query

# Query with filters
python audit_logger.py --query --from 2026-03-20 --action send_email

# Show statistics
python audit_logger.py --stats

# Generate compliance report
python audit_logger.py --report daily
python audit_logger.py --report weekly

# Export logs
python audit_logger.py --export audit_export.json --from 2026-03-01

# Cleanup old logs
python audit_logger.py --cleanup
```

**Log Entry Fields:**
- ID, Timestamp, Action, Status
- User, Model, Record ID
- Details (JSON)
- IP Address, Session ID
- Environment info

---

### 4. 🔌 MCP Servers

#### Odoo MCP Server (Port 5001)

Integration with Odoo 19 for accounting, sales, and inventory.

**Endpoints:**
- `GET/POST /account/invoices` - List/Create invoices
- `POST /account/invoices/:id/post` - Post invoice
- `GET /account/journal-items` - Get journal items
- `GET/POST /sales/orders` - List/Create sales orders
- `POST /sales/quotation/:id/confirm` - Confirm quotation
- `GET /partners` - List partners/customers
- `GET /products` - List products

**Configuration:**
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
ODOO_API_KEY=your-api-key
```

#### Social Media MCP Server (Port 5002)

Unified social media management across Facebook, Instagram, Twitter/X, and LinkedIn.

**Endpoints:**
- `POST /post` - Post to all platforms
- `POST /post/facebook` - Facebook only
- `POST /post/instagram` - Instagram only
- `POST /post/twitter` - Twitter/X only
- `POST /post/linkedin` - LinkedIn only
- `GET /analytics` - Get analytics
- `POST /schedule` - Schedule post
- `POST /schedule/:id/cancel` - Cancel scheduled post

**Configuration:**
```bash
# Facebook
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_ACCESS_TOKEN=your-access-token
FACEBOOK_PAGE_ID=your-page-id

# Instagram
INSTAGRAM_APP_ID=your-app-id
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-business-id

# Twitter/X
TWITTER_BEARER_TOKEN=your-bearer-token
TWITTER_API_KEY=your-api-key
TWITTER_ACCESS_TOKEN=your-access-token

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your-access-token
LINKEDIN_ORGANIZATION_ID=your-org-id
```

---

### 5. 🎯 Gold Tier Dashboard

Advanced monitoring and control center for all Gold Tier features.

**Access:** http://localhost:3000/gold-tier

**Tabs:**

1. **System Overview**
   - Overall health status (healthy/degraded/down)
   - Watcher status (4 watchers)
   - MCP server status (4 servers)
   - Real-time updates

2. **Audit Logs**
   - Real-time log viewer
   - Filter by status/action
   - Timestamp & details
   - Export options

3. **Ralph Wiggum Loop**
   - Running status
   - Tasks processed counter
   - Consecutive failures
   - Start/Stop controls
   - Activity history

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Watchers Layer                        │
├─────────────────────────────────────────────────────────┤
│  Gmail  │  WhatsApp  │  LinkedIn  │  Filesystem        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Obsidian Vault                         │
│  Inbox  │  Needs_Action  │  Plans  │  Completed        │
│                      Audit                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│            Ralph Wiggum Loop (Autonomy Engine)           │
│  • Scan vault  • AI analysis  • Execute  • Learn       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                    MCP Server Layer                      │
├─────────────────────────────────────────────────────────┤
│  Email   │  Odoo    │  Social   │  Dashboard          │
│  :5000   │  :5001   │  :5002    │  :8000              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│               Gold Tier Dashboard                        │
│  http://localhost:3000/gold-tier                        │
│  • System Health  • Audit Logs  • Loop Control         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              CEO Briefing Generator                      │
│  • Daily/Weekly Briefings  • Email Delivery            │
└─────────────────────────────────────────────────────────┘
```

---

## Starting Services

### Option 1: Start All (Recommended)

```bash
# Windows
start_gold_tier.bat
```

### Option 2: Manual Start

```bash
# Terminal 1: Dashboard API (Silver Tier)
cd silver/skills/dashboard-api
python api_server.py

# Terminal 2: Odoo MCP Server
cd silver/mcp
python odoo_mcp_server.py

# Terminal 3: Social Media MCP Server
cd silver/mcp
python social_media_mcp_server.py

# Terminal 4: Next.js Dashboard
cd dashboard
npm run dev

# Terminal 5: Ralph Wiggum Loop (Autonomous Mode)
cd silver
python ralph_wiggum_loop.py
```

---

## Testing

### Test Odoo MCP Server

```bash
# Test connection
curl http://localhost:5001/test-connection

# List invoices
curl http://localhost:5001/account/invoices

# List products
curl http://localhost:5001/products
```

### Test Social Media MCP Server

```bash
# Health check
curl http://localhost:5002/health

# Post to all platforms
curl -X POST http://localhost:5002/post \
  -H "Content-Type: application/json" \
  -d '{"text": "Test post from Gold Tier!", "platforms": ["facebook", "twitter"]}'
```

### Test Ralph Wiggum Loop

```bash
# Single iteration
cd silver
python ralph_wiggum_loop.py --once

# Check status
python ralph_wiggum_loop.py --status
```

### Test CEO Briefing

```bash
# Generate daily briefing
cd silver/skills/ceo-briefing
python ceo_briefing.py --type daily
```

### Test Audit Logger

```bash
# Query recent logs
cd silver
python audit_logger.py --query --limit 10

# Show statistics
python audit_logger.py --stats
```

---

## Configuration

### Environment Variables (.env)

Create or update `.env` in the project root:

```bash
# AI Providers
GEMINI_API_KEY=your-gemini-key
OPENROUTER_API_KEY=your-openrouter-key

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
ODOO_API_KEY=

# Social Media - Facebook
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
FACEBOOK_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=

# Social Media - Instagram
INSTAGRAM_APP_ID=
INSTAGRAM_APP_SECRET=
INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_BUSINESS_ACCOUNT_ID=

# Social Media - Twitter
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_BEARER_TOKEN=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

# Social Media - LinkedIn
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_ORGANIZATION_ID=

# Audit Logging
AUDIT_RETENTION_DAYS=90
AUDIT_ENABLE_COMPRESSION=true
```

---

## Troubleshooting

### Ralph Wiggum Loop Not Starting

```bash
# Check Python version (requires 3.10+)
python --version

# Check dependencies
pip install requests python-dotenv

# Run with debug output
python ralph_wiggum_loop.py --once
```

### MCP Server Port Conflicts

```bash
# Check if port is in use (Windows)
netstat -ano | findstr :5001
netstat -ano | findstr :5002

# Kill process (replace PID)
taskkill /PID 12345 /F
```

### Dashboard Build Errors

```bash
# Clear cache and rebuild
cd dashboard
rm -rf .next
npm run build
```

### Audit Logs Not Appearing

```bash
# Check audit directory exists
ls vault/Audit

# Create if missing
mkdir vault/Audit
```

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| MCP Servers | 4 | ✅ |
| Watchers | 4 | ✅ |
| Autonomous Execution | Yes | ✅ |
| Audit Logging | Yes | ✅ |
| CEO Briefings | Yes | ✅ |
| Dashboard Integration | Yes | ✅ |
| Build Passing | Yes | ✅ |

---

## File Structure

```
Personal_AI_Employee/
├── silver/
│   ├── mcp/
│   │   ├── odoo_mcp_server.py      # Odoo integration
│   │   └── social_media_mcp_server.py  # Social media
│   ├── skills/
│   │   ├── ceo-briefing/
│   │   │   └── ceo_briefing.py     # Briefing generator
│   │   └── dashboard-api/
│   │       └── api_server.py       # Dashboard API
│   ├── vault/
│   │   ├── Audit/                  # Audit logs
│   │   ├── CEO_Briefings/          # Generated briefings
│   │   └── ...
│   ├── ralph_wiggum_loop.py        # Autonomy engine
│   └── audit_logger.py             # Audit logging
├── dashboard/
│   └── src/
│       └── app/
│           ├── gold-tier/
│           │   └── page.tsx        # Gold Tier dashboard
│           └── ...
└── start_gold_tier.bat             # Start script
```

---

## Next Steps

### After Installation

1. **Configure API Keys**
   - Add Odoo credentials
   - Add social media API keys
   - Test each MCP server

2. **Test Autonomous Execution**
   - Create a test task in `vault/Inbox`
   - Run Ralph Wiggum Loop
   - Verify task execution

3. **Set Up Scheduled Briefings**
   - Configure Windows Task Scheduler
   - Schedule daily briefing at 8 AM
   - Schedule weekly briefing on Monday 9 AM

4. **Monitor System Health**
   - Check Gold Tier dashboard
   - Review audit logs daily
   - Set up alerts for failures

### Future Enhancements

- Voice interaction
- Advanced ML models
- Custom integrations
- Multi-tenant support
- Mobile app

---

## Support

- **Documentation:** See `GOLD_TIER_COMPLETE.md` for detailed implementation
- **API Docs:** http://localhost:8000/docs
- **Logs:** `vault/Audit/`
- **Briefings:** `vault/CEO_Briefings/`

---

**Gold Tier Status:** ✅ COMPLETE  
**Implementation Date:** March 27, 2026  
**Version:** 1.0.0
