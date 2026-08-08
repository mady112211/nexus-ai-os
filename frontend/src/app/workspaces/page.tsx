'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, workspaceAPI } from '@/lib/api';

interface Workspace {
  id: number;
  name: string;
  description: string;
  icon: string;
  is_owner: boolean;
  created_at: string;
}

export default function WorkspacesPage() {
  const router = useRouter();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', description: '', icon: '🏢' });
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    workspaceAPI
      .getAll()
      .then((data) => {
        setWorkspaces(data.workspaces || []);
        setLoading(false);
      })
      .catch(() => router.push('/'));
  }, [router]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name) return;

    setCreating(true);
    try {
      await workspaceAPI.create(form.name, form.description, form.icon);
      setForm({ name: '', description: '', icon: '🏢' });
      setShowForm(false);
      const data = await workspaceAPI.getAll();
      setWorkspaces(data.workspaces || []);
    } finally {
      setCreating(false);
    }
  };

  const icons = ['🏢', '🚀', '💼', '⭐', '🎯', '💡', '🔥', '⚡'];

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold">Workspaces</h1>
            <p className="text-gray-400 mt-1">Collaborate with your team</p>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
          >
            + New Workspace
          </button>
        </div>

        {showForm && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
            <h2 className="font-semibold mb-4">Create Workspace</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Icon</label>
                <div className="flex gap-2 flex-wrap">
                  {icons.map((icon) => (
                    <button
                      key={icon}
                      type="button"
                      onClick={() => setForm({ ...form, icon })}
                      className={`w-12 h-12 rounded-lg text-2xl transition-colors ${
                        form.icon === icon
                          ? 'bg-blue-600'
                          : 'bg-gray-800 hover:bg-gray-700'
                      }`}
                    >
                      {icon}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1 block">Name *</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="My Team"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1 block">
                  Description
                </label>
                <textarea
                  value={form.description}
                  onChange={(e) =>
                    setForm({ ...form, description: e.target.value })
                  }
                  rows={2}
                  placeholder="What's this workspace for?"
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-2 rounded-lg text-sm font-medium"
                >
                  {creating ? 'Creating...' : 'Create Workspace'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded-lg text-sm font-medium"
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
            Loading workspaces...
          </div>
        ) : workspaces.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <div className="text-6xl mb-4">🏢</div>
            <h3 className="text-lg font-medium text-gray-400 mb-2">
              No workspaces yet
            </h3>
            <p className="text-sm mb-4">
              Create your first workspace to collaborate
            </p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium"
            >
              Create Workspace
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workspaces.map((ws) => (
              <div
                key={ws.id}
                onClick={() => router.push(`/workspaces/${ws.id}`)}
                className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-blue-800 hover:bg-blue-900/10 cursor-pointer transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="text-4xl">{ws.icon}</div>
                  {ws.is_owner && (
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full">
                      Owner
                    </span>
                  )}
                </div>
                <h3 className="font-semibold text-lg mb-1">{ws.name}</h3>
                <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                  {ws.description || 'No description'}
                </p>
                <div className="text-xs text-gray-500">
                  Created {new Date(ws.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}