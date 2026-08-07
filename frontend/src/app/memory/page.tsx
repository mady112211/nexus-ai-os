'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, memoryAPI } from '@/lib/api';

interface MemoryItem {
  id: number;
  memory_type: string;
  content: string;
  parsed_content: unknown;
  importance: number;
  created_at: string;
}

export default function MemoryPage() {
  const router = useRouter();

  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [lastContext, setLastContext] = useState<MemoryItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [prefTitle, setPrefTitle] = useState('');
  const [prefValue, setPrefValue] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const token = getToken();

    if (!token) {
      router.push('/');
      return;
    }

    const loadData = async () => {
      try {
        const memoryData = await memoryAPI.getAll();
        const contextData = await memoryAPI.getLastContext();

        setMemories(memoryData.memories || []);
        setLastContext(contextData.last_project_context || null);
        setLoading(false);
      } catch {
        router.push('/');
      }
    };

    loadData();
  }, [router]);

  const handleSavePreference = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!prefTitle || !prefValue) return;

    try {
      setSaving(true);
      await memoryAPI.savePreference(prefTitle, prefValue);

      const memoryData = await memoryAPI.getAll();
      setMemories(memoryData.memories || []);

      setPrefTitle('');
      setPrefValue('');
    } finally {
      setSaving(false);
    }
  };

  const renderContent = (memory: MemoryItem) => {
    if (
      memory.parsed_content &&
      typeof memory.parsed_content === 'object' &&
      !Array.isArray(memory.parsed_content)
    ) {
      const obj = memory.parsed_content as Record<string, unknown>;

      return (
        <div className="space-y-2 text-sm">
          {Object.entries(obj).map(([key, value]) => (
            <div key={key}>
              <span className="text-gray-500 capitalize">
                {key.replace(/_/g, ' ')}:
              </span>{' '}
              <span className="text-gray-300">
                {String(value)}
              </span>
            </div>
          ))}
        </div>
      );
    }

    return <div className="text-sm text-gray-300">{memory.content}</div>;
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Memory</h1>
          <p className="text-gray-400 mt-1">Project history, preferences and saved intelligence</p>
        </div>

        {loading ? (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading memory...
          </div>
        ) : (
          <>
            {lastContext && (
              <div className="bg-blue-900/20 border border-blue-800 rounded-xl p-6 mb-6">
                <h2 className="text-lg font-semibold text-blue-400 mb-3">
                  🧠 Last Project Context
                </h2>
                {renderContent(lastContext)}
              </div>
            )}

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4">Save Preference</h2>

              <form onSubmit={handleSavePreference} className="space-y-4">
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Preference Title</label>
                  <input
                    type="text"
                    value={prefTitle}
                    onChange={(e) => setPrefTitle(e.target.value)}
                    placeholder="e.g. Report Style"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Preference Value</label>
                  <textarea
                    value={prefValue}
                    onChange={(e) => setPrefValue(e.target.value)}
                    placeholder="e.g. I prefer detailed professional reports with bullet points"
                    rows={3}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none"
                  />
                </div>

                <button
                  type="submit"
                  disabled={saving}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  {saving ? 'Saving...' : 'Save Preference'}
                </button>
              </form>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-lg font-semibold mb-4">Saved Memories</h2>

              {memories.length === 0 ? (
                <div className="text-gray-500 text-sm">No memories yet.</div>
              ) : (
                <div className="space-y-4">
                  {memories.map((memory) => (
                    <div
                      key={memory.id}
                      className="bg-gray-800 border border-gray-700 rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="text-sm font-medium text-white">
                          {memory.memory_type}
                        </div>
                        <div className="text-xs text-gray-500">
                          {new Date(memory.created_at).toLocaleString()}
                        </div>
                      </div>

                      {renderContent(memory)}

                      <div className="mt-3 text-xs text-gray-500">
                        Importance: {memory.importance}/10
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </main>
    </div>
  );
}