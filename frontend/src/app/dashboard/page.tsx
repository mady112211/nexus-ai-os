'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { dashboardAPI, getToken } from '@/lib/api';

interface DashboardData {
  stats: {
    total_missions: number;
    active_missions: number;
    completed_missions: number;
    total_tasks: number;
    active_agents: number;
  };
  recent_missions: Array<{
    id: number;
    title: string;
    status: string;
    progress: number;
    created_at: string;
  }>;
}

async function fetchDashboard() {
  return await dashboardAPI.get();
}

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();

    if (!token) {
      router.push('/');
      return;
    }

    const loadData = async () => {
      try {
        const result = await fetchDashboard();
        setData(result);
        setLoading(false);
      } catch {
        router.push('/');
      }
    };

    loadData();

    const interval = setInterval(loadData, 4000);

    return () => clearInterval(interval);
  }, [router]);

  const statusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500/20 text-yellow-400',
      running: 'bg-blue-500/20 text-blue-400',
      completed: 'bg-green-500/20 text-green-400',
      failed: 'bg-red-500/20 text-red-400',
    };

    return colors[status] || 'bg-gray-500/20 text-gray-400';
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-400 mt-1">NEXUS AI OS Control Center</p>
        </div>

        {loading ? (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading...
          </div>
        ) : data ? (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
              {[
                { label: 'Total Missions', value: data.stats.total_missions, icon: '🎯' },
                { label: 'Active', value: data.stats.active_missions, icon: '⚡' },
                { label: 'Completed', value: data.stats.completed_missions, icon: '✅' },
                { label: 'Total Tasks', value: data.stats.total_tasks, icon: '📋' },
                { label: 'Agents', value: data.stats.active_agents, icon: '🤖' },
              ].map((stat) => (
                <div key={stat.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                  <div className="text-2xl mb-1">{stat.icon}</div>
                  <div className="text-2xl font-bold">{stat.value}</div>
                  <div className="text-xs text-gray-400">{stat.label}</div>
                </div>
              ))}
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold">Recent Missions</h2>
                <button
                  onClick={() => router.push('/missions')}
                  className="text-blue-400 text-sm hover:text-blue-300"
                >
                  View all →
                </button>
              </div>

              {data.recent_missions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">🎯</div>
                  <p>No missions yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {data.recent_missions.map((mission) => (
                    <div
                      key={mission.id}
                      onClick={() => router.push(`/missions/${mission.id}`)}
                      className="p-4 bg-gray-800 rounded-lg cursor-pointer hover:bg-gray-700 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium text-sm">{mission.title}</div>
                        <span className={`text-xs px-2 py-1 rounded-full ${statusColor(mission.status)}`}>
                          {mission.status}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                        <span>{new Date(mission.created_at).toLocaleDateString()}</span>
                        <span>{mission.progress}% complete</span>
                      </div>

                      <div className="bg-gray-700 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-1.5 rounded-full ${
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
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
}