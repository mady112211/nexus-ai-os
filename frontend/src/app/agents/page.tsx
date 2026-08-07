'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { agentAPI, getToken } from '@/lib/api';

interface Agent {
  id: number;
  name: string;
  role: string;
  description: string;
  is_active: boolean;
  status: string;
}

async function fetchAgents() {
  return await agentAPI.getAll();
}

export default function AgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    fetchAgents()
      .then((data) => {
        setAgents(data.agents);
        setLoading(false);
      })
      .catch(() => {
        router.push('/');
      });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const statusColor = (active: boolean) => {
    return active
      ? 'bg-green-500/20 text-green-400 border-green-800'
      : 'bg-gray-500/20 text-gray-400 border-gray-700';
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Agents</h1>
          <p className="text-gray-400 mt-1">Your AI workforce</p>
        </div>

        {loading ? (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading agents...
          </div>
        ) : agents.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-6xl mb-4">🤖</div>
            <h3 className="text-lg font-medium text-gray-400 mb-2">No agents found</h3>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="font-semibold text-lg">{agent.name}</h3>
                    <p className="text-sm text-blue-400 mt-1">{agent.role}</p>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full border ${statusColor(agent.is_active)}`}
                  >
                    {agent.is_active ? 'ready' : 'offline'}
                  </span>
                </div>

                <p className="text-sm text-gray-400 mb-4">
                  {agent.description || 'No description available'}
                </p>

                <div className="pt-4 border-t border-gray-800">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-500">Agent ID</span>
                    <span className="text-gray-300">#{agent.id}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}