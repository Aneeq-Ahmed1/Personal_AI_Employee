# 📊 Silver Tier Dashboard API

FastAPI-based backend server for the Personal AI Employee dashboard.

---

## 🚀 Quick Start

### Install Dependencies
```bash
cd D:\Aneeq-AI\Personal_AI_Employee\silver\skills\dashboard-api
pip install -r requirements.txt
```

### Start the Server
```bash
python api_server.py
```

Server will start on: **http://localhost:8000**

---

## 📡 API Endpoints

### Health Check
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/api/health` | GET | Health check |

### Tasks
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tasks` | GET | Get all tasks |
| `/api/tasks?status=inbox` | GET | Filter by status |
| `/api/tasks/inbox` | GET | Get inbox tasks |
| `/api/tasks/needs-action` | GET | Get pending tasks |
| `/api/tasks/completed` | GET | Get completed tasks |
| `/api/tasks/approve` | POST | Approve a task |
| `/api/tasks/reject` | POST | Reject a task |
| `/api/tasks/create` | POST | Create new task |

### Plans
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/plans` | GET | Get generated plans |
| `/api/plans?limit=20` | GET | Limit results |

### Approvals
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/approvals` | GET | Get pending approvals |

### Stats & Activity
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Dashboard statistics |
| `/api/activity` | GET | Recent activity log |
| `/api/activity?limit=50` | GET | Limit results |

### Vault Files
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vault/file/{path}` | GET | Get vault file content |

### WebSocket
| Endpoint | Description |
|----------|-------------|
| `/ws` | Real-time updates |

---

## 🔌 WebSocket Usage

### Connect from Frontend
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to dashboard API');
  // Subscribe to events
  ws.send(JSON.stringify({
    type: 'subscribe',
    events: ['task_created', 'task_approved', 'vault_change']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
  
  // Handle different event types
  switch(data.type) {
    case 'task_created':
      // Update UI with new task
      break;
    case 'task_approved':
      // Refresh task list
      break;
    case 'vault_change':
      // Update counts
      break;
  }
};
```

### Event Types
- `task_created` - New task added to inbox
- `task_approved` - Task approved/completed
- `task_rejected` - Task rejected
- `vault_change` - Vault file count changed
- `pong` - Response to ping

---

## 📝 Request/Response Examples

### Get Tasks
```bash
curl http://localhost:8000/api/tasks
```

**Response:**
```json
[
  {
    "id": "needs_action_TODO_example",
    "title": "Send email to client",
    "summary": "Client requested a follow-up email",
    "next_step": "Draft and send email response",
    "source_file": "email_20260324_120000.md",
    "created_at": "2026-03-24 12:00:00",
    "status": "needs_action"
  }
]
```

### Approve Task
```bash
curl -X POST http://localhost:8000/api/tasks/approve \
  -H "Content-Type: application/json" \
  -d '{"task_id": "needs_action_TODO_example"}'
```

**Response:**
```json
{
  "success": true,
  "message": "Task needs_action_TODO_example approved and moved to completed"
}
```

### Get Stats
```bash
curl http://localhost:8000/api/stats
```

**Response:**
```json
{
  "inbox_count": 3,
  "needs_action_count": 5,
  "pending_approvals": 2,
  "completed_today": 12,
  "total_plans": 47,
  "total_tasks_completed": 156
}
```

---

## 🗂️ Vault Structure

```
silver/vault/
├── Inbox/              # New tasks arrive here
├── Needs_Action/       # Tasks awaiting action/approval
├── Plans/              # AI-generated action plans
├── Approvals/          # Approval requests
├── Completed/          # Finished tasks
└── memory/             # Processing memory (JSON)
```

---

## 🔧 Configuration

Edit `.env` in project root:

```env
# Dashboard API (no special config needed)
# Server runs on port 8000 by default
```

---

## 🧪 Testing

### Test Vault Reader
```bash
python vault_reader.py
```

### Test API Server
1. Start server: `python api_server.py`
2. Open browser: http://localhost:8000/docs
3. Try endpoints from Swagger UI

---

## 🔗 Integration with Next.js

### API Client Example
```typescript
// lib/api-client.ts
const API_BASE = 'http://localhost:8000';

export async function getTasks(status?: string) {
  const url = status 
    ? `${API_BASE}/api/tasks?status=${status}`
    : `${API_BASE}/api/tasks`;
  
  const res = await fetch(url);
  return res.json();
}

export async function approveTask(taskId: string) {
  const res = await fetch(`${API_BASE}/api/tasks/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task_id: taskId, action: 'approve' })
  });
  return res.json();
}

export async function getStats() {
  const res = await fetch(`${API_BASE}/api/stats`);
  return res.json();
}
```

---

## 📊 API Documentation

Once server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Change port in api_server.py
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use 8001 instead
```

### CORS Errors
Add your frontend URL in `api_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://your-frontend-url.com",  # Add your URL
    ],
    ...
)
```

### Vault Path Issues
Ensure vault directories exist:
```bash
mkdir -p silver/vault/Inbox
mkdir -p silver/vault/Needs_Action
mkdir -p silver/vault/Plans
mkdir -p silver/vault/Approvals
mkdir -p silver/vault/Completed
```

---

## 📈 Next Steps

1. ✅ Dashboard API complete
2. ⏳ Create Next.js frontend
3. ⏳ Connect API to frontend components
4. ⏳ Add real-time WebSocket updates
5. ⏳ Deploy to production

---

**Created:** 2026-03-24  
**Version:** 1.0.0  
**Status:** ✅ Ready for Testing
