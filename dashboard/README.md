# 📊 Silver Tier Dashboard

Next.js-based frontend dashboard for the Personal AI Employee system.

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Silver Tier Dashboard API running (`http://localhost:8000`)

### Installation

1. **Install dependencies:**
```bash
cd D:\Aneeq-AI\Personal_AI_Employee\dashboard
npm install
```

2. **Start the Dashboard API (if not already running):**
```bash
cd D:\Aneeq-AI\Personal_AI_Employee\silver\skills\dashboard-api
python api_server.py
```

3. **Start the Dashboard:**
```bash
npm run dev
```

4. **Open in browser:**
```
http://localhost:3000
```

---

## 📁 Project Structure

```
dashboard/
├── src/
│   ├── app/
│   │   ├── page.tsx          # Main dashboard page
│   │   ├── layout.tsx        # Root layout
│   │   └── globals.css       # Global styles
│   ├── components/
│   │   ├── StatsCard.tsx     # Statistics cards
│   │   ├── TaskCard.tsx      # Task display card
│   │   └── ActivityFeed.tsx  # Activity timeline
│   ├── lib/
│   │   ├── api-client.ts     # API REST client
│   │   └── websocket-client.ts # WebSocket client
│   └── types/
│       └── index.ts          # TypeScript types
├── .env.local                # Environment variables
├── next.config.ts            # Next.js configuration
├── tailwind.config.ts        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

---

## 🎯 Features

### Dashboard Overview
- **Real-time Statistics**: Inbox count, needs action, completed today, total plans
- **Task Management**: View, approve, or reject tasks
- **Activity Feed**: Recent system activity
- **Live Updates**: WebSocket-based real-time updates

### Components

#### StatsCard
Displays statistics with color-coded cards:
- 📥 Inbox (Blue)
- ⏳ Needs Action (Yellow)
- ✅ Completed Today (Green)
- 📋 Total Plans (Purple)

#### TaskCard
Shows task details with:
- Title and summary
- Next step suggestion
- Source file reference
- Approve/Reject actions

#### ActivityFeed
Timeline of recent events:
- Plan generated
- Task completed
- Task received
- Task approved/rejected

---

## 🔌 API Integration

### REST API Client
```typescript
import { getStats, getTasks, approveTask } from '@/lib/api-client';

// Get dashboard stats
const stats = await getStats();

// Get tasks
const tasks = await getTasks();

// Approve a task
await approveTask('task_id');
```

### WebSocket Client
```typescript
import { getWebSocketClient } from '@/lib/websocket-client';

const ws = getWebSocketClient();

// Connect
await ws.connect();

// Listen for events
ws.on('task_created', (message) => {
  console.log('New task created:', message);
});

// Disconnect
ws.disconnect();
```

---

## 🎨 Customization

### Colors
Edit `tailwind.config.ts` to customize theme colors:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#0ea5e9',  // Change primary color
      },
    },
  },
}
```

### Environment Variables
Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

---

## 🛠️ Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

### Build for Production

```bash
npm run build
npm start
```

The dashboard will be available at `http://localhost:3000`.

---

## 📸 Screenshots

### Dashboard View
- Stats cards at top
- Tasks list in main column
- Activity feed on right
- Real-time updates via WebSocket

---

## 🔗 Related

- **Dashboard API**: `silver/skills/dashboard-api/`
- **Backend**: Silver Tier Personal AI Employee
- **Vault**: `silver/vault/`

---

## 📝 License

Part of Silver Tier Personal AI Employee project.

---

**Created:** 2026-03-24  
**Version:** 1.0.0  
**Status:** ✅ Ready for Use
