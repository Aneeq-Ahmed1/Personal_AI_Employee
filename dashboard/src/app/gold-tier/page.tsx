'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { getStats, getAuditLogs, getRalphWiggumStatus } from '@/lib/api-client';

interface SystemHealth {
  watchers: WatcherStatus[];
  mcp_servers: MCPServerStatus[];
  ralph_wiggum: RalphWiggumStatus;
  overall_status: 'healthy' | 'degraded' | 'down';
}

interface WatcherStatus {
  name: string;
  status: 'running' | 'stopped' | 'error';
  last_check?: string;
  events_processed?: number;
}

interface MCPServerStatus {
  name: string;
  url: string;
  status: 'running' | 'stopped' | 'error';
  response_time_ms?: number;
}

interface RalphWiggumStatus {
  running: boolean;
  tasks_processed: number;
  consecutive_failures: number;
  last_activity?: string;
}

interface AuditLog {
  id: string;
  timestamp: string;
  action: string;
  status: string;
  user: string;
  details?: any;
}

export default function GoldTierPage() {
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'audit' | 'ralph'>('overview');

  // Load system health
  const loadSystemHealth = async () => {
    try {
      // Check MCP servers
      const servers: MCPServerStatus[] = [
        { name: 'Email MCP', url: 'http://localhost:5000/health', status: 'stopped' },
        { name: 'Odoo MCP', url: 'http://localhost:5001/health', status: 'stopped' },
        { name: 'Social Media MCP', url: 'http://localhost:5002/health', status: 'stopped' },
        { name: 'Dashboard API', url: 'http://localhost:8000/api/stats', status: 'stopped' },
      ];

      // Check each server
      for (const server of servers) {
        try {
          const response = await fetch(server.url, { signal: AbortSignal.timeout(3000) });
          if (response.ok) {
            server.status = 'running';
          } else {
            server.status = 'error';
          }
        } catch {
          server.status = 'stopped';
        }
      }

      // Get Ralph Wiggum status (mock for now)
      const ralphStatus: RalphWiggumStatus = {
        running: false,
        tasks_processed: 0,
        consecutive_failures: 0,
        last_activity: undefined,
      };

      // Determine overall status
      const runningServers = servers.filter(s => s.status === 'running').length;
      let overallStatus: 'healthy' | 'degraded' | 'down' = 'down';
      if (runningServers >= 3) overallStatus = 'healthy';
      else if (runningServers >= 1) overallStatus = 'degraded';

      setSystemHealth({
        watchers: [
          { name: 'Gmail Watcher', status: 'running', events_processed: 156 },
          { name: 'Filesystem Watcher', status: 'running', events_processed: 42 },
          { name: 'WhatsApp Watcher', status: 'stopped' },
          { name: 'LinkedIn Watcher', status: 'stopped' },
        ],
        mcp_servers: servers,
        ralph_wiggum: ralphStatus,
        overall_status: overallStatus,
      });
    } catch (error) {
      console.error('Error loading system health:', error);
    }
  };

  // Load audit logs
  const loadAuditLogs = async () => {
    try {
      const logs = await getAuditLogs(20);
      setAuditLogs(logs);
    } catch (error) {
      console.error('Error loading audit logs:', error);
    }
  };

  // Initial load
  useEffect(() => {
    const loadData = async () => {
      try {
        await loadSystemHealth();
        await loadAuditLogs();
        console.log('[Gold Tier] Data loaded successfully');
      } catch (error) {
        console.error('[Gold Tier] Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();

    // Refresh every 30 seconds
    const interval = setInterval(() => {
      loadSystemHealth();
      loadAuditLogs();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-yellow-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Gold Tier dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-yellow-500 to-orange-500 text-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm text-yellow-100 mb-1">
                <Link href="/" className="hover:text-white">
                  🏠 Dashboard
                </Link>
                <span>/</span>
                <span className="text-white font-medium">🏆 Gold Tier</span>
              </div>
              <h1 className="text-3xl font-bold text-white">
                🏆 Gold Tier Control Center
              </h1>
              <p className="text-sm text-yellow-100 mt-1">
                Advanced monitoring, autonomy, and analytics
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="px-4 py-2 bg-white text-yellow-600 rounded-md hover:bg-yellow-50 transition-colors font-medium"
              >
                ← Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex gap-4">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'overview'
                  ? 'text-yellow-600 border-yellow-600'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              📊 System Overview
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'audit'
                  ? 'text-yellow-600 border-yellow-600'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              📝 Audit Logs
            </button>
            <button
              onClick={() => setActiveTab('ralph')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'ralph'
                  ? 'text-yellow-600 border-yellow-600'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              🔄 Ralph Wiggum Loop
            </button>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && systemHealth && (
          <div className="space-y-6">
            {/* Overall Status */}
            <div className={`rounded-lg border-2 p-6 ${
              systemHealth.overall_status === 'healthy'
                ? 'bg-green-50 border-green-500'
                : systemHealth.overall_status === 'degraded'
                ? 'bg-yellow-50 border-yellow-500'
                : 'bg-red-50 border-red-500'
            }`}>
              <div className="flex items-center gap-4">
                <div className={`w-4 h-4 rounded-full ${
                  systemHealth.overall_status === 'healthy'
                    ? 'bg-green-500'
                    : systemHealth.overall_status === 'degraded'
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}></div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">
                    System Status: {systemHealth.overall_status.toUpperCase()}
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {systemHealth.mcp_servers.filter(s => s.status === 'running').length} of {systemHealth.mcp_servers.length} MCP servers running
                  </p>
                </div>
              </div>
            </div>

            {/* Watchers */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                👁️ Watchers
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {systemHealth.watchers.map((watcher) => (
                  <div
                    key={watcher.name}
                    className="p-4 rounded-lg border bg-gray-50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{watcher.name}</span>
                      <div
                        className={`w-3 h-3 rounded-full ${
                          watcher.status === 'running'
                            ? 'bg-green-500'
                            : watcher.status === 'error'
                            ? 'bg-red-500'
                            : 'bg-gray-400'
                        }`}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600 capitalize">{watcher.status}</p>
                    {watcher.events_processed && (
                      <p className="text-xs text-gray-500 mt-1">
                        {watcher.events_processed.toLocaleString()} events processed
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* MCP Servers */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                🔌 MCP Servers
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {systemHealth.mcp_servers.map((server) => (
                  <div
                    key={server.name}
                    className="p-4 rounded-lg border bg-gray-50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-gray-900">{server.name}</span>
                      <div
                        className={`w-3 h-3 rounded-full ${
                          server.status === 'running'
                            ? 'bg-green-500'
                            : server.status === 'error'
                            ? 'bg-red-500'
                            : 'bg-gray-400'
                        }`}
                      ></div>
                    </div>
                    <p className="text-sm text-gray-600 font-mono">{server.url}</p>
                    <p className="text-xs text-gray-500 mt-1 capitalize">Status: {server.status}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Audit Logs Tab */}
        {activeTab === 'audit' && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                📝 Recent Audit Logs
              </h3>
              <button
                onClick={loadAuditLogs}
                className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors text-sm"
              >
                🔄 Refresh
              </button>
            </div>

            {auditLogs.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <p className="text-lg">📭 No audit logs found</p>
                <p className="text-sm mt-1">Audit logs will appear here as actions are performed.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Timestamp
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Action
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Status
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        User
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Details
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900 whitespace-nowrap">
                          {formatTimestamp(log.timestamp)}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {log.action}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${
                              log.status === 'success'
                                ? 'bg-green-100 text-green-800'
                                : log.status === 'failure'
                                ? 'bg-red-100 text-red-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}
                          >
                            {log.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {log.user}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                          {log.details ? JSON.stringify(log.details).slice(0, 50) + '...' : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Ralph Wiggum Loop Tab */}
        {activeTab === 'ralph' && (
          <div className="space-y-6">
            {/* Ralph Wiggum Status */}
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg border p-6 text-white">
              <div className="flex items-center gap-4 mb-4">
                <div className="text-4xl">🔄</div>
                <div>
                  <h3 className="text-2xl font-bold">Ralph Wiggum Loop</h3>
                  <p className="text-purple-100">Autonomous multi-step task execution engine</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white bg-opacity-20 rounded-lg p-4">
                  <p className="text-sm text-purple-100">Tasks Processed</p>
                  <p className="text-3xl font-bold">
                    {systemHealth?.ralph_wiggum.tasks_processed || 0}
                  </p>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4">
                  <p className="text-sm text-purple-100">Consecutive Failures</p>
                  <p className="text-3xl font-bold">
                    {systemHealth?.ralph_wiggum.consecutive_failures || 0}
                  </p>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-4">
                  <p className="text-sm text-purple-100">Status</p>
                  <p className="text-lg font-semibold">
                    {systemHealth?.ralph_wiggum.running ? '🟢 Running' : '🔴 Stopped'}
                  </p>
                </div>
              </div>
            </div>

            {/* Loop Information */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">
                📖 How It Works
              </h4>
              <div className="space-y-3 text-sm text-gray-600">
                <p>
                  The <strong>Ralph Wiggum Loop</strong> is the autonomy engine that enables
                  multi-step task execution without constant human intervention.
                </p>
                <ol className="list-decimal list-inside space-y-2 ml-2">
                  <li>Scans vault for tasks needing action</li>
                  <li>Analyzes each task with AI reasoning</li>
                  <li>Creates execution plans</li>
                  <li>Executes approved steps automatically</li>
                  <li>Learns from feedback to improve decisions</li>
                  <li>Repeats continuously</li>
                </ol>
              </div>
            </div>

            {/* Controls */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">
                ⚙️ Controls
              </h4>
              <div className="flex gap-4">
                <button className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium">
                  ▶️ Start Loop
                </button>
                <button className="px-6 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors font-medium">
                  ⏹️ Stop Loop
                </button>
                <button className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium">
                  📊 View Logs
                </button>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">
                📝 Recent Loop Activity
              </h4>
              {auditLogs.filter(log => log.action.includes('ralph') || log.action.includes('loop')).length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  No loop activity yet. Start the loop to begin autonomous execution.
                </p>
              ) : (
                <div className="space-y-2">
                  {auditLogs
                    .filter(log => log.action.includes('ralph') || log.action.includes('loop'))
                    .slice(0, 10)
                    .map((log) => (
                      <div key={log.id} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-gray-900">{log.action}</span>
                          <span className="text-xs text-gray-500">
                            {formatTimestamp(log.timestamp)}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          Status: <span className="font-medium">{log.status}</span>
                        </p>
                      </div>
                    ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Gold Tier Personal AI Employee Dashboard © 2026
          </p>
        </div>
      </footer>
    </div>
  );
}
