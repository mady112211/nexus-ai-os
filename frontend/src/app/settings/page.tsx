'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, settingsAPI, removeToken } from '@/lib/api';

interface Profile {
  id: number;
  name: string;
  email: string;
  role: string;
  created_at: string;
}

interface AISettings {
  default_model: string;
  provider: string;
  free_models: string[];
  api_key_set: boolean;
}

interface Stats {
  total_missions: number;
  completed_missions: number;
  total_tasks: number;
  total_memories: number;
  success_rate: number;
}

export default function SettingsPage() {
  const router = useRouter();

  const [profile, setProfile] = useState<Profile | null>(null);
  const [aiSettings, setAISettings] = useState<AISettings | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  const [editName, setEditName] = useState('');
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMsg, setProfileMsg] = useState('');

  const [selectedModel, setSelectedModel] = useState('');
  const [responseStyle, setResponseStyle] = useState('professional');
  const [savingAI, setSavingAI] = useState(false);
  const [aiMsg, setAIMsg] = useState('');

  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    const loadAll = async () => {
      try {
        const [profileData, aiData, statsData] = await Promise.all([
          settingsAPI.getProfile(),
          settingsAPI.getAISettings(),
          settingsAPI.getStats(),
        ]);

        setProfile(profileData);
        setEditName(profileData.name);
        setAISettings(aiData);
        setSelectedModel(aiData.default_model);
        setStats(statsData);
        setLoading(false);
      } catch {
        router.push('/');
      }
    };

    loadAll();
  }, [router]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingProfile(true);
    setProfileMsg('');

    try {
      await settingsAPI.updateProfile(editName);
      setProfileMsg('✅ Profile updated successfully');
      if (profile) {
        setProfile({ ...profile, name: editName });
      }
    } catch {
      setProfileMsg('❌ Failed to update profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleSaveAI = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingAI(true);
    setAIMsg('');

    try {
      await settingsAPI.updateAISettings(selectedModel, responseStyle);
      setAIMsg('✅ AI settings saved successfully');
    } catch {
      setAIMsg('❌ Failed to save AI settings');
    } finally {
      setSavingAI(false);
    }
  };

  const handleLogout = () => {
    removeToken();
    router.push('/');
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: '👤' },
    { id: 'ai', label: 'AI Settings', icon: '🤖' },
    { id: 'stats', label: 'Statistics', icon: '📊' },
    { id: 'system', label: 'System', icon: '⚙️' },
  ];

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Settings</h1>
          <p className="text-gray-400 mt-1">
            Configure your NEXUS AI OS
          </p>
        </div>

        {loading ? (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading settings...
          </div>
        ) : (
          <div className="flex gap-6">
            {/* Tab Navigation */}
            <div className="w-48 shrink-0">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-2 space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                    }`}
                  >
                    <span>{tab.icon}</span>
                    <span>{tab.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Tab Content */}
            <div className="flex-1">
              {/* Profile Tab */}
              {activeTab === 'profile' && profile && (
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h2 className="text-lg font-semibold mb-6">Profile Settings</h2>

                  <div className="flex items-center gap-4 mb-6">
                    <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-2xl font-bold">
                      {profile.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="font-semibold text-lg">{profile.name}</div>
                      <div className="text-gray-400 text-sm">{profile.email}</div>
                      <div className="text-xs text-blue-400 mt-1 capitalize">
                        {profile.role}
                      </div>
                    </div>
                  </div>

                  <form onSubmit={handleSaveProfile} className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-400 mb-1 block">
                        Display Name
                      </label>
                      <input
                        type="text"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                      />
                    </div>

                    <div>
                      <label className="text-sm text-gray-400 mb-1 block">
                        Email
                      </label>
                      <input
                        type="email"
                        value={profile.email}
                        disabled
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-500 cursor-not-allowed"
                      />
                    </div>

                    <div>
                      <label className="text-sm text-gray-400 mb-1 block">
                        Member Since
                      </label>
                      <input
                        type="text"
                        value={new Date(profile.created_at).toLocaleDateString()}
                        disabled
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-500 cursor-not-allowed"
                      />
                    </div>

                    {profileMsg && (
                      <div className="text-sm text-gray-300">{profileMsg}</div>
                    )}

                    <button
                      type="submit"
                      disabled={savingProfile}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      {savingProfile ? 'Saving...' : 'Save Profile'}
                    </button>
                  </form>
                </div>
              )}

              {/* AI Settings Tab */}
              {activeTab === 'ai' && aiSettings && (
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h2 className="text-lg font-semibold mb-6">AI Settings</h2>

                  <div className="mb-4 flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        aiSettings.api_key_set ? 'bg-green-500' : 'bg-red-500'
                      }`}
                    />
                    <span className="text-sm text-gray-400">
                      OpenRouter API:{' '}
                      {aiSettings.api_key_set ? 'Connected ✅' : 'Not configured ❌'}
                    </span>
                  </div>

                  <form onSubmit={handleSaveAI} className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-400 mb-1 block">
                        Default AI Model
                      </label>
                      <select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                      >
                        {aiSettings.free_models.map((model) => (
                          <option key={model} value={model}>
                            {model}
                          </option>
                        ))}
                      </select>
                      <p className="text-xs text-gray-500 mt-1">
                        These are free models from OpenRouter
                      </p>
                    </div>

                    <div>
                      <label className="text-sm text-gray-400 mb-1 block">
                        Response Style
                      </label>
                      <select
                        value={responseStyle}
                        onChange={(e) => setResponseStyle(e.target.value)}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                      >
                        <option value="professional">Professional</option>
                        <option value="detailed">Detailed</option>
                        <option value="concise">Concise</option>
                        <option value="creative">Creative</option>
                      </select>
                    </div>

                    {aiMsg && (
                      <div className="text-sm text-gray-300">{aiMsg}</div>
                    )}

                    <button
                      type="submit"
                      disabled={savingAI}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      {savingAI ? 'Saving...' : 'Save AI Settings'}
                    </button>
                  </form>
                </div>
              )}

              {/* Stats Tab */}
              {activeTab === 'stats' && stats && (
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <h2 className="text-lg font-semibold mb-6">Your Statistics</h2>

                  <div className="grid grid-cols-2 gap-4 mb-6">
                    {[
                      {
                        label: 'Total Missions',
                        value: stats.total_missions,
                        icon: '🎯',
                        color: 'text-blue-400',
                      },
                      {
                        label: 'Completed',
                        value: stats.completed_missions,
                        icon: '✅',
                        color: 'text-green-400',
                      },
                      {
                        label: 'Total Tasks',
                        value: stats.total_tasks,
                        icon: '📋',
                        color: 'text-yellow-400',
                      },
                      {
                        label: 'Memories Saved',
                        value: stats.total_memories,
                        icon: '🧠',
                        color: 'text-purple-400',
                      },
                    ].map((stat) => (
                      <div
                        key={stat.label}
                        className="bg-gray-800 border border-gray-700 rounded-xl p-4"
                      >
                        <div className="text-2xl mb-1">{stat.icon}</div>
                        <div className={`text-3xl font-bold ${stat.color}`}>
                          {stat.value}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          {stat.label}
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-400">Success Rate</span>
                      <span className="text-sm font-bold text-green-400">
                        {stats.success_rate}%
                      </span>
                    </div>
                    <div className="bg-gray-700 rounded-full h-3 overflow-hidden">
                      <div
                        className="bg-green-500 h-3 rounded-full transition-all"
                        style={{ width: `${stats.success_rate}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* System Tab */}
              {activeTab === 'system' && (
                <div className="space-y-4">
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h2 className="text-lg font-semibold mb-4">System Info</h2>

                    <div className="space-y-3">
                      {[
                        { label: 'Version', value: 'NEXUS AI OS v0.5.0' },
                        { label: 'Backend', value: 'Flask + Python' },
                        { label: 'Frontend', value: 'Next.js + Tailwind' },
                        { label: 'Database', value: 'SQLite' },
                        { label: 'AI Provider', value: 'OpenRouter' },
                        { label: 'Status', value: '🟢 All Systems Operational' },
                      ].map((item) => (
                        <div
                          key={item.label}
                          className="flex items-center justify-between py-2 border-b border-gray-800"
                        >
                          <span className="text-sm text-gray-400">
                            {item.label}
                          </span>
                          <span className="text-sm text-white">{item.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h2 className="text-lg font-semibold mb-4">Account</h2>

                    <button
                      onClick={handleLogout}
                      className="w-full bg-red-900/30 border border-red-800 hover:bg-red-900/50 text-red-400 px-4 py-3 rounded-lg text-sm font-medium transition-colors"
                    >
                      🚪 Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}