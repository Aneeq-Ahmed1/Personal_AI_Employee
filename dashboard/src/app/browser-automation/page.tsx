'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  getBrowserAutomationStatus,
  postToSocialMedia,
  postToPlatform,
  sendWhatsAppMessage,
  sendGmailEmail,
  getBrowserAutomationHistory,
  BrowserPostData,
  WhatsAppMessageData,
  GmailData,
} from '@/lib/api-client';

interface PlatformStatus {
  name: string;
  configured: boolean;
  icon: string;
  color: string;
}

export default function BrowserAutomationPage() {
  const [loading, setLoading] = useState(true);
  const [platformStatus, setPlatformStatus] = useState<PlatformStatus[]>([]);
  const [activeTab, setActiveTab] = useState<'social' | 'whatsapp' | 'gmail'>('social');
  
  // Social Post Form
  const [postMessage, setPostMessage] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(['facebook', 'twitter', 'linkedin']);
  const [imagePath, setImagePath] = useState('');
  const [posting, setPosting] = useState(false);
  const [postResult, setPostResult] = useState<any>(null);

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

  // Load platform status
  useEffect(() => {
    const loadStatus = async () => {
      try {
        const status = await getBrowserAutomationStatus();
        
        const platforms: PlatformStatus[] = [
          { name: 'facebook', configured: status.platforms.facebook, icon: '📘', color: 'blue' },
          { name: 'instagram', configured: status.platforms.instagram, icon: '📷', color: 'pink' },
          { name: 'twitter', configured: status.platforms.twitter, icon: '🐦', color: 'sky' },
          { name: 'linkedin', configured: status.platforms.linkedin, icon: '💼', color: 'indigo' },
          { name: 'whatsapp', configured: status.platforms.whatsapp, icon: '💬', color: 'green' },
          { name: 'gmail', configured: status.platforms.gmail, icon: '📧', color: 'red' },
        ];
        
        setPlatformStatus(platforms);
      } catch (error) {
        console.error('Error loading browser automation status:', error);
      } finally {
        setLoading(false);
      }
    };

    loadStatus();
  }, []);

  // Toggle platform selection
  const togglePlatform = (platform: string) => {
    setSelectedPlatforms(prev =>
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  // Post to social media
  const handleSocialPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!postMessage.trim()) return;

    setPosting(true);
    setPostResult(null);

    try {
      const data: BrowserPostData = {
        message: postMessage,
        platforms: selectedPlatforms,
        image_path: imagePath || undefined,
      };

      const result = await postToSocialMedia(data);
      setPostResult(result);
    } catch (error: any) {
      setPostResult({
        success: false,
        error: error.message || 'Failed to post',
      });
    } finally {
      setPosting(false);
    }
  };

  // Send WhatsApp message
  const handleWhatsAppSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!whatsappPhone.trim() || !whatsappMessage.trim()) return;

    setWhatsappSending(true);
    setWhatsappResult(null);

    try {
      const data: WhatsAppMessageData = {
        phone: whatsappPhone,
        message: whatsappMessage,
      };

      const result = await sendWhatsAppMessage(data);
      setWhatsappResult(result);
    } catch (error: any) {
      setWhatsappResult({
        success: false,
        error: error.message || 'Failed to send message',
      });
    } finally {
      setWhatsappSending(false);
    }
  };

  // Send Gmail email
  const handleGmailSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!gmailTo.trim() || !gmailSubject.trim() || !gmailBody.trim()) return;

    setGmailSending(true);
    setGmailResult(null);

    try {
      const data: GmailData = {
        to: gmailTo,
        subject: gmailSubject,
        body: gmailBody,
      };

      const result = await sendGmailEmail(data);
      setGmailResult(result);
    } catch (error: any) {
      setGmailResult({
        success: false,
        error: error.message || 'Failed to send email',
      });
    } finally {
      setGmailSending(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading Browser Automation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-600 to-pink-600 text-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm text-purple-100 mb-1">
                <Link href="/" className="hover:text-white">
                  🏠 Dashboard
                </Link>
                <span>/</span>
                <span className="text-white font-medium">🤖 Browser Automation</span>
              </div>
              <h1 className="text-3xl font-bold text-white">
                🤖 Browser Automation Center
              </h1>
              <p className="text-sm text-purple-100 mt-1">
                Post to social media, send messages & emails - No API keys required!
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="px-4 py-2 bg-white text-purple-600 rounded-md hover:bg-purple-50 transition-colors font-medium"
              >
                ← Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Platform Status */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            🔌 Connected Platforms
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {platformStatus.map((platform) => (
              <div
                key={platform.name}
                className={`p-4 rounded-lg border text-center ${
                  platform.configured
                    ? 'bg-green-50 border-green-500'
                    : 'bg-gray-50 border-gray-300'
                }`}
              >
                <div className="text-3xl mb-2">{platform.icon}</div>
                <div className="font-medium text-gray-900 capitalize">{platform.name}</div>
                <div className={`text-xs mt-1 ${
                  platform.configured ? 'text-green-600' : 'text-gray-500'
                }`}>
                  {platform.configured ? '✅ Ready' : '⚠️ Configure credentials'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white border-b border-gray-200 mb-6">
          <nav className="flex gap-4">
            <button
              onClick={() => setActiveTab('social')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'social'
                  ? 'text-purple-600 border-purple-600'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              📱 Social Media Post
            </button>
            <button
              onClick={() => setActiveTab('whatsapp')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'whatsapp'
                  ? 'text-purple-600 border-purple-600'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              💬 WhatsApp Message
            </button>
            <button
              onClick={() => setActiveTab('gmail')}
              className={`px-4 py-3 font-medium transition-colors border-b-2 ${
                activeTab === 'gmail'
                  ? 'text-purple-600 border-purple-600'
                  : 'text-gray-600 border-transparent hover:text-gray-900'
              }`}
            >
              📧 Gmail Email
            </button>
          </nav>
        </div>

        {/* Social Media Tab */}
        {activeTab === 'social' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Post Form */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Create Social Media Post
              </h3>
              <form onSubmit={handleSocialPost} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Post Message *
                  </label>
                  <textarea
                    value={postMessage}
                    onChange={(e) => setPostMessage(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    rows={4}
                    placeholder="What would you like to post?"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Character count: {postMessage.length} (Twitter limit: 280)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Platforms *
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {['facebook', 'twitter', 'linkedin', 'instagram'].map((platform) => (
                      <label
                        key={platform}
                        className="flex items-center gap-2 p-2 border rounded-md cursor-pointer hover:bg-gray-50"
                      >
                        <input
                          type="checkbox"
                          checked={selectedPlatforms.includes(platform)}
                          onChange={() => togglePlatform(platform)}
                          className="w-4 h-4 text-purple-600"
                        />
                        <span className="capitalize">{platform}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Image Path (Optional)
                  </label>
                  <input
                    type="text"
                    value={imagePath}
                    onChange={(e) => setImagePath(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    placeholder="C:/path/to/image.jpg"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Required for Instagram posts
                  </p>
                </div>

                <button
                  type="submit"
                  disabled={posting || selectedPlatforms.length === 0}
                  className="w-full px-4 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {posting ? '🔄 Posting...' : '🚀 Post to Social Media'}
                </button>
              </form>
            </div>

            {/* Results */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Post Results
              </h3>
              {postResult ? (
                <div className="space-y-4">
                  <div className={`p-4 rounded-lg ${
                    postResult.success ? 'bg-green-50' : 'bg-red-50'
                  }`}>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">
                        {postResult.success ? '✅' : '❌'}
                      </span>
                      <span className="font-semibold text-gray-900">
                        {postResult.success ? 'Success!' : 'Failed'}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2">
                      Posted to {postResult.posted_to || 0} platforms
                      {postResult.failed_on > 0 && `, failed on ${postResult.failed_on}`}
                    </p>
                  </div>

                  {postResult.results?.success?.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Successful Posts:</h4>
                      <div className="space-y-2">
                        {postResult.results.success.map((result: any, idx: number) => (
                          <div key={idx} className="p-2 bg-green-50 rounded border border-green-200">
                            <span className="text-sm text-green-800">
                              ✅ {result.platform}: {result.message || 'Posted'}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {postResult.results?.failed?.length > 0 && (
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Failed Posts:</h4>
                      <div className="space-y-2">
                        {postResult.results.failed.map((result: any, idx: number) => (
                          <div key={idx} className="p-2 bg-red-50 rounded border border-red-200">
                            <span className="text-sm text-red-800">
                              ❌ {result.platform}: {result.error}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">📭 No results yet</p>
                  <p className="text-sm mt-1">Fill out the form and post to see results here</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* WhatsApp Tab */}
        {activeTab === 'whatsapp' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Send WhatsApp Message
              </h3>
              <form onSubmit={handleWhatsAppSend} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    value={whatsappPhone}
                    onChange={(e) => setWhatsappPhone(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    placeholder="+1234567890"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Include country code (e.g., +1 for US)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message *
                  </label>
                  <textarea
                    value={whatsappMessage}
                    onChange={(e) => setWhatsappMessage(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    rows={4}
                    placeholder="Type your message..."
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={whatsappSending}
                  className="w-full px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {whatsappSending ? '🔄 Sending...' : '💬 Send WhatsApp Message'}
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Send Results
              </h3>
              {whatsappResult ? (
                <div className={`p-4 rounded-lg ${
                  whatsappResult.success ? 'bg-green-50' : 'bg-red-50'
                }`}>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {whatsappResult.success ? '✅' : '❌'}
                    </span>
                    <span className="font-semibold text-gray-900">
                      {whatsappResult.success ? 'Message Sent!' : 'Failed'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    Recipient: {whatsappResult.recipient}
                  </p>
                  {whatsappResult.error && (
                    <p className="text-sm text-red-600 mt-2">{whatsappResult.error}</p>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">📭 No results yet</p>
                  <p className="text-sm mt-1">Send a message to see results here</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Gmail Tab */}
        {activeTab === 'gmail' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Send Gmail Email
              </h3>
              <form onSubmit={handleGmailSend} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    To *
                  </label>
                  <input
                    type="email"
                    value={gmailTo}
                    onChange={(e) => setGmailTo(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    placeholder="recipient@example.com"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subject *
                  </label>
                  <input
                    type="text"
                    value={gmailSubject}
                    onChange={(e) => setGmailSubject(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    placeholder="Email subject"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Body *
                  </label>
                  <textarea
                    value={gmailBody}
                    onChange={(e) => setGmailBody(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-purple-500 focus:border-purple-500"
                    rows={6}
                    placeholder="Email body..."
                    required
                  />
                </div>

                <button
                  type="submit"
                  disabled={gmailSending}
                  className="w-full px-4 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {gmailSending ? '🔄 Sending...' : '📧 Send Email'}
                </button>
              </form>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Send Results
              </h3>
              {gmailResult ? (
                <div className={`p-4 rounded-lg ${
                  gmailResult.success ? 'bg-green-50' : 'bg-red-50'
                }`}>
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">
                      {gmailResult.success ? '✅' : '❌'}
                    </span>
                    <span className="font-semibold text-gray-900">
                      {gmailResult.success ? 'Email Sent!' : 'Failed'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-2">
                    To: {gmailResult.recipient}<br />
                    Subject: {gmailResult.subject}
                  </p>
                  {gmailResult.error && (
                    <p className="text-sm text-red-600 mt-2">{gmailResult.error}</p>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <p className="text-lg">📭 No results yet</p>
                  <p className="text-sm mt-1">Send an email to see results here</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            Browser Automation - No API Keys Required © 2026
          </p>
          <p className="text-center text-xs text-gray-400 mt-1">
            ⚠️ First-time use requires manual QR code scan for WhatsApp Web
          </p>
        </div>
      </footer>
    </div>
  );
}
