'use client';

import React from 'react';
import Link from 'next/link';

interface StatsCardProps {
  title: string;
  value: number;
  icon: string;
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  description?: string;
  link?: string;
  onClick?: () => void;
}

export default function StatsCard({ title, value, icon, color, description, link, onClick }: StatsCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
  };

  const iconColorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500',
  };

  const cardContent = (
    <div 
      className={`rounded-lg border p-6 ${colorClasses[color]} transition-shadow hover:shadow-md cursor-pointer`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-80">{title}</p>
          <p className="text-3xl font-bold mt-1">{value.toLocaleString()}</p>
          {description && <p className="text-xs mt-2 opacity-70">{description}</p>}
        </div>
        <div className={`${iconColorClasses[color]} text-white rounded-full p-4`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  );

  if (link) {
    return (
      <Link href={link} className="block hover:scale-105 transition-transform">
        {cardContent}
      </Link>
    );
  }

  return cardContent;
}
