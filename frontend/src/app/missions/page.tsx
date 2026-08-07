'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { missionAPI, getToken } from '@/lib/api';

interface Mission {
  id: number;
  title: string;
  goal: string;
  status: string;
  progress: number;
  created_at: string;
}

async function fetchMissions() {
  return await missionAPI.getAll();
}

export default function MissionsPage() {
  const router = useRouter();
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ title: '', goal: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    let interval: NodeJS.Timeout;

    const loadData = async () => {
      try {
        const data = await fetchMissions();
        setMissions(data.missions);
        setLoading(false);
      } catch {
        router.push('/');
      }
    };

    loadData();
    interval = setInterval(loadData, 4000);

    return () => clearInterval(interval);
  }, [router]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.goal) return;

    setCreating(true);
    setError('');

    try {
      await missionAPI.create(form.goal, form.title || form.goal.slice(0, 50));
      setForm({ title: '', goal: '' });
      setShowForm(false);

      const data = await fetchMissions();
      setMissions(data.missions);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create mission');
    } finally {
      setCreating(false);
    }
  };

  const statusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-800',
      running: 'bg-blue-500/20 text-blue-400 border-blue-800',
      completed: 'bg-green-500/20 text-green-400 border-green-800',
      failed: 'bg-red-500/20 text-red-400 border-red-800',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-800';
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Missions</h1>
            <p className="text-gray-400 mt-1">Create and manage AI missions</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            + New Mission
          </button>
        </div>

        {showForm && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
            <h2 className="font-semibold mb-4">Create New Mission</h2>

            {error && (
              <div className="bg-red-900/30 border border-red-800 text-red-400 rounded-lg p-3 mb-4 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-1 block">Title (optional)</label>
                <input
                  type="text"
                  placeholder="Mission title..."
                  value={form.title}
                  onChange={(e) => setForm({ ...form, title: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1 block">Goal *</label>
                <textarea
                  placeholder="What do you want NEXUS to do?..."
                  value={form.goal}
                  onChange={(e) => setForm({ ...form, goal: e.target.value })}
                  rows={3}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                  required
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  {creating ? 'Creating...' : 'Create Mission'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading missions...
          </div>
        ) : missions.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-6xl mb-4">🎯</div>
            <h3 className="text-lg font-medium text-gray-400 mb-2">No missions yet</h3>
            <p className="text-sm mb-4">Create your first AI mission</p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium"
            >
              Create Mission
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {missions.map((mission) => (
              <div
                key={mission.id}
                onClick={() => router.push(`/missions/${mission.id}`)}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-gray-700 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold">{mission.title}</h3>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full border ${statusColor(mission.status)}`}
                      >
                        {mission.status}
                      </span>
                    </div>

                    <p className="text-sm text-gray-400 mb-3">{mission.goal}</p>

                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span>📅 {new Date(mission.created_at).toLocaleDateString()}</span>
                      <span>📊 {mission.progress}% complete</span>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/missions/${mission.id}`);
                    }}
                    className="text-sm text-blue-400 hover:text-blue-300"
                  >
                    View →
                  </button>
                </div>

                <div className="mt-4 bg-gray-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-1.5 rounded-full transition-all ${
                      mission.status === 'completed'
                        ? 'bg-green-500'
                        : mission.status === 'running'
                        ? 'bg-blue-600'
                        : 'bg-yellow-500'
                    }`}
                    style={{ width: `${mission.progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}