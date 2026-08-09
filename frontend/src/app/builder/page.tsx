'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, selfModAPI } from '@/lib/api';

interface Understanding {
  feature_name: string;
  feature_type: string;
  description: string;
  complexity: string;
  icon_suggestion: string;
  estimated_files: number;
}

interface ManualInstruction {
  step: string;
  file: string;
  instruction: string;
  code: string;
}

interface StepResult {
  step: number;
  file: string;
  action?: string;
  error?: string;
}

interface BuildResult {
  success: boolean;
  understanding: Understanding;
  total_steps: number;
  completed_count: number;
  failed_count: number;
  steps_completed: StepResult[];
  steps_failed: StepResult[];
  manual_instructions?: ManualInstruction[];
  plan?: {
    slug: string;
    icon: string;
  };
}

export default function BuilderPage() {
  const router = useRouter();
  const [request, setRequest] = useState('');
  const [step, setStep] = useState<'input' | 'building' | 'result'>('input');
  const [understanding, setUnderstanding] = useState<Understanding | null>(null);
  const [result, setResult] = useState<BuildResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  useEffect(() => {
    const token = getToken();
    if (!token) router.push('/');
  }, [router]);

  const handleUnderstand = async () => {
    if (!request.trim()) return;
    setLoading(true);
    setMessage('🧠 NEXUS understanding your request...');
    try {
      const res = await selfModAPI.builderUnderstand(request);
      if (res.success) {
        setUnderstanding(res.understanding);
        setMessage('');
      } else {
        setMessage(`❌ ${res.error}`);
      }
    } catch {
      setMessage('❌ Failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBuild = async () => {
    if (!confirm(`Safely build: ${understanding?.feature_name}?\n\nOnly new files will be created. No existing files will be modified.`)) return;

    setLoading(true);
    setStep('building');
    setMessage('🛡️ Safely building your feature... (1-2 minutes)');

    try {
      const res = await selfModAPI.builderBuild(request);
      setResult(res);
      setStep('result');
      if (res.success) {
        setMessage('🎉 Safe build complete!');
      } else {
        setMessage('⚠️ Some steps failed');
      }
    } catch {
      setMessage('❌ Build failed');
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setRequest('');
    setUnderstanding(null);
    setResult(null);
    setStep('input');
    setMessage('');
    setCopiedIndex(null);
  };

  const copyCode = (code: string, index: number) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const complexityColor = (c: string) => {
    if (c === 'low') return 'bg-green-500/20 text-green-400';
    if (c === 'medium') return 'bg-yellow-500/20 text-yellow-400';
    return 'bg-red-500/20 text-red-400';
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            🛡️ NEXUS Safe Builder
          </h1>
          <p className="text-gray-400 mt-1">
            Autonomous feature creation with 100% safety
          </p>
        </div>

        <div className="bg-gradient-to-br from-green-900/30 to-blue-900/30 border border-green-800 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-3xl">🛡️</div>
            <div className="text-sm text-green-100">
              <strong>100% Safe Mode:</strong> Only creates NEW files. Never modifies existing files. Your app will NEVER break!
            </div>
          </div>
        </div>

        {message && (
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 mb-6 text-sm text-white">
            {message}
          </div>
        )}

        {step === 'input' && (
          <>
            {!understanding ? (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="font-semibold mb-4">What do you want to build?</h2>

                <textarea
                  value={request}
                  onChange={(e) => setRequest(e.target.value)}
                  placeholder="Examples:
- Add a random jokes page from public API
- Create a crypto prices page
- Build a quotes generator page
- Add a random cat images page"
                  rows={6}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-green-500 resize-none text-sm"
                />

                <button
                  onClick={handleUnderstand}
                  disabled={loading || !request.trim()}
                  className="mt-4 bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white px-6 py-3 rounded-lg text-sm font-medium"
                >
                  {loading ? '🧠 Analyzing...' : '🚀 Analyze Request'}
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="font-semibold">✅ Understanding Complete</h2>
                    <span className={`text-xs px-3 py-1 rounded-full ${complexityColor(understanding.complexity)}`}>
                      {understanding.complexity.toUpperCase()}
                    </span>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-3">
                      <div className="text-4xl">{understanding.icon_suggestion}</div>
                      <div>
                        <div className="font-semibold text-lg">{understanding.feature_name}</div>
                        <div className="text-xs text-gray-400">{understanding.feature_type}</div>
                      </div>
                    </div>

                    <div>
                      <div className="text-gray-500 mb-1">Description:</div>
                      <div className="text-gray-200">{understanding.description}</div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleBuild}
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white px-6 py-3 rounded-lg text-sm font-medium"
                  >
                    🛡️ Safe Build
                  </button>

                  <button
                    onClick={reset}
                    className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-3 rounded-lg text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </>
        )}

        {step === 'building' && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
            <div className="text-6xl mb-4 animate-bounce">🛡️</div>
            <h3 className="text-xl font-semibold mb-2">Building safely...</h3>
            <p className="text-gray-400 text-sm">
              Creating new files without touching existing ones
            </p>
            <div className="flex items-center justify-center gap-2 mt-6">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce" />
              <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce delay-100" />
              <div className="w-3 h-3 bg-green-500 rounded-full animate-bounce delay-200" />
            </div>
          </div>
        )}

        {step === 'result' && result && (
          <div className="space-y-4">
            <div className={`border rounded-xl p-6 ${result.success ? 'bg-green-900/20 border-green-800' : 'bg-yellow-900/20 border-yellow-800'}`}>
              <div className="flex items-center gap-3 mb-4">
                <div className="text-4xl">{result.success ? '🎉' : '⚠️'}</div>
                <div>
                  <h2 className="text-xl font-bold">
                    {result.success ? 'Build Complete!' : 'Build Failed'}
                  </h2>
                  <p className="text-sm text-gray-300">
                    {result.completed_count}/{result.total_steps} files created
                  </p>
                </div>
              </div>
            </div>

            {/* Files Created */}
            {result.steps_completed.length > 0 && (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h3 className="font-semibold mb-4">✅ Files Created</h3>
                <div className="space-y-2">
                  {result.steps_completed.map((s) => (
                    <div key={s.step} className="flex items-center gap-3 bg-green-900/10 border border-green-800/50 rounded-lg p-3 text-sm">
                      <span className="text-green-400">✓</span>
                      <code className="text-xs text-blue-400 flex-1">{s.file}</code>
                      <span className="text-xs text-gray-500">{s.action}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Manual Instructions */}
            {result.manual_instructions && result.manual_instructions.length > 0 && (
              <div className="bg-yellow-900/10 border border-yellow-800 rounded-xl p-6">
                <h3 className="font-semibold mb-4 text-yellow-400">
                  📝 Manual Steps Required (30 seconds)
                </h3>
                <p className="text-sm text-gray-300 mb-4">
                  To activate this feature, please add the following manually:
                </p>

                <div className="space-y-4">
                  {result.manual_instructions.map((inst, index) => (
                    <div key={index} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                      <div className="text-sm font-semibold mb-2">{inst.step}</div>
                      <div className="text-xs text-gray-400 mb-2">
                        File: <code className="text-blue-400">{inst.file}</code>
                      </div>
                      <div className="text-xs text-gray-300 mb-3">{inst.instruction}</div>

                      <div className="bg-gray-950 rounded-lg p-3 relative">
                        <pre className="text-xs text-green-400 font-mono overflow-x-auto">
                          {inst.code}
                        </pre>
                        <button
                          onClick={() => copyCode(inst.code, index)}
                          className="absolute top-2 right-2 bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1 rounded"
                        >
                          {copiedIndex === index ? '✅ Copied!' : '📋 Copy'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="mt-4 p-3 bg-blue-900/20 border border-blue-800 rounded-lg text-xs text-blue-200">
                  💡 <strong>Tip:</strong> Copy the code, open the file in VS Code, paste it, and save. Your new feature will be live!
                </div>
              </div>
            )}

            {/* Access URL */}
            {result.success && result.plan && (
              <div className="bg-blue-900/20 border border-blue-800 rounded-xl p-6">
                <h3 className="font-semibold mb-2">🔗 Access Your New Feature</h3>
                <p className="text-sm text-gray-300 mb-3">
                  After adding the sidebar entry, visit:
                </p>
                <code className="block bg-gray-950 text-green-400 px-3 py-2 rounded text-sm">
                  http://localhost:3000/{result.plan.slug}
                </code>
              </div>
            )}

            {/* Failed Steps */}
            {result.steps_failed.length > 0 && (
              <div className="bg-red-900/10 border border-red-800 rounded-xl p-6">
                <h3 className="font-semibold mb-4 text-red-400">❌ Failed Steps</h3>
                {result.steps_failed.map((s) => (
                  <div key={s.step} className="text-sm">
                    <div className="text-red-400">Step {s.step}: {s.file}</div>
                    <div className="text-xs text-gray-400 mt-1">{s.error}</div>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={reset}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg text-sm font-medium"
              >
                🚀 Build Another
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}