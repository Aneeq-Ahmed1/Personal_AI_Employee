'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { getStats, getVaultFile } from '@/lib/api-client';
import { DashboardStats } from '@/types';

export default function SettingsPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'general' | 'integrations' | 'vault'>('general');

  // Load stats
  useEffect(() => {
    const loadStats = async () => {
      try {
        const statsData = await getStats();
        setStats(statsData);
      } catch (error) {
        console.error('Error loading stats:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm text-gray-500 mb-1">
                <Link href="/" className="hover:text-blue-600">
                  🏠 Dashboard
                </Link>
                <span>/</span>
                <span className="text-gray-900 font-medium">⚙️ Settings</span>
              </div>
              <h1 className="text-2xl font-bold text-gray-900">
                ⚙️ Settings
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Configure your Personal AI Employee
              </p>
            </div>
            <Link
              href="/"
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
            >
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg border border-gray-200 mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('general')}
                className={`px-6 py-3 text-sm font-medium ${
                  activeTab === 'general'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📊 System Status
              </button>
              <button
                onClick={() => setActiveTab('integrations')}
                className={`px-6 py-3 text-sm font-medium ${
                  activeTab === 'integrations'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                🔗 Integrations
              </button>
              <button
                onClick={() => setActiveTab('vault')}
                className={`px-6 py-3 text-sm font-medium ${
                  activeTab === 'vault'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                📁 Vault Status
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'general' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    📊 System Status
                  </h2>
                  
                  {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Inbox Tasks</p>
                            <p className="text-2xl font-bold text-blue-600">{stats.inbox_count}</p>
                          </div>
                          <span className="text-3xl">📥</span>
                        </div>
                      </div>
                      
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Needs Action</p>
                            <p className="text-2xl font-bold text-yellow-600">{stats.needs_action_count}</p>
                          </div>
                          <span className="text-3xl">⏳</span>
                        </div>
                      </div>
                      
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Completed Today</p>
                            <p className="text-2xl font-bold text-green-600">{stats.completed_today}</p>
                          </div>
                          <span className="text-3xl">✅</span>
                        </div>
                      </div>
                      
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Total Plans</p>
                            <p className="text-2xl font-bold text-purple-600">{stats.total_plans}</p>
                          </div>
                          <span className="text-3xl">📋</span>
                        </div>
                      </div>
                      
                      <div className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-sm text-gray-500">Total Completed</p>
                            <p className="text-2xl font-bold text-gray-600">{stats.total_tasks_completed}</p>
                          </div>
                          <span className="text-3xl">🏆</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-md font-semibold text-gray-900 mb-3">
                    ℹ️ System Information
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-500">Tier</span>
                      <span className="font-medium text-gray-900">Silver</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-500">Version</span>
                      <span className="font-medium text-gray-900">1.0.0</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-500">API Server</span>
                      <span className="font-medium text-gray-900">http://localhost:8000</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-500">Dashboard</span>
                      <span className="font-medium text-gray-900">http://localhost:3000</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-500">Vault Path</span>
                      <span className="font-medium text-gray-900 font-mono text-xs">
                        silver/vault/
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'integrations' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    🔗 Connected Integrations
                  </h2>
                  
                  <div className="space-y-4">
                    {/* Gmail Integration */}
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">📧</span>
                          <div>
                            <h3 className="font-semibold text-gray-900">Gmail Watcher</h3>
                            <p className="text-sm text-gray-500">Monitor Gmail for new emails</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            Active
                          </span>
                        </div>
                      </div>
                      <div className="mt-3 text-sm text-gray-600">
                        <p>Monitors: INBOX, SPAM folders</p>
                        <p>Labels processed: Personal AI Employee</p>
                      </div>
                    </div>

                    {/* File System Watcher */}
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">📁</span>
                          <div>
                            <h3 className="font-semibold text-gray-900">File System Watcher</h3>
                            <p className="text-sm text-gray-500">Monitor folders for new files</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            Active
                          </span>
                        </div>
                      </div>
                      <div className="mt-3 text-sm text-gray-600">
                        <p>Watched folders: Inbox, Downloads</p>
                        <p>Auto-triage: Enabled</p>
                      </div>
                    </div>

                    {/* Reasoning Engine */}
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">🧠</span>
                          <div>
                            <h3 className="font-semibold text-gray-900">Claude Reasoning Engine</h3>
                            <p className="text-sm text-gray-500">AI planning and execution</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            Active
                          </span>
                        </div>
                      </div>
                      <div className="mt-3 text-sm text-gray-600">
                        <p>Auto-trigger: Enabled</p>
                        <p>Fallback mode: Available</p>
                      </div>
                    </div>

                    {/* Dashboard API */}
                    <div className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">📊</span>
                          <div>
                            <h3 className="font-semibold text-gray-900">Dashboard API</h3>
                            <p className="text-sm text-gray-500">Real-time task management</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                            Active
                          </span>
                        </div>
                      </div>
                      <div className="mt-3 text-sm text-gray-600">
                        <p>WebSocket: Connected</p>
                        <p>Port: 8000</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-md font-semibold text-gray-900 mb-3">
                    📝 Configuration
                  </h3>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-sm text-yellow-800">
                      <strong>Note:</strong> Configuration changes require editing the <code className="bg-yellow-100 px-1 rounded">.env</code> file 
                      in the project root directory. After making changes, restart the services.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'vault' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    📁 Vault Structure
                  </h2>
                  
                  <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-blue-600">📁</span>
                        <span className="text-gray-700">silver/vault/</span>
                      </div>
                      <div className="flex items-center gap-2 pl-4">
                        <span className="text-yellow-600">📁</span>
                        <span className="text-gray-700">Inbox/</span>
                        <span className="text-gray-400 text-xs">({stats?.inbox_count} files)</span>
                      </div>
                      <div className="flex items-center gap-2 pl-4">
                        <span className="text-orange-600">📁</span>
                        <span className="text-gray-700">Needs_Action/</span>
                        <span className="text-gray-400 text-xs">({stats?.needs_action_count} files)</span>
                      </div>
                      <div className="flex items-center gap-2 pl-4">
                        <span className="text-purple-600">📁</span>
                        <span className="text-gray-700">Plans/</span>
                        <span className="text-gray-400 text-xs">({stats?.total_plans} files)</span>
                      </div>
                      <div className="flex items-center gap-2 pl-4">
                        <span className="text-red-600">📁</span>
                        <span className="text-gray-700">Approvals/</span>
                      </div>
                      <div className="flex items-center gap-2 pl-4">
                        <span className="text-green-600">📁</span>
                        <span className="text-gray-700">Completed/</span>
                        <span className="text-gray-400 text-xs">({stats?.total_tasks_completed} files)</span>
                      </div>
                      <div className="flex items-center gap-2 pl-4">
                        <span className="text-gray-600">📁</span>
                        <span className="text-gray-700">Generated/</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-md font-semibold text-gray-900 mb-3">
                    📊 Vault Statistics
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <p className="text-2xl font-bold text-blue-600">{stats?.inbox_count || 0}</p>
                      <p className="text-xs text-gray-500 mt-1">Inbox</p>
                    </div>
                    <div className="text-center p-4 bg-yellow-50 rounded-lg">
                      <p className="text-2xl font-bold text-yellow-600">{stats?.needs_action_count || 0}</p>
                      <p className="text-xs text-gray-500 mt-1">Needs Action</p>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <p className="text-2xl font-bold text-purple-600">{stats?.total_plans || 0}</p>
                      <p className="text-xs text-gray-500 mt-1">Plans</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <p className="text-2xl font-bold text-green-600">{stats?.completed_today || 0}</p>
                      <p className="text-xs text-gray-500 mt-1">Today</p>
                    </div>
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                      <p className="text-2xl font-bold text-gray-600">{stats?.total_tasks_completed || 0}</p>
                      <p className="text-xs text-gray-500 mt-1">Total</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Silver Tier Personal AI Employee Dashboard © 2026
          </p>
        </div>
      </footer>
    </div>
  );
}
