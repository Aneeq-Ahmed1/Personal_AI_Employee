# 🤖 AI WORKFLOW & SENSITIVE DATA HANDLING

**Complete Guide to How AI Works in Silver Tier**

---

## 📋 Table of Contents

1. [AI Provider Architecture](#ai-provider-architecture)
2. [How AI Processes Tasks](#how-ai-processes-tasks)
3. [Sensitive Data Handling](#sensitive-data-handling)
4. [Human-in-the-Loop Approval](#human-in-the-loop-approval)
5. [Live Demo Test](#live-demo-test)

---

## 🏗️ AI Provider Architecture

### Multi-Provider with Auto-Failover

```
┌─────────────────────────────────────────────────────────┐
│                    User Request                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Provider Manager (Auto Mode)                │
│                                                          │
│  Priority 1: Gemini API (Free)                          │
│  Priority 2: OpenRouter API (Paid Backup)               │
│                                                          │
│  Auto-failover if quota exhausted                       │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│   Gemini 2.0     │              │  OpenRouter      │
│   Flash API      │              │  (Claude/GPT-4)  │
│   (Primary)      │              │  (Backup)        │
└──────────────────┘              └──────────────────┘
```

### Configuration (`.env`)

```bash
# AI Provider Mode
AI_PROVIDER=auto  # auto | gemini | openrouter

# Gemini (Primary)
GEMINI_API_KEY=AIzaSyCztmynoN_N0vMVkPomw5RZZSHcOg9laJY

# OpenRouter (Backup)
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=google/gemini-2.0-flash-001
```

### Code Flow: `provider_manager.py`

```python
# File: silver/skills/ai-providers/provider_manager.py

class ProviderManager:
    def generate(self, prompt: str) -> AIResponse:
        
        # MODE: auto (default)
        if self.mode == 'auto':
            
            # Step 1: Try Gemini first
            if self.gemini and not self.gemini_exhausted:
                response = self.gemini.generate(prompt)
                
                if response.success:
                    return response  # ✅ Success!
                
                if response.is_quota_error:
                    self.gemini_exhausted = True
                    # Fall through to OpenRouter
            
            # Step 2: Fallback to OpenRouter
            if self.openrouter:
                response = self.openrouter.generate(prompt)
                return response
        
        # Error: Both failed
        return AIResponse(success=False, error="No providers available")
```

---

## 🔍 How AI Processes Tasks

### Step-by-Step Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Watcher Detects New Task                            │
│ Gmail/WhatsApp → silver/vault/Inbox/                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: File Triage Skill                                   │
│ Analyzes content → Moves to Needs_Action/ or Completed/     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Reasoning Engine (AI Analysis)                      │
│ Reads task → Calls Gemini API → Extracts:                  │
│   • Summary                                                 │
│   • Suggested Next Step                                     │
│   • Priority (High/Medium/Low)                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Plan Generation                                     │
│ Creates Plan_YYYYMMDD_HHMMSS.md with prioritized tasks     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Sensitive Action Check                              │
│ If action is sensitive → Request Approval                   │
│ If normal → Execute automatically                           │
└─────────────────────────────────────────────────────────────┘
```

### AI Analysis Example

**Input Task:** `EMAIL_20260324_235305_Test_Email.md`

```markdown
# Test Email - Dashboard Check

## From
aneeq.edward@outlook.com

## Email Body
Yeh test email hai Gmail integration check karne ke liye.
Please confirm receipt and add this to the dashboard.
```

**AI Prompt to Gemini:**
```python
prompt = f"""
Analyze the following task and provide:
1. A concise summary of the task
2. A suggested next step to take
3. A priority level (High, Medium, or Low)

Task content:
{content}

Respond in JSON format with keys: "summary", "suggested_next", "priority".
"""
```

**AI Response:**
```json
{
  "summary": "Test email to verify Gmail integration with dashboard. User wants confirmation of receipt and dashboard visibility.",
  "suggested_next": "Verify email appears in dashboard inbox and mark as processed",
  "priority": "Low"
}
```

**Generated Plan:**
```markdown
# Action Plan
Generated on: 2026-03-24 23:53:05

## Tasks by Priority

### Task 1: Test Email - Dashboard Check (Priority: Low)
- **Source File**: EMAIL_20260324_235305_Test_Email.md
- **Summary**: Test email to verify Gmail integration...
- **Suggested Next Step**: Verify email appears in dashboard...
```

---

## 🔒 Sensitive Data Handling

### What Triggers Approval?

**Sensitive Keywords:**
```python
sensitive_keywords = [
    'delete', 'remove', 'terminate', 'shutdown',
    'payment', 'financial', 'money', 'salary',
    'confidential', 'private', 'password',
    'credentials', 'security', 'admin', 'administrator'
]
```

### Approval Flow

```
┌─────────────────────────────────────────────────────────────┐
│ AI Detects Sensitive Action                                 │
│ Example: "Delete all emails from inbox"                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Approval Request Created                                    │
│ File: silver/vault/Approvals/approval_request_12345.md     │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│  Email Alert     │              │  Dashboard       │
│  (if configured) │              │  Shows pending   │
│                  │              │  approval        │
└──────────────────┘              └──────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Human Reviews & Approves/Rejects                            │
│   • Click Approve in Dashboard                              │
│   • Or edit approval file                                   │
│   • Or reply to email                                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│   APPROVED ✅    │              │   REJECTED ❌    │
│   Execute action │              │   Cancel action  │
│   Log to vault   │              │   Log rejection  │
└──────────────────┘              └──────────────────┘
```

### Code: Approval Check

```python
# File: silver/skills/human-approval/human_approval.py

class ApprovalManager:
    def is_sensitive_action(self, action_data):
        """Check if action contains sensitive keywords"""
        sensitive_keywords = ['delete', 'payment', 'password', ...]
        action_str = json.dumps(action_data).lower()
        return any(keyword in action_str for keyword in sensitive_keywords)

    def request_approval(self, action_type, action_data):
        """Request human approval before executing"""
        
        # Not sensitive? Auto-approve
        if not self.is_sensitive_action(action_data):
            return True
        
        # Create approval file
        approval_request = {
            "action_type": action_type,
            "data": action_data,
            "status": "pending"
        }
        
        # Save to vault/Approvals/
        request_path = self.save_approval_file(approval_request)
        
        # Send email notification
        self.send_email_notification(action_type, action_data)
        
        # Wait for approval
        return self.wait_for_approval(request_path)
```

---

## 🎯 Human-in-the-Loop Approval

### Approval Methods

#### Method 1: Dashboard UI (Recommended)
```
1. Open http://localhost:3000
2. See "Needs Action" section
3. Click task → Modal opens
4. Click "✓ Approve" or "✕ Reject"
```

#### Method 2: File Editing
```
1. Open: silver/vault/Approvals/approval_request_*.md
2. Change: **Status:** pending → **Status:** approved
3. Save file
4. AI detects change and proceeds
```

#### Method 3: Email Reply
```
1. Receive email notification
2. Reply with "APPROVE" or "REJECT"
3. Gmail watcher processes reply
4. Approval status updated
```

---

## 🧪 Live Demo Test

### Test 1: Normal Task (No Approval Needed)

**Send Email:**
```
To: aneeq113@gmail.com
Subject: Meeting Notes

Body: Please add meeting notes to the vault.
```

**Expected Flow:**
1. ✅ Gmail watcher detects email
2. ✅ Creates task in `Inbox/`
3. ✅ Reasoning engine analyzes (AI call)
4. ✅ Moves to `Needs_Action/`
5. ✅ Plan generated
6. ✅ Dashboard shows task
7. ⏳ Waiting for human approval (NOT sensitive, but requires review)

### Test 2: Sensitive Task (Approval Required)

**Send Email:**
```
To: aneeq113@gmail.com
Subject: Delete Old Emails

Body: Please delete all emails older than 30 days from the inbox.
```

**Expected Flow:**
1. ✅ Gmail watcher detects email
2. ✅ Creates task in `Inbox/`
3. ✅ Reasoning engine analyzes
4. ✅ **Keyword "delete" detected** → SENSITIVE!
5. ✅ Approval request created in `Approvals/`
6. ✅ Email notification sent
7. ⏳ **BLOCKED - Waiting for human approval**
8. Human must approve before deletion

---

## 📊 AI Logs & Monitoring

### Check AI Activity

```bash
# View reasoning engine logs
type silver\skills\reasoning-engine\reasoning_engine.log

# View provider logs
type silver\skills\ai-providers\provider_manager.log

# View approval logs
dir silver\vault\Approvals\
```

### Sample Log Output

```
2026-03-24 23:53:05 | ==================================================
2026-03-24 23:53:05 | AI Provider Mode: auto
2026-03-24 23:53:05 | ==================================================
2026-03-24 23:53:05 | Attempting Gemini API (primary)...
2026-03-24 23:53:06 | ✅ Gemini SUCCESS (Provider: gemini)
2026-03-24 23:53:06 | Gemini reasoning started (attempt 1/3)
2026-03-24 23:53:07 | Gemini reasoning success: Priority=Low
2026-03-24 23:53:07 | Processing complete: EMAIL_20260324_235305_Test_Email.md
```

---

## 🔐 Security & Privacy

### Data Never Leaves Your System

```
✅ Local Processing:
   - All files stored in silver/vault/
   - AI API calls only when needed
   - Sensitive data filtered before API call

✅ API Call Filtering:
   - Passwords removed from prompts
   - Credentials never sent to AI
   - Only task content analyzed

✅ Human Oversight:
   - All sensitive actions require approval
   - Audit trail in Approvals folder
   - Email notifications for transparency
```

### What Gets Sent to AI

**Sent to Gemini:**
```
Task content:
- Meeting notes from email
- Summary request
- Priority analysis
```

**NOT Sent to Gemini:**
```
❌ Email passwords
❌ API keys
❌ Credit card numbers
❌ Personal identifiers
```

---

## 🚀 Quick Test Commands

```bash
# Test AI connection
cd silver\skills\ai-providers
python provider_manager.py

# Test reasoning engine
cd silver\skills\reasoning-engine
python reasoning_engine.py

# Check current AI status
cd silver
python -c "from skills.ai-providers.provider_manager import get_provider_manager; print(get_provider_manager().get_status())"
```

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `silver/skills/ai-providers/provider_manager.py` | AI provider management |
| `silver/skills/reasoning-engine/reasoning_engine.py` | Task analysis with AI |
| `silver/skills/human-approval/human_approval.py` | Approval workflow |
| `silver/vault/Approvals/` | Approval requests |
| `silver/vault/Plans/` | AI-generated plans |
| `silver/vault/Needs_Action/` | Tasks pending review |

---

*Generated by Silver Tier AI System*
