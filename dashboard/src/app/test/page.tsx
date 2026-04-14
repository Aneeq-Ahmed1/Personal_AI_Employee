'use client';

import { useState, useEffect } from 'react';

export default function TestPage() {
  const [count, setCount] = useState(0);
  const [apiStatus, setApiStatus] = useState('loading');

  useEffect(() => {
    console.log('[Test Page] Component mounted');
    
    // Test API call
    fetch('http://localhost:8000/api/stats')
      .then(res => res.json())
      .then(data => {
        console.log('[Test Page] API response:', data);
        setApiStatus('connected: ' + JSON.stringify(data));
      })
      .catch(err => {
        console.error('[Test Page] API error:', err);
        setApiStatus('error: ' + err.message);
      });
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold mb-4">🧪 Test Page</h1>
        <p className="mb-4">Count: {count}</p>
        <button 
          onClick={() => setCount(count + 1)}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Increment
        </button>
        <p className="mt-4 text-sm text-gray-600">API Status: {apiStatus}</p>
        <p className="mt-2 text-xs text-gray-400">Check browser console for logs</p>
      </div>
    </div>
  );
}
