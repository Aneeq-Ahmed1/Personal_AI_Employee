'use client';

import React, { useState } from 'react';
import { Task } from '@/types';

interface TaskCardProps {
  task: Task;
  onApprove?: (taskId: string) => void;
  onReject?: (taskId: string) => void;
  showActions?: boolean;
}

export default function TaskCard({ task, onApprove, onReject, showActions = false }: TaskCardProps) {
  const [showDetails, setShowDetails] = useState(false);

  const statusColors: Record<string, string> = {
    inbox: 'bg-blue-100 text-blue-800',
    needs_action: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    completed: 'bg-gray-100 text-gray-800',
  };

  const statusLabels: Record<string, string> = {
    inbox: '📥 Inbox',
    needs_action: '⏳ Needs Action',
    approved: '✅ Approved',
    rejected: '❌ Rejected',
    completed: '✓ Completed',
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <>
      <div 
        className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow cursor-pointer"
        onClick={() => setShowDetails(true)}
      >
        <div className="flex items-start justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 flex-1">{task.title}</h3>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[task.status] || statusColors.inbox}`}>
            {statusLabels[task.status] || task.status}
          </span>
        </div>

        {task.summary && (
          <p className="text-gray-600 text-sm mb-3 line-clamp-2">{task.summary}</p>
        )}

        {task.next_step && (
          <div className="bg-blue-50 rounded p-3 mb-3">
            <p className="text-xs font-medium text-blue-700 mb-1">Next Step:</p>
            <p className="text-sm text-blue-900">{task.next_step}</p>
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>📁 {task.source_file}</span>
          <span>🕐 {formatDate(task.created_at)}</span>
        </div>

        {showActions && onApprove && onReject && task.status === 'needs_action' && (
          <div className="flex gap-2 mt-4 pt-4 border-t border-gray-200" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => onApprove(task.id)}
              className="flex-1 bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors font-medium"
            >
              ✓ Approve
            </button>
            <button
              onClick={() => onReject(task.id)}
              className="flex-1 bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors font-medium"
            >
              ✕ Reject
            </button>
          </div>
        )}
      </div>

      {/* Task Details Modal */}
      {showDetails && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setShowDetails(false)}
        >
          <div 
            className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">{task.title}</h2>
              <button
                onClick={() => setShowDetails(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Status</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[task.status] || statusColors.inbox}`}>
                  {statusLabels[task.status] || task.status}
                </span>
              </div>

              {task.summary && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Summary</h3>
                  <p className="text-gray-600 whitespace-pre-wrap">{task.summary}</p>
                </div>
              )}

              {task.next_step && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Next Step</h3>
                  <p className="text-gray-600 whitespace-pre-wrap">{task.next_step}</p>
                </div>
              )}

              {task.content && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-2">Full Content</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans">
                      {task.content}
                    </pre>
                  </div>
                </div>
              )}

              <div className="mb-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Source File</h3>
                <p className="text-gray-600 font-mono text-sm">{task.source_file}</p>
              </div>

              <div className="mb-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Created At</h3>
                <p className="text-gray-600">{formatDate(task.created_at)}</p>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              {showActions && onApprove && onReject && task.status === 'needs_action' && (
                <>
                  <button
                    onClick={() => {
                      onApprove(task.id);
                      setShowDetails(false);
                    }}
                    className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600 transition-colors font-medium"
                  >
                    ✓ Approve
                  </button>
                  <button
                    onClick={() => {
                      onReject(task.id);
                      setShowDetails(false);
                    }}
                    className="bg-red-500 text-white px-6 py-2 rounded-md hover:bg-red-600 transition-colors font-medium"
                  >
                    ✕ Reject
                  </button>
                </>
              )}
              <button
                onClick={() => setShowDetails(false)}
                className="bg-gray-100 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-200 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
