'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, selfModAPI } from '@/lib/api';

interface ScanStats {
  total_files: number;
  tsx_files: number;
  python_files: number;
  folders: number;
}

interface Issue {
  file: string;
  type: string;
  severity: string;
  title: string;
  description: string;
  suggestion: string;
}

interface Improvement {
  id: number;
  title: string;
  priority: string;
  category: string;
  description: string;
  benefit: string;
  estimated_impact: string;
  auto_implementable: boolean;
  files_affected: string[];
}

export default function AutoUpgradePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [stats, setStats] = useState<ScanStats | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [improvements, setImprovements] = useState<Improvement[]>([]);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = getToken();
    if (!token) router.push('/');
  }, [router]);

  const handleScan = async () => {
    setScanning(true);
    setMessage('🔍 Scanning system...');
    try {
      const result = await selfModAPI.scanSystem();
      if (result.success) {
        setStats(result.stats);
        setIssues(result.issues || []);
        setMessage(`✅ Scan complete: ${result.total_issues} issues found`);
      } else {
        setMessage('❌ Scan failed');
      }
    } catch {
      setMessage('❌ Scan error');
    } finally {
      setScanning(false);
    }
  };

  const handleGetSuggestions = async () => {
    setLoading(true);
    setMessage('🧠 AI analyzing and generating suggestions... (30-60s)');
    try {
      const result = await selfModAPI.getSuggestions();
      if (result.success) {
        setImprovements(result.improvements || []);
        setStats(result.scan_stats);
        setMessage(`✅ Generated ${result.improvements.length} AI suggestions`);
      } else {
        setMessage(`❌ ${result.error || 'Failed'}`);
      }
    } catch {
      setMessage('❌ AI generation failed');
    } finally {
      setLoading(false);
    }
  };

  const priorityColor = (p: string) => {
    if (p === 'high') return 'bg-red-500/20 text-red-400 border-red-800';
    if (p === 'medium') return 'bg-yellow-500/20 text-yellow-400 border-yellow-800';
    return 'bg-blue-500/20 text-blue-400 border-blue-800';
  };

  const severityColor = (s: string) => {
    if (s === 'high') return 'text-red-400';
    if (s === 'medium') return 'text-yellow-400';
    return 'text-blue-400';
  };

  const categoryIcon = (c: string) => {
    const icons: Record<string, string> = {
      performance: '⚡',
      security: '🔒',
      UX: '🎨',
      feature: '✨',
      quality: '🛠️',
    };
    return icons[c] || '💡';
  };

  const implementSuggestion = (imp: Improvement) => {
    const request = `${imp.title}: ${imp.description}. Files: ${imp.files_affected.join(', ')}`;
    localStorage.setItem('nexus_pending_request', request);
    router.push('/self-mod');
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            🧬 Auto Upgrade System
          </h1>
          <p className="text-gray-400 mt-1">
            NEXUS analyzes itself and suggests improvements
          </p>
        </div>

        <div className="bg-purple-900/20 border border-purple-800 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-2xl">🧠</div>
            <div className="text-sm text-purple-200">
              <strong>Self-Evolving AI:</strong> NEXUS scans its own code, detects issues, and generates improvement suggestions using AI.
            </div>
          </div>
        </div>

        {message && (
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 mb-6 text-sm text-white">
            {message}
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          <button
            onClick={handleScan}
            disabled={scanning}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white p-6 rounded-xl text-left transition-colors"
          >
            <div className="text-3xl mb-2">🔍</div>
            <div className="font-semibold text-lg">Quick Scan</div>
            <div className="text-sm text-blue-200 mt-1">
              {scanning ? 'Scanning...' : 'Fast scan for issues'}
            </div>
          </button>

          <button
            onClick={handleGetSuggestions}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white p-6 rounded-xl text-left transition-colors"
          >
            <div className="text-3xl mb-2">🧠</div>
            <div className="font-semibold text-lg">AI Suggestions</div>
            <div className="text-sm text-purple-200 mt-1">
              {loading ? 'Analyzing...' : 'AI-powered improvement suggestions'}
            </div>
          </button>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="text-2xl mb-1">📁</div>
              <div className="text-2xl font-bold">{stats.total_files}</div>
              <div className="text-xs text-gray-400">Total Files</div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="text-2xl mb-1">⚛️</div>
              <div className="text-2xl font-bold">{stats.tsx_files}</div>
              <div className="text-xs text-gray-400">React Files</div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="text-2xl mb-1">🐍</div>
              <div className="text-2xl font-bold">{stats.python_files}</div>
              <div className="text-xs text-gray-400">Python Files</div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="text-2xl mb-1">📂</div>
              <div className="text-2xl font-bold">{stats.folders}</div>
              <div className="text-xs text-gray-400">Folders</div>
            </div>
          </div>
        )}

        {/* AI Suggestions */}
        {improvements.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">🧠 AI Improvement Suggestions</h2>
            <div className="space-y-4">
              {improvements.map((imp) => (
                <div
                  key={imp.id}
                  className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-purple-800 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div className="flex items-center gap-3">
                      <div className="text-3xl">{categoryIcon(imp.category)}</div>
                      <div>
                        <h3 className="font-semibold text-lg">{imp.title}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full border ${priorityColor(imp.priority)}`}>
                            {imp.priority.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">
                            {imp.category}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => implementSuggestion(imp)}
                      className="bg-purple-600 hover:bg-purple-700 text-white text-xs px-3 py-2 rounded-lg font-medium"
                    >
                      ⚡ Implement
                    </button>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-500">What: </span>
                      <span className="text-gray-200">{imp.description}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Benefit: </span>
                      <span className="text-green-400">{imp.benefit}</span>
                    </div>
                    {imp.files_affected && imp.files_affected.length > 0 && (
                      <div>
                        <span className="text-gray-500">Files: </span>
                        <span className="text-blue-400 text-xs">
                          {imp.files_affected.join(', ')}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Issues */}
        {issues.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold mb-4">⚠️ Detected Issues</h2>
            <div className="space-y-3">
              {issues.slice(0, 10).map((issue, index) => (
                <div
                  key={index}
                  className="bg-gray-900 border border-gray-800 rounded-xl p-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={`text-xs font-bold ${severityColor(issue.severity)}`}>
                          {issue.severity.toUpperCase()}
                        </span>
                        <span className="text-sm font-medium">{issue.title}</span>
                      </div>
                      <div className="text-xs text-gray-400 mb-2">
                        {issue.description}
                      </div>
                      <div className="text-xs text-blue-400">
                        💡 {issue.suggestion}
                      </div>
                      <code className="text-xs text-gray-500 mt-2 block">
                        {issue.file}
                      </code>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!improvements.length && !issues.length && !loading && !scanning && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">🧬</div>
            <h3 className="text-lg font-medium mb-2">
              Ready to analyze NEXUS?
            </h3>
            <p className="text-gray-400 text-sm">
             Click Quick Scan for fast issue detection, or AI Suggestions for intelligent improvement ideas.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}