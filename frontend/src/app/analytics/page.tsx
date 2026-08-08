'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, analyticsAPI } from '@/lib/api';

interface Analytics {
  missions: {
    total: number;
    completed: number;
    running: number;
    pending: number;
    success_rate: number;
  };
  tasks: {
    total: number;
    completed: number;
    avg_per_mission: number;
  };
  agents: Array<{ name: string; count: number }>;
  daily_activity: Array<{ date: string; count: number }>;
  memory: {
    total_saved: number;
  };
}

export default function AnalyticsPage() {
  const router = useRouter();
  const [data, setData] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    analyticsAPI
      .getOverview()
      .then((result) => {
        setData(result);
        setLoading(false);
      })
      .catch(() => {
        router.push('/');
      });
  }, [router]);

  const maxAgentCount = data?.agents.length
    ? Math.max(...data.agents.map((a) => a.count))
    : 1;

  const maxDailyCount = data?.daily_activity.length
    ? Math.max(...data.daily_activity.map((d) => d.count))
    : 1;

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Analytics Dashboard</h1>
          <p className="text-gray-400 mt-1">Deep insights into your NEXUS activity</p>
        </div>

        {loading ? (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading analytics...
          </div>
        ) : data ? (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              <div className="bg-gradient-to-br from-blue-900/40 to-blue-950 border border-blue-800 rounded-xl p-5">
                <div className="text-3xl mb-2">🎯</div>
                <div className="text-3xl font-bold text-blue-400">{data.missions.total}</div>
                <div className="text-xs text-gray-400 mt-1">Total Missions</div>
              </div>

              <div className="bg-gradient-to-br from-green-900/40 to-green-950 border border-green-800 rounded-xl p-5">
                <div className="text-3xl mb-2">✅</div>
                <div className="text-3xl font-bold text-green-400">{data.missions.completed}</div>
                <div className="text-xs text-gray-400 mt-1">Completed</div>
              </div>

              <div className="bg-gradient-to-br from-yellow-900/40 to-yellow-950 border border-yellow-800 rounded-xl p-5">
                <div className="text-3xl mb-2">📋</div>
                <div className="text-3xl font-bold text-yellow-400">{data.tasks.total}</div>
                <div className="text-xs text-gray-400 mt-1">Total Tasks</div>
              </div>

              <div className="bg-gradient-to-br from-purple-900/40 to-purple-950 border border-purple-800 rounded-xl p-5">
                <div className="text-3xl mb-2">🧠</div>
                <div className="text-3xl font-bold text-purple-400">{data.memory.total_saved}</div>
                <div className="text-xs text-gray-400 mt-1">Memories</div>
              </div>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold">📊 Success Rate</h2>
                <span className="text-2xl font-bold text-green-400">{data.missions.success_rate}%</span>
              </div>
              <div className="bg-gray-800 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-green-500 to-green-400 h-4 rounded-full transition-all"
                  style={{ width: `${data.missions.success_rate}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-gray-400 mt-3">
                <span>Pending: {data.missions.pending}</span>
                <span>Running: {data.missions.running}</span>
                <span>Completed: {data.missions.completed}</span>
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6 mb-8">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="font-semibold mb-4">🤖 Agent Usage</h2>
                {data.agents.length === 0 ? (
                  <div className="text-gray-500 text-sm">No agent data yet</div>
                ) : (
                  <div className="space-y-3">
                    {data.agents.map((agent) => (
                      <div key={agent.name}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-300">{agent.name}</span>
                          <span className="text-sm font-bold text-blue-400">{agent.count}</span>
                        </div>
                        <div className="bg-gray-800 rounded-full h-2 overflow-hidden">
                          <div
                            className="bg-blue-500 h-2 rounded-full transition-all"
                            style={{ width: `${(agent.count / maxAgentCount) * 100}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="font-semibold mb-4">📈 7-Day Activity</h2>
                {data.daily_activity.length === 0 ? (
                  <div className="text-gray-500 text-sm">No activity in last 7 days</div>
                ) : (
                  <div className="flex items-end gap-2 h-40">
                    {data.daily_activity.map((day) => (
                      <div key={day.date} className="flex-1 flex flex-col items-center gap-2">
                        <div className="text-xs text-gray-400">{day.count}</div>
                        <div
                          className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t transition-all"
                          style={{
                            height: `${(day.count / maxDailyCount) * 100}%`,
                            minHeight: '4px',
                          }}
                        />
                        <div className="text-xs text-gray-500">{day.date.slice(5)}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold mb-4">📋 Task Statistics</h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-800 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-blue-400">{data.tasks.total}</div>
                  <div className="text-xs text-gray-400 mt-1">Total Tasks</div>
                </div>
                <div className="bg-gray-800 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-green-400">{data.tasks.completed}</div>
                  <div className="text-xs text-gray-400 mt-1">Completed</div>
                </div>
                <div className="bg-gray-800 rounded-xl p-4 text-center">
                  <div className="text-3xl font-bold text-purple-400">{data.tasks.avg_per_mission}</div>
                  <div className="text-xs text-gray-400 mt-1">Avg per Mission</div>
                </div>
              </div>
            </div>
          </>
        ) : null}
      </main>
    </div>
  );
}