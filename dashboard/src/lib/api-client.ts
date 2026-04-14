/**
 * Dashboard API Client
 * Connects to Silver Tier Dashboard API (FastAPI backend)
 */

import {
  Task,
  DashboardStats,
  Activity,
  Plan,
  Approval,
  TasksResponse,
  PlansResponse,
  ActivityResponse,
  ApprovalsResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Generic API request handler
 */
async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const config = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

/**
 * Health check
 */
export async function checkHealth(): Promise<{ status: string; timestamp: string }> {
  return apiRequest('/api/health');
}

/**
 * Tasks API
 */
export async function getTasks(status?: string): Promise<Task[]> {
  const endpoint = status ? `/api/tasks?status=${status}` : '/api/tasks';
  return apiRequest<Task[]>(endpoint);
}

export async function getInboxTasks(): Promise<TasksResponse> {
  return apiRequest<TasksResponse>('/api/tasks/inbox');
}

export async function getNeedsActionTasks(): Promise<TasksResponse> {
  return apiRequest<TasksResponse>('/api/tasks/needs-action');
}

export async function getCompletedTasks(): Promise<TasksResponse> {
  return apiRequest<TasksResponse>('/api/tasks/completed');
}

export async function approveTask(taskId: string): Promise<{ success: boolean; message: string }> {
  return apiRequest('/api/tasks/approve', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId, action: 'approve' }),
  });
}

export async function rejectTask(taskId: string): Promise<{ success: boolean; message: string }> {
  return apiRequest('/api/tasks/reject', {
    method: 'POST',
    body: JSON.stringify({ task_id: taskId, action: 'reject' }),
  });
}

export async function createTask(
  title: string,
  content: string,
  priority: string = 'medium'
): Promise<{ success: boolean; task_id: string; message: string }> {
  return apiRequest('/api/tasks/create', {
    method: 'POST',
    body: JSON.stringify({ title, content, priority }),
  });
}

/**
 * Stats API
 */
export async function getStats(): Promise<DashboardStats> {
  return apiRequest<DashboardStats>('/api/stats');
}

/**
 * Activity API
 */
export async function getActivity(limit: number = 20): Promise<ActivityResponse> {
  return apiRequest<ActivityResponse>(`/api/activity?limit=${limit}`);
}

/**
 * Plans API
 */
export async function getPlans(limit: number = 10): Promise<PlansResponse> {
  return apiRequest<PlansResponse>(`/api/plans?limit=${limit}`);
}

/**
 * Approvals API
 */
export async function getApprovals(): Promise<ApprovalsResponse> {
  return apiRequest<ApprovalsResponse>('/api/approvals');
}

/**
 * Vault File API
 */
export async function getVaultFile(filePath: string): Promise<{
  filename: string;
  path: string;
  content: string;
}> {
  return apiRequest(`/api/vault/file/${encodeURIComponent(filePath)}`);
}

/**
 * Audit Logs API (Gold Tier)
 */
export async function getAuditLogs(limit: number = 20): Promise<any[]> {
  return apiRequest(`/api/audit?limit=${limit}`);
}

/**
 * Ralph Wiggum Loop Status API (Gold Tier)
 */
export async function getRalphWiggumStatus(): Promise<{
  running: boolean;
  tasks_processed: number;
  consecutive_failures: number;
  last_activity?: string;
}> {
  return apiRequest('/api/ralph-wiggum/status');
}

/**
 * Browser Automation API (Gold Tier - No API Keys Required)
 */
export interface BrowserPostData {
  message: string;
  platforms?: string[];
  image_path?: string;
}

export interface WhatsAppMessageData {
  phone: string;
  message: string;
}

export interface GmailData {
  to: string;
  subject: string;
  body: string;
}

export interface BrowserAutomationStatus {
  available: boolean;
  platforms: {
    facebook: boolean;
    instagram: boolean;
    twitter: boolean;
    linkedin: boolean;
    whatsapp: boolean;
    gmail: boolean;
  };
  selenium_installed: boolean;
}

export async function getBrowserAutomationStatus(): Promise<BrowserAutomationStatus> {
  return apiRequest('/api/browser-automation/status');
}

export async function postToSocialMedia(data: BrowserPostData): Promise<{
  success: boolean;
  posted_to: number;
  failed_on: number;
  results: {
    success: any[];
    failed: any[];
  };
  timestamp: string;
}> {
  return apiRequest('/api/browser-automation/post', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function postToPlatform(
  platform: string,
  data: BrowserPostData
): Promise<{
  success: boolean;
  platform: string;
  message?: string;
  error?: string;
  timestamp: string;
}> {
  return apiRequest(`/api/browser-automation/post/${platform}`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function sendWhatsAppMessage(data: WhatsAppMessageData): Promise<{
  success: boolean;
  platform: string;
  recipient: string;
  message?: string;
  error?: string;
  timestamp: string;
}> {
  return apiRequest('/api/browser-automation/whatsapp', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function sendGmailEmail(data: GmailData): Promise<{
  success: boolean;
  platform: string;
  recipient: string;
  subject: string;
  message?: string;
  error?: string;
  timestamp: string;
}> {
  return apiRequest('/api/browser-automation/gmail', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getBrowserAutomationHistory(
  limit: number = 10
): Promise<{ count: number; history: any[] }> {
  return apiRequest(`/api/browser-automation/history?limit=${limit}`);
}
