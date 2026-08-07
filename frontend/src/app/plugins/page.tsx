'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, pluginAPI } from '@/lib/api';

interface Plugin {
  id: number;
  name: string;
  slug: string;
  description: string;
  version: string;
  category: string;
  icon: string;
  is_enabled: boolean;
  config: Record<string, string>;
}

interface Categories {
  [category: string]: Plugin[];
}

const categoryLabels: Record<string, string> = {
  research: '🔍 Research',
  productivity: '📋 Productivity',
  development: '💻 Development',
  communication: '💬 Communication',
  social: '🌐 Social Media',
  finance: '💰 Finance',
  ecommerce: '🛍️ E-Commerce',
  general: '⚙️ General',
};

export default function PluginsPage() {
  const router = useRouter();

  const [categories, setCategories] = useState<Categories>({});
  const [loading, setLoading] = useState(true);
  const [toggling, setToggling] = useState<string | null>(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    pluginAPI
      .getByCategory()
      .then((data) => {
        setCategories(data.categories || {});
        setLoading(false);
      })
      .catch(() => {
        router.push('/');
      });
  }, [router]);

  const handleToggle = async (slug: string, currentState: boolean) => {
    setToggling(slug);
    setMessage('');

    try {
      await pluginAPI.toggle(slug, !currentState);

      setCategories((prev) => {
        const updated = { ...prev };
        for (const cat in updated) {
          updated[cat] = updated[cat].map((p) =>
            p.slug === slug ? { ...p, is_enabled: !currentState } : p
          );
        }
        return updated;
      });

      setMessage(
        `✅ ${slug} ${!currentState ? 'enabled' : 'disabled'} successfully`
      );
    } catch {
      setMessage('❌ Failed to update plugin');
    } finally {
      setToggling(null);
      setTimeout(() => setMessage(''), 3000);
    }
  };

  const totalPlugins = Object.values(categories).flat().length;
  const enabledPlugins = Object.values(categories)
    .flat()
    .filter((p) => p.is_enabled).length;

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Plugin Ecosystem</h1>
          <p className="text-gray-400 mt-1">
            Connect NEXUS with external tools and services
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <div className="text-2xl mb-1">🔌</div>
            <div className="text-2xl font-bold">{totalPlugins}</div>
            <div className="text-xs text-gray-400">Total Plugins</div>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <div className="text-2xl mb-1">✅</div>
            <div className="text-2xl font-bold text-green-400">{enabledPlugins}</div>
            <div className="text-xs text-gray-400">Enabled</div>
          </div>
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <div className="text-2xl mb-1">⭕</div>
            <div className="text-2xl font-bold text-gray-400">
              {totalPlugins - enabledPlugins}
            </div>
            <div className="text-xs text-gray-400">Disabled</div>
          </div>
        </div>

        {/* Message */}
        {message && (
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-3 mb-6 text-sm text-gray-300">
            {message}
          </div>
        )}

        {loading ? (
          <div className="flex items-center gap-3 text-gray-400">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Loading plugins...
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(categories).map(([category, plugins]) => (
              <div key={category}>
                <h2 className="text-lg font-semibold mb-4">
                  {categoryLabels[category] || category}
                </h2>

                <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {plugins.map((plugin) => (
                    <div
                      key={plugin.slug}
                      className={`bg-gray-900 border rounded-xl p-5 transition-all ${
                        plugin.is_enabled
                          ? 'border-blue-800 bg-blue-900/10'
                          : 'border-gray-800'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <div className="text-3xl">{plugin.icon}</div>
                          <div>
                            <h3 className="font-semibold text-sm">
                              {plugin.name}
                            </h3>
                            <div className="text-xs text-gray-500">
                              v{plugin.version}
                            </div>
                          </div>
                        </div>

                        {/* Toggle Switch */}
                        <button
                          onClick={() =>
                            handleToggle(plugin.slug, plugin.is_enabled)
                          }
                          disabled={toggling === plugin.slug}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            plugin.is_enabled ? 'bg-blue-600' : 'bg-gray-700'
                          } ${toggling === plugin.slug ? 'opacity-50' : ''}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              plugin.is_enabled
                                ? 'translate-x-6'
                                : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>

                      <p className="text-sm text-gray-400 mb-3">
                        {plugin.description}
                      </p>

                      <div className="flex items-center justify-between">
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full ${
                            plugin.is_enabled
                              ? 'bg-green-500/20 text-green-400'
                              : 'bg-gray-700 text-gray-400'
                          }`}
                        >
                          {plugin.is_enabled ? 'Active' : 'Inactive'}
                        </span>

                        {Object.keys(plugin.config).length > 0 && (
                          <span className="text-xs text-gray-500">
                            ⚙️ Config required
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}