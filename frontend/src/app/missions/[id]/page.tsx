'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, missionAPI } from '@/lib/api';

interface MissionTask {
  id: number;
  task_name: string;
  description?: string;
  assigned_agent: string;
  status: string;
  result: string | null;
}

interface MissionDetail {
  id: number;
  title: string;
  goal: string;
  status: string;
  progress: number;
  result: string | null;
  created_at: string;
  tasks: MissionTask[];
}

async function fetchMission(id: number) {
  return await missionAPI.getOne(id);
}

export default function MissionDetailPage() {
  const params = useParams();
  const router = useRouter();

  const [mission, setMission] = useState<MissionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);

  const missionId = Number(params.id);

  useEffect(() => {
    const token = getToken();

    if (!token) {
      router.push('/');
      return;
    }

    if (!missionId) {
      router.push('/missions');
      return;
    }

    const loadData = async () => {
      try {
        const data = await fetchMission(missionId);
        setMission(data);
        setLoading(false);

        if (data.status === 'running') {
          setExecuting(true);
        } else if (data.status === 'completed' || data.status === 'failed') {
          setExecuting(false);
        }
      } catch {
        router.push('/missions');
      }
    };

    loadData();

    const interval = setInterval(() => {
      loadData();
    }, 3000);

    return () => {
      clearInterval(interval);
    };
  }, [missionId, router]);

  const handleExecute = async () => {
    try {
      setExecuting(true);
      await missionAPI.execute(missionId);

      const updated = await fetchMission(missionId);
      setMission(updated);
    } catch (error) {
      console.error(error);
      setExecuting(false);
    }
  };

  const statusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500/20 text-yellow-400 border-yellow-800',
      running: 'bg-blue-500/20 text-blue-400 border-blue-800',
      completed: 'bg-green-500/20 text-green-400 border-green-800',
      failed: 'bg-red-500/20 text-red-400 border-red-800',
    };

    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-700';
  };

  const statusIcon = (status: string) => {
    const icons: Record<string, string> = {
      pending: '⏳',
      running: '🔄',
      completed: '✅',
      failed: '❌',
    };

    return icons[status] || '⏳';
  };

  const completedTasks =
    mission?.tasks.filter((task) => task.status === 'completed').length || 0;

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <button
            onClick={() => router.push('/missions')}
            className="text-sm text-blue-400 hover:text-blue-300 mb-4"
          >
            ← Back to Missions
          </button>

          {loading ? (
            <div className="flex items-center gap-3 text-gray-400">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              Loading mission...
            </div>
          ) : mission ? (
            <>
              <div className="flex items-start justify-between gap-4 mb-6">
                <div>
                  <h1 className="text-2xl font-bold">{mission.title}</h1>
                  <p className="text-gray-400 mt-2 max-w-3xl">{mission.goal}</p>
                </div>

                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs px-3 py-1 rounded-full border ${statusColor(mission.status)}`}
                  >
                    {statusIcon(mission.status)} {mission.status}
                  </span>

                  {mission.status === 'pending' && (
                    <button
                      onClick={handleExecute}
                      disabled={executing}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                      {executing ? '⏳ Starting...' : '▶️ Execute Mission'}
                    </button>
                  )}

                  {mission.status === 'running' && (
                    <div className="flex items-center gap-2 text-blue-400 text-sm">
                      <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                      Executing...
                    </div>
                  )}
                </div>
              </div>

              <div className="grid md:grid-cols-4 gap-4 mb-8">
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                  <div className="text-sm text-gray-400">Progress</div>
                  <div className="text-2xl font-bold mt-1">{mission.progress}%</div>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                  <div className="text-sm text-gray-400">Tasks</div>
                  <div className="text-2xl font-bold mt-1">{mission.tasks.length}</div>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                  <div className="text-sm text-gray-400">Completed</div>
                  <div className="text-2xl font-bold mt-1">{completedTasks}</div>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
                  <div className="text-sm text-gray-400">Created</div>
                  <div className="text-sm font-medium mt-2">
                    {new Date(mission.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <div className="bg-gray-800 rounded-full h-3 mb-8 overflow-hidden">
                <div
                  className={`h-3 rounded-full transition-all duration-500 ${
                    mission.status === 'completed'
                      ? 'bg-green-500'
                      : mission.status === 'running'
                      ? 'bg-blue-600'
                      : 'bg-yellow-500'
                  }`}
                  style={{ width: `${mission.progress}%` }}
                />
              </div>

              {mission.result && (
                <div className="bg-green-900/20 border border-green-800 rounded-xl p-6 mb-8">
                  <h2 className="text-lg font-semibold text-green-400 mb-3">
                    📋 Final Mission Report
                  </h2>
                  <div className="text-sm text-gray-300 whitespace-pre-wrap leading-7">
                    {mission.result}
                  </div>
                </div>
              )}

              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold mb-4">Mission Tasks</h2>

                <div className="space-y-4">
                  {mission.tasks.map((task, index) => (
                    <div
                      key={task.id}
                      className={`border rounded-lg p-4 ${
                        task.status === 'running'
                          ? 'bg-blue-900/10 border-blue-800'
                          : task.status === 'completed'
                          ? 'bg-green-900/10 border-green-800'
                          : 'bg-gray-800 border-gray-700'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div>
                          <div className="text-xs text-gray-500 mb-1">
                            Task #{index + 1}
                          </div>
                          <h3 className="font-medium">
                            {statusIcon(task.status)} {task.task_name}
                          </h3>
                        </div>

                        <span
                          className={`text-xs px-2 py-1 rounded-full border ${statusColor(task.status)}`}
                        >
                          {task.status}
                        </span>
                      </div>

                      {task.description && (
                        <div className="text-sm text-gray-400 mb-2">
                          {task.description}
                        </div>
                      )}

                      <div className="text-sm text-gray-400 mb-2">
                        <span className="text-gray-500">Agent:</span>{' '}
                        <span className="text-blue-400">
                          {task.assigned_agent || 'Not assigned'}
                        </span>
                      </div>

                      <div className="text-sm text-gray-400">
                        <span className="text-gray-500">Result:</span>{' '}
                        {task.result || 'No result yet'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : null}
        </div>
      </main>
    </div>
  );
}