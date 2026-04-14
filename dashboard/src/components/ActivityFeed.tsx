'use client';

import React from 'react';
import { Activity } from '@/types';

interface ActivityFeedProps {
  activities: Activity[];
}

export default function ActivityFeed({ activities }: ActivityFeedProps) {
  const getEventIcon = (type: string): string => {
    switch (type) {
      case 'plan_generated':
        return '📋';
      case 'task_completed':
        return '✅';
      case 'task_received':
        return '📥';
      case 'task_approved':
        return '✓';
      case 'task_rejected':
        return '✕';
      case 'vault_change':
        return '📁';
      default:
        return '📝';
    }
  };

  const getEventColor = (type: string): string => {
    switch (type) {
      case 'plan_generated':
        return 'text-blue-600 bg-blue-50';
      case 'task_completed':
        return 'text-green-600 bg-green-50';
      case 'task_received':
        return 'text-purple-600 bg-purple-50';
      case 'task_approved':
        return 'text-green-600 bg-green-50';
      case 'task_rejected':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (activities.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No recent activity</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {activities.map((activity, index) => (
        <div key={index} className="flex gap-3">
          <div className={`rounded-full p-2 ${getEventColor(activity.type)}`}>
            <span className="text-lg">{getEventIcon(activity.type)}</span>
          </div>
          <div className="flex-1">
            <p className="text-sm text-gray-900">{activity.description}</p>
            <p className="text-xs text-gray-500 mt-1">{formatTime(activity.timestamp)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
