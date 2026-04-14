'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  getStats,
  getInboxTasks,
  getNeedsActionTasks,
  getCompletedTasks,
  getPlans,
  getActivity,
  approveTask,
  rejectTask,
  getBrowserAutomationStatus,
  postToSocialMedia,
  sendWhatsAppMessage,
  sendGmailEmail,
} from '@/lib/api-client';
import { DashboardStats, Task, Activity } from '@/types';
import { getWebSocketClient } from '@/lib/websocket-client';

const platformIcons: Record<string, string> = {
  facebook: '📘',
  instagram: '📷',
  twitter: '🐦',
  linkedin: '💼',
  whatsapp: '💬',
  gmail: '📧',
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  
  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<'inbox' | 'needs_action' | 'completed' | 'plans' | null>(null);
  const [modalData, setModalData] = useState<any[]>([]);
  
  // Browser Automation State
  const [activeTab, setActiveTab] = useState('social');
  const [platformStatus, setPlatformStatus] = useState<any>(null);
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<any>(null);
  const [postMessage, setPostMessage] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['facebook', 'twitter', 'linkedin']);
  const [imagePath, setImagePath] = useState('');
  const [aiGenerating, setAiGenerating] = useState(false);
  
  // WhatsApp Form
  const [whatsappPhone, setWhatsappPhone] = useState('');
  const [whatsappMessage, setWhatsappMessage] = useState('');
  const [whatsappSending, setWhatsappSending] = useState(false);
  const [whatsappResult, setWhatsappResult] = useState<any>(null);
  
  // Gmail Form
  const [gmailTo, setGmailTo] = useState('');
  const [gmailSubject, setGmailSubject] = useState('');
  const [gmailBody, setGmailBody] = useState('');
  const [gmailSending, setGmailSending] = useState(false);
  const [gmailResult, setGmailResult] = useState<any>(null);

  const loadData = async () => {
    console.log('[Dashboard] Starting to load data...');
    try {
      // Load each piece of data separately with logging
      console.log('[Dashboard] Fetching stats...');
      const statsData = await getStats();
      console.log('[Dashboard] Stats loaded:', statsData);
      setStats(statsData);
      
      console.log('[Dashboard] Fetching tasks...');
      const tasksData = await getNeedsActionTasks();
      console.log('[Dashboard] Tasks loaded:', tasksData.tasks?.length);
      setTasks(tasksData.tasks);
      
      console.log('[Dashboard] Fetching activity...');
      const activitiesData = await getActivity(10);
      console.log('[Dashboard] Activity loaded:', activitiesData.activities?.length);
      setActivities(activitiesData.activities);
      
      console.log('[Dashboard] All data loaded successfully!');
    } catch (error) {
      console.error('[Dashboard] Error loading data:', error);
    } finally {
      console.log('[Dashboard] Setting loading to false');
      setLoading(false);
    }
  };

  const loadPlatformStatus = async () => {
    try {
      const status = await getBrowserAutomationStatus();
      setPlatformStatus(status);
    } catch (error) {
      console.error('Error loading platform status:', error);
    }
  };

  useEffect(() => {
    loadPlatformStatus();
  }, []);

  useEffect(() => {
    const ws = getWebSocketClient();
    ws.connect()
      .then(() => {
        console.log('[Dashboard] WebSocket connected');
        setWsConnected(true);
      })
      .catch((err) => {
        console.warn('[Dashboard] WebSocket connection failed (will retry):', err);
        setWsConnected(false);
      });
    loadData();
    return () => ws.disconnect();
  }, []);

  // Open Modal with data
  const openModal = async (type: 'inbox' | 'needs_action' | 'completed' | 'plans') => {
    setModalType(type);
    setModalOpen(true);
    setModalData([]);
    
    try {
      if (type === 'inbox') {
        const data = await getInboxTasks();
        setModalData(data.tasks || []);
        console.log('Inbox data:', data.tasks);
      } else if (type === 'needs_action') {
        const data = await getNeedsActionTasks();
        setModalData(data.tasks || []);
        console.log('Needs Action data:', data.tasks);
      } else if (type === 'completed') {
        const data = await getCompletedTasks();
        setModalData(data.tasks || []);
        console.log('Completed data:', data.tasks);
      } else if (type === 'plans') {
        const data = await getPlans(50);
        setModalData(data.plans || []);
        console.log('Plans data:', data.plans);
      }
    } catch (error) {
      console.error('Error loading modal data:', error);
      setModalData([]);
    }
  };

  const togglePlatform = (platform: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platform) ? prev.filter(p => p !== platform) : [...prev, platform]
    );
  };

  // AI Post Generator - Uses Backend API (OpenRouter/Gemini)
  const generateAIPost = async () => {
    if (!postMessage.trim()) return;

    setAiGenerating(true);
    try {
      console.log('[AI Generate] Sending to AI for enhancement...');

      // Use backend API endpoint instead of direct API call
      const response = await fetch('http://localhost:8000/api/ai/enhance', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: postMessage
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `AI API error: ${response.status}`);
      }

      const data = await response.json();
      const aiEnhanced = data.enhanced_post || postMessage;

      console.log('[AI Generate] Enhanced post:', aiEnhanced);
      setPostMessage(aiEnhanced);

    } catch (error: any) {
      console.error('[AI Generate] Error:', error);
      // Better fallback with variations
      const fallbacks = [
        `🚀 ${postMessage}\n\n#Innovation #Tech #Growth`,
        `✨ ${postMessage}\n\n#Success #Motivation #Goals`,
        `💡 ${postMessage}\n\n#Ideas #Business #Entrepreneur`,
        `🔥 ${postMessage}\n\n#Trending #Viral #Awesome`,
      ];
      const randomFallback = fallbacks[Math.floor(Math.random() * fallbacks.length)];
      setPostMessage(randomFallback);
      console.log('[AI Generate] Using enhanced fallback');
    }
    setAiGenerating(false);
  };

  const handleSocialPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!postMessage.trim()) return;
    setPosting(true);
    setPostResult(null);
    try {
      const result = await postToSocialMedia({
        message: postMessage,
        platforms: selectedPlatforms,
        image_path: imagePath || undefined,
      });
      setPostResult(result);
      if (result.success) {
        setPostMessage('');
        setImagePath('');
      }
    } catch (error: any) {
      setPostResult({ success: false, error: error.message || 'Failed to post' });
    }
    setPosting(false);
  };

  const handleWhatsAppSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!whatsappPhone.trim() || !whatsappMessage.trim()) return;
    setWhatsappSending(true);
    setWhatsappResult(null);
    try {
      const result = await sendWhatsAppMessage({
        phone: whatsappPhone,
        message: whatsappMessage,
      });
      setWhatsappResult(result);
      if (result.success) setWhatsappMessage('');
    } catch (error: any) {
      setWhatsappResult({ success: false, error: error.message || 'Failed to send' });
    }
    setWhatsappSending(false);
  };

  const handleGmailSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!gmailTo.trim() || !gmailSubject.trim() || !gmailBody.trim()) return;
    setGmailSending(true);
    setGmailResult(null);
    try {
      const result = await sendGmailEmail({
        to: gmailTo,
        subject: gmailSubject,
        body: gmailBody,
      });
      setGmailResult(result);
      if (result.success) {
        setGmailTo('');
        setGmailSubject('');
        setGmailBody('');
      }
    } catch (error: any) {
      setGmailResult({ success: false, error: error.message || 'Failed to send' });
    }
    setGmailSending(false);
  };

  const handleApprove = async (taskId: string) => {
    try {
      await approveTask(taskId);
      setTasks(prev => prev.filter(t => t.id !== taskId));
      if (stats) setStats({ ...stats, needs_action_count: stats.needs_action_count - 1 });
    } catch (error) {
      alert('Failed to approve task');
    }
  };

  const handleReject = async (taskId: string) => {
    try {
      await rejectTask(taskId);
      setTasks(prev => prev.filter(t => t.id !== taskId));
      if (stats) setStats({ ...stats, needs_action_count: stats.needs_action_count - 1 });
    } catch (error) {
      alert('Failed to reject task');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-lg shadow-lg border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                🤖 AI Employee Dashboard
              </h1>
              <p className="text-xs text-gray-500 mt-1">Silver Tier • Task Management & Automation</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-full">
                <div className={`w-2.5 h-2.5 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`}></div>
                <span className="text-xs font-medium text-gray-600">{wsConnected ? 'Live' : 'Offline'}</span>
              </div>
              <Link href="/gold-tier" className="px-4 py-2 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:shadow-lg transition-all font-medium text-sm">
                🏆 Gold Tier
              </Link>
              <button onClick={loadData} className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-medium text-sm">
                🔄 Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid - Clickable */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div onClick={() => openModal('inbox')} className="bg-white rounded-2xl shadow-lg border border-blue-200 p-6 hover:shadow-xl hover:scale-105 transition-all cursor-pointer group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">📥 Inbox</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.inbox_count}</p>
                  <p className="text-xs text-gray-500 mt-1">Click to view</p>
                </div>
                <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">📥</div>
              </div>
            </div>

            <div onClick={() => openModal('needs_action')} className="bg-white rounded-2xl shadow-lg border border-yellow-200 p-6 hover:shadow-xl hover:scale-105 transition-all cursor-pointer group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">⏳ Needs Action</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.needs_action_count}</p>
                  <p className="text-xs text-gray-500 mt-1">Click to review</p>
                </div>
                <div className="w-14 h-14 bg-yellow-100 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">⏳</div>
              </div>
            </div>

            <div onClick={() => openModal('completed')} className="bg-white rounded-2xl shadow-lg border border-green-200 p-6 hover:shadow-xl hover:scale-105 transition-all cursor-pointer group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">✅ Completed</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.completed_today}</p>
                  <p className="text-xs text-gray-500 mt-1">Click to view</p>
                </div>
                <div className="w-14 h-14 bg-green-100 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">✅</div>
              </div>
            </div>

            <div onClick={() => openModal('plans')} className="bg-white rounded-2xl shadow-lg border border-purple-200 p-6 hover:shadow-xl hover:scale-105 transition-all cursor-pointer group">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">📋 Total Plans</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stats.total_plans}</p>
                  <p className="text-xs text-gray-500 mt-1">Click to view</p>
                </div>
                <div className="w-14 h-14 bg-purple-100 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">📋</div>
              </div>
            </div>
          </div>
        )}

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Automation & Tasks */}
          <div className="lg:col-span-2 space-y-8">
            {/* Browser Automation Center */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
                <h2 className="text-xl font-bold text-white">🤖 Browser Automation Center</h2>
                <p className="text-sm text-indigo-100 mt-1">AI-powered social media posting • No API keys required</p>
              </div>

              {/* Platform Status */}
              {platformStatus && (
                <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                  <div className="flex items-center gap-4 flex-wrap">
                    {Object.entries(platformStatus.platforms).map(([platform, configured]) => (
                      <div key={platform} className={`flex items-center gap-2 px-3 py-2 rounded-lg ${configured ? 'bg-green-100' : 'bg-gray-200'}`}>
                        <span className="text-lg">{platformIcons[platform]}</span>
                        <span className="text-xs font-medium capitalize text-gray-700">{platform}</span>
                        <span className="text-xs">{configured ? '✅' : '⚠️'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Tabs */}
              <div className="flex border-b border-gray-200">
                <button onClick={() => { setActiveTab('social'); setPostResult(null); }} className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${activeTab === 'social' ? 'bg-indigo-50 text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-600 hover:bg-gray-50'}`}>📱 Social Media</button>
                <button onClick={() => { setActiveTab('whatsapp'); setWhatsappResult(null); }} className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${activeTab === 'whatsapp' ? 'bg-green-50 text-green-600 border-b-2 border-green-600' : 'text-gray-600 hover:bg-gray-50'}`}>💬 WhatsApp</button>
                <button onClick={() => { setActiveTab('gmail'); setGmailResult(null); }} className={`flex-1 px-6 py-3 text-sm font-medium transition-colors ${activeTab === 'gmail' ? 'bg-red-50 text-red-600 border-b-2 border-red-600' : 'text-gray-600 hover:bg-gray-50'}`}>📧 Gmail</button>
              </div>

              {/* Social Media Tab */}
              {activeTab === 'social' && (
                <div className="p-6">
                  <form onSubmit={handleSocialPost} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Your Idea</label>
                      <div className="flex gap-2">
                        <textarea value={postMessage} onChange={(e) => setPostMessage(e.target.value)} className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none" rows={3} placeholder="e.g., New product launch tomorrow!" required />
                        <button type="button" onClick={generateAIPost} disabled={aiGenerating || !postMessage.trim()} className="px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:shadow-lg transition-all font-medium disabled:opacity-50 whitespace-nowrap">
                          {aiGenerating ? '🤖 Generating...' : '✨ AI Generate'}
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 mt-1 text-right">{postMessage.length} characters {postMessage.length > 280 && '⚠️ Twitter limit: 280'}</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Select Platforms</label>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {['facebook', 'twitter', 'linkedin', 'instagram'].map((platform) => (
                          <label key={platform} className={`flex items-center gap-2 p-3 border rounded-xl cursor-pointer transition-all ${selectedPlatforms.includes(platform) ? 'bg-indigo-50 border-indigo-500' : 'hover:bg-gray-50'}`}>
                            <input type="checkbox" checked={selectedPlatforms.includes(platform)} onChange={() => togglePlatform(platform)} className="w-4 h-4 text-indigo-600" />
                            <span className="text-lg">{platformIcons[platform]}</span>
                            <span className="text-sm font-medium capitalize text-gray-700">{platform}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Image Path (Optional)</label>
                      <input type="text" value={imagePath} onChange={(e) => setImagePath(e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent" placeholder="C:/path/to/image.jpg" />
                      <p className="text-xs text-gray-500 mt-1">Required for Instagram posts</p>
                    </div>
                    <button type="submit" disabled={posting || selectedPlatforms.length === 0} className="w-full px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl hover:shadow-lg transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed">{posting ? '🔄 Posting...' : '🚀 Post to Social Media'}</button>
                  </form>
                  {postResult && (
                    <div className={`mt-6 p-4 rounded-xl ${postResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-2xl">{postResult.success ? '✅' : '❌'}</span>
                        <span className="font-semibold text-lg">{postResult.success ? 'Success!' : 'Failed'}</span>
                      </div>
                      {postResult.success ? <p className="text-sm text-gray-700">Posted to {postResult.posted_to} platforms</p> : <p className="text-sm text-red-700">{postResult.error}</p>}
                    </div>
                  )}
                </div>
              )}

              {/* WhatsApp Tab */}
              {activeTab === 'whatsapp' && (
                <div className="p-6">
                  <form onSubmit={handleWhatsAppSend} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                      <input type="tel" value={whatsappPhone} onChange={(e) => setWhatsappPhone(e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent" placeholder="+923001234567" required />
                      <p className="text-xs text-gray-500 mt-1">Include country code (e.g., +92 for Pakistan)</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                      <textarea value={whatsappMessage} onChange={(e) => setWhatsappMessage(e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none" rows={4} placeholder="Type your message..." required />
                    </div>
                    <button type="submit" disabled={whatsappSending} className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:shadow-lg transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed">{whatsappSending ? '🔄 Sending...' : '💬 Send WhatsApp Message'}</button>
                  </form>
                  {whatsappResult && (
                    <div className={`mt-6 p-4 rounded-xl ${whatsappResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{whatsappResult.success ? '✅' : '❌'}</span>
                        <span className="font-semibold">{whatsappResult.success ? 'Message Sent!' : 'Failed'}</span>
                      </div>
                      {whatsappResult.success && <p className="text-sm text-gray-700 mt-2">To: {whatsappResult.recipient}</p>}
                      {whatsappResult.error && <p className="text-sm text-red-700 mt-2">{whatsappResult.error}</p>}
                    </div>
                  )}
                </div>
              )}

              {/* Gmail Tab */}
              {activeTab === 'gmail' && (
                <div className="p-6">
                  <form onSubmit={handleGmailSend} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">To</label>
                      <input type="email" value={gmailTo} onChange={(e) => setGmailTo(e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent" placeholder="recipient@example.com" required />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Subject</label>
                      <input type="text" value={gmailSubject} onChange={(e) => setGmailSubject(e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent" placeholder="Email subject" required />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Body</label>
                      <textarea value={gmailBody} onChange={(e) => setGmailBody(e.target.value)} className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none" rows={6} placeholder="Email body..." required />
                    </div>
                    <button type="submit" disabled={gmailSending} className="w-full px-6 py-3 bg-gradient-to-r from-red-600 to-rose-600 text-white rounded-xl hover:shadow-lg transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed">{gmailSending ? '🔄 Sending...' : '📧 Send Email'}</button>
                  </form>
                  {gmailResult && (
                    <div className={`mt-6 p-4 rounded-xl ${gmailResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{gmailResult.success ? '✅' : '❌'}</span>
                        <span className="font-semibold">{gmailResult.success ? 'Email Sent!' : 'Failed'}</span>
                      </div>
                      {gmailResult.success && <p className="text-sm text-gray-700 mt-2">To: {gmailResult.recipient} • Subject: {gmailResult.subject}</p>}
                      {gmailResult.error && <p className="text-sm text-red-700 mt-2">{gmailResult.error}</p>}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Tasks Section */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900">⏳ Tasks Needing Action</h2>
                <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">{tasks.length} tasks</span>
              </div>
              {tasks.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🎉</div>
                  <p className="text-lg font-medium text-gray-900">All caught up!</p>
                  <p className="text-sm text-gray-500 mt-1">No tasks need your attention</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {tasks.map((task) => (
                    <div key={task.id} className="p-4 border border-gray-200 rounded-xl hover:shadow-md transition-all">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{task.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">{task.summary}</p>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <button onClick={() => handleApprove(task.id)} className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm font-medium">✅ Approve</button>
                          <button onClick={() => handleReject(task.id)} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium">❌ Reject</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Activity Feed */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 sticky top-24">
              <h2 className="text-xl font-bold text-gray-900 mb-4">📝 Recent Activity</h2>
              <div className="space-y-4">
                {activities.length === 0 ? (
                  <p className="text-center text-gray-500 py-8">No recent activity</p>
                ) : (
                  activities.map((activity, idx) => (
                    <div key={idx} className="flex gap-3">
                      <div className="w-2 h-2 rounded-full bg-indigo-500 mt-2 flex-shrink-0"></div>
                      <div className="flex-1">
                        <p className="text-sm text-gray-900">{activity.description}</p>
                        <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setModalOpen(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
              <h2 className="text-xl font-bold text-gray-900">
                {modalType === 'inbox' && `📥 Inbox Tasks (${modalData.length})`}
                {modalType === 'needs_action' && `⏳ Needs Action (${modalData.length})`}
                {modalType === 'completed' && `✅ Completed Tasks (${modalData.length})`}
                {modalType === 'plans' && `📋 AI Generated Plans (${modalData.length})`}
              </h2>
              <button onClick={() => setModalOpen(false)} className="text-gray-500 hover:text-gray-700 text-2xl">×</button>
            </div>
            <div className="p-6">
              {modalData.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📭</div>
                  <p className="text-lg text-gray-500">No items found</p>
                  <p className="text-sm text-gray-400 mt-2">This section is currently empty</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {modalData.map((item: any, idx: number) => (
                    <div key={idx} className="p-4 border border-gray-200 rounded-xl hover:shadow-md transition-all bg-gray-50">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-bold text-gray-900 text-lg">{item.title || item.name || 'Untitled Item'}</h3>
                          {item.summary && <p className="text-sm text-gray-600 mt-2">{item.summary}</p>}
                          {item.content && (
                            <p className="text-sm text-gray-600 mt-2 line-clamp-3">
                              {typeof item.content === 'string' ? item.content.substring(0, 300) : 'No description available'}
                              {item.content.length > 300 && '...'}
                            </p>
                          )}
                          {item.description && <p className="text-sm text-gray-600 mt-2">{item.description}</p>}
                          <div className="flex gap-4 mt-3">
                            {item.status && (
                              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                                Status: {item.status}
                              </span>
                            )}
                            {item.created_at && (
                              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded-full">
                                Created: {item.created_at}
                              </span>
                            )}
                            {item.source_file && (
                              <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                                File: {item.source_file}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">🤖 AI Employee Dashboard • Silver Tier © 2026</p>
        </div>
      </footer>
    </div>
  );
}
