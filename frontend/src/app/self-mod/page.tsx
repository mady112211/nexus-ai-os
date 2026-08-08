'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, selfModAPI } from '@/lib/api';

interface Plan {
  understanding: string;
  target_files: string[];
  change_type: string;
  risk_level: string;
  description: string;
  estimated_changes: string;
}

interface GeneratedCode {
  file: string;
  current_code: string;
  new_code: string;
  lines_before: number;
  lines_after: number;
}

export default function SelfModPage() {
  const router = useRouter();
  const [request, setRequest] = useState('');
  const [step, setStep] = useState<'input' | 'plan' | 'generate' | 'preview'>('input');
  const [plan, setPlan] = useState<Plan | null>(null);
  const [selectedFile, setSelectedFile] = useState('');
  const [generated, setGenerated] = useState<GeneratedCode | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
    }
  }, [router]);

  const handlePlan = async () => {
    if (!request.trim()) return;
    setLoading(true);
    setMessage('');
    try {
      const result = await selfModAPI.planChange(request);
      if (result.success && result.plan) {
        setPlan(result.plan);
        setStep('plan');
      } else {
        setMessage('Could not create plan');
      }
    } catch {
      setMessage('Failed to plan');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (file: string) => {
    setSelectedFile(file);
    setLoading(true);
    setMessage('');
    try {
      const result = await selfModAPI.generateCode(request, file);
      if (result.success) {
        setGenerated(result);
        setStep('preview');
      } else {
        setMessage('Could not generate code');
      }
    } catch {
      setMessage('Generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!generated) return;
    if (!confirm(`Apply changes to ${generated.file}?`)) return;

    setLoading(true);
    try {
      const result = await selfModAPI.applyChange(generated.file, generated.new_code);
      if (result.success) {
        setMessage(`Change applied! Backup: ${result.backup}`);
        setTimeout(() => reset(), 3000);
      } else {
        setMessage(result.error || 'Failed');
      }
    } catch {
      setMessage('Failed to apply');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setRequest('');
    setPlan(null);
    setGenerated(null);
    setSelectedFile('');
    setStep('input');
    setMessage('');
  };

  const riskColor = (risk: string) => {
    if (risk === 'low') return 'bg-green-500/20 text-green-400';
    if (risk === 'medium') return 'bg-yellow-500/20 text-yellow-400';
    return 'bg-red-500/20 text-red-400';
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            🧬 Self-Modification System
          </h1>
          <p className="text-gray-400 mt-1">
            NEXUS can modify its own code — with your approval
          </p>
        </div>

        <div className="bg-yellow-900/20 border border-yellow-800 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-2xl">⚠️</div>
            <div className="text-sm text-yellow-200">
              <strong>Safety First:</strong> All changes require your approval. Auto-backups created before every modification.
            </div>
          </div>
        </div>

        {message && (
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 mb-6 text-sm text-white">
            {message}
          </div>
        )}

        {step === 'input' && (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="font-semibold mb-4">What do you want to change?</h2>

            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="Examples:
- Change sidebar color to purple
- Add welcome message on dashboard
- Change login page title"
              rows={6}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none text-sm"
            />

            <button
              onClick={handlePlan}
              disabled={loading || !request.trim()}
              className="mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-3 rounded-lg text-sm font-medium"
            >
              {loading ? 'Planning...' : 'Plan Modification'}
            </button>
          </div>
        )}

        {step === 'plan' && plan && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold">Modification Plan</h2>
                <span className={`text-xs px-3 py-1 rounded-full ${riskColor(plan.risk_level)}`}>
                  {plan.risk_level.toUpperCase()} RISK
                </span>
              </div>

              <div className="space-y-4 text-sm">
                <div>
                  <div className="text-gray-500 mb-1">Understanding:</div>
                  <div className="text-gray-200">{plan.understanding}</div>
                </div>

                <div>
                  <div className="text-gray-500 mb-1">Plan:</div>
                  <div className="text-gray-200">{plan.description}</div>
                </div>

                <div>
                  <div className="text-gray-500 mb-1">Change Type:</div>
                  <div className="text-blue-400 uppercase">{plan.change_type}</div>
                </div>

                <div>
                  <div className="text-gray-500 mb-2">Target Files:</div>
                  <div className="space-y-2">
                    {plan.target_files.map((file) => (
                      <div
                        key={file}
                        className="flex items-center justify-between bg-gray-800 rounded-lg p-3"
                      >
                        <code className="text-xs text-blue-400">{file}</code>
                        <button
                          onClick={() => handleGenerate(file)}
                          disabled={loading}
                          className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1 rounded"
                        >
                          {loading && selectedFile === file ? '...' : 'Generate Code'}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={reset}
              className="text-sm text-gray-400 hover:text-white"
            >
              Cancel
            </button>
          </div>
        )}

        {step === 'preview' && generated && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="font-semibold">Code Preview</h2>
                  <code className="text-xs text-blue-400">{generated.file}</code>
                </div>
                <div className="text-xs text-gray-400">
                  {generated.lines_before} to {generated.lines_after} lines
                </div>
              </div>

              <div className="bg-gray-950 border border-gray-800 rounded-lg p-4 max-h-96 overflow-auto">
                <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono">
                  {generated.new_code}
                </pre>
              </div>

              <div className="flex gap-3 mt-4">
                <button
                  onClick={handleApply}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 text-white px-6 py-2 rounded-lg text-sm font-medium"
                >
                  {loading ? 'Applying...' : 'Apply Change'}
                </button>

                <button
                  onClick={() => setStep('plan')}
                  className="bg-gray-800 hover:bg-gray-700 text-white px-6 py-2 rounded-lg text-sm"
                >
                  Back
                </button>

                <button
                  onClick={reset}
                  className="text-gray-400 hover:text-white text-sm px-6 py-2"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}