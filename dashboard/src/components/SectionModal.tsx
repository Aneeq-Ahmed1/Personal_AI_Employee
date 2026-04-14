'use client';

import React from 'react';
import { Task, Activity } from '@/types';

interface SectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  icon: string;
  tasks?: Task[];
  activities?: Activity[];
  count?: number;
}

export default function SectionModal({
  isOpen,
  onClose,
  title,
  icon,
  tasks = [],
  activities = [],
  count,
}: SectionModalProps) {
  if (!isOpen) return null;

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
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden my-8"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between bg-gray-50">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{icon}</span>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{title}</h2>
              <p className="text-sm text-gray-500">{count || tasks.length || activities.length} items</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[70vh]">
          {/* Tasks View */}
          {tasks.length > 0 && (
            <div className="space-y-4">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 flex-1">{task.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      task.status === 'needs_action' ? 'bg-yellow-100 text-yellow-800' :
                      task.status === 'approved' ? 'bg-green-100 text-green-800' :
                      task.status === 'rejected' ? 'bg-red-100 text-red-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {task.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>

                  {task.summary && (
                    <p className="text-gray-600 text-sm mb-3">{task.summary}</p>
                  )}

                  {task.next_step && (
                    <div className="bg-blue-50 rounded p-3 mb-3">
                      <p className="text-xs font-medium text-blue-700 mb-1">Next Step:</p>
                      <p className="text-sm text-blue-900">{task.next_step}</p>
                    </div>
                  )}

                  {task.content && (
                    <div className="mb-3">
                      <p className="text-xs font-medium text-gray-700 mb-1">Content:</p>
                      <div className="bg-gray-50 rounded p-3">
                        <pre className="text-sm text-gray-800 whitespace-pre-wrap font-sans max-h-40 overflow-y-auto">
                          {task.content}
                        </pre>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>📁 {task.source_file}</span>
                    <span>🕐 {formatDate(task.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Activities View */}
          {activities.length > 0 && (
            <div className="space-y-3">
              {activities.map((activity, index) => {
                // Determine icon based on activity type
                const getIcon = (type: string) => {
                  if (type.includes('approved')) return '✅';
                  if (type.includes('rejected')) return '❌';
                  if (type.includes('created')) return '📝';
                  if (type.includes('modified')) return '✏️';
                  if (type.includes('deleted')) return '🗑️';
                  return '📌';
                };
                
                return (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <span className="text-xl">{getIcon(activity.type)}</span>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{activity.description}</p>
                      <p className="text-xs text-gray-500 mt-1">{formatDate(activity.timestamp)}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Empty State */}
          {(tasks.length === 0 && activities.length === 0) && (
            <div className="text-center py-12">
              <span className="text-6xl">🎉</span>
              <p className="text-lg text-gray-600 mt-4">No items to show</p>
              <p className="text-sm text-gray-500 mt-2">Everything is up to date!</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
