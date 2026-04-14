// Task types
export interface Task {
  id: string;
  title: string;
  summary: string;
  next_step: string;
  source_file: string;
  created_at: string;
  status: 'inbox' | 'needs_action' | 'approved' | 'rejected' | 'completed';
  content?: string;
}

// Stats types
export interface DashboardStats {
  inbox_count: number;
  needs_action_count: number;
  pending_approvals: number;
  completed_today: number;
  total_plans: number;
  total_tasks_completed: number;
}

// Activity types
export interface Activity {
  timestamp: string;
  type: string;
  description: string;
  details?: {
    file?: string;
    category?: string;
    [key: string]: any;
  };
}

// Plan types
export interface Plan {
  id: string;
  title: string;
  summary: string;
  next_step: string;
  source_file: string;
  created_at: string;
  content: string;
}

// Approval types
export interface Approval {
  id: string;
  file_path: string;
  content: string;
  created_at: string;
  action_type?: string;
  status?: string;
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

export interface TasksResponse {
  count: number;
  tasks: Task[];
}

export interface PlansResponse {
  count: number;
  plans: Plan[];
}

export interface ActivityResponse {
  count: number;
  activities: Activity[];
}

export interface ApprovalsResponse {
  count: number;
  approvals: Approval[];
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

export interface TaskCreatedMessage extends WebSocketMessage {
  type: 'task_created';
  task_id: string;
  title: string;
  timestamp: string;
}

export interface TaskApprovedMessage extends WebSocketMessage {
  type: 'task_approved';
  task_id: string;
  timestamp: string;
}

export interface TaskRejectedMessage extends WebSocketMessage {
  type: 'task_rejected';
  task_id: string;
  timestamp: string;
}

export interface VaultChangeMessage extends WebSocketMessage {
  type: 'vault_change';
  category: 'inbox' | 'needs_action' | 'plans';
  old_count: number;
  new_count: number;
  timestamp: string;
}
