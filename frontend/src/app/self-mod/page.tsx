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
  reasoning?: string;
}

interface Validation {
  valid: boolean;
  errors: string[];
  warnings: string[];
  line_count: number;
}

interface GeneratedCode {
  file: string;
  current_code: string;
  new_code: string;
  lines_before: number;
  lines_after: number;
  validation?: Validation;
  has_warnings?: boolean;
  comparison_warnings?: string[];
}

export default function SelfModPage() {
  const router = useRouter();
  const [request, setRequest] = useState('');
  const [step, setStep] = useState<'input' | 'plan' | 'preview'>('input');
  const [plan, setPlan] = useState<Plan | null>(null);
  const [selectedFile, setSelectedFile] = useState('');
  const [generated, setGenerated] = useState<GeneratedCode | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = getToken();
    if (!token) router.push('/');
  }, [router]);

  const handlePlan = async () => {
    if (!request.trim()) return;
    setLoading(true);
    setMessage('🧠 Smart planning in progress...');
    try {
      const result = await selfModAPI.planChange(request);
      if (result.success && result.plan) {
        setPlan(result.plan);
        setStep('plan');
        setMessage('');
      } else {
        setMessage('❌ Could not create plan');
      }
    } catch {
      setMessage('❌ Failed to plan');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (file: string) => {
    setSelectedFile(file);
    setLoading(true);
    setMessage('🧠 Reading context and generating perfect code... (may take 30s)');
    try {
      const result = await selfModAPI.generateCode(request, file);
      if (result.success) {
        setGenerated(result);
        setStep('preview');
        if (result.has_warnings) {
          setMessage('⚠️ Code generated with warnings - review carefully');
        } else {
          setMessage('✅ Code validated and ready');
        }
      } else {
        setMessage(`❌ ${result.error}`);
      }
    } catch {
      setMessage('❌ Generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (force = false) => {
    if (!generated) return;
    const msg = force
      ? `FORCE apply to ${generated.file}? (skips validation)`
      : `Apply changes to ${generated.file}?`;
    if (!confirm(msg)) return;

    setLoading(true);
    try {
      const result = await selfModAPI.applyChange(
        generated.file,
        generated.new_code,
        force
      );
      if (result.success) {
        setMessage(`✅ Applied! Backup: ${result.backup}`);
        setTimeout(() => reset(), 3000);
      } else {
        setMessage(`❌ ${result.error}`);
      }
    } catch {
      setMessage('❌ Failed to apply');
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
            🧬 Smart Self-Modification
          </h1>
          <p className="text-gray-400 mt-1">
            Context-aware code modification with auto-validation
          </p>
        </div>

        <div className="bg-blue-900/20 border border-blue-800 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-2xl">🧠</div>
            <div className="text-sm text-blue-200">
              <strong>Smart Mode:</strong> AI reads related files, follows patterns, validates code, and auto-retries on errors.
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
- Change dashboard heading text to 'NEXUS Control'
- Add a purple color to sidebar
- Change login page welcome message"
              rows={6}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none text-sm"
            />

            <button
              onClick={handlePlan}
              disabled={loading || !request.trim()}
              className="mt-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-3 rounded-lg text-sm font-medium"
            >
              {loading ? '🧠 Planning...' : '🚀 Smart Plan'}
            </button>
          </div>
        )}

        {step === 'plan' && plan && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold">📋 Smart Plan</h2>
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

                {plan.reasoning && (
                  <div>
                    <div className="text-gray-500 mb-1">Reasoning:</div>
                    <div className="text-gray-300 italic">{plan.reasoning}</div>
                  </div>
                )}

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
                          {loading && selectedFile === file ? '🧠 Reading context...' : '⚡ Smart Generate'}
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
            {/* Validation Status */}
            {generated.validation && (
              <div
                className={`border rounded-xl p-4 ${
                  generated.validation.valid
                    ? 'bg-green-900/20 border-green-800'
                    : 'bg-red-900/20 border-red-800'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="text-2xl">
                    {generated.validation.valid ? '✅' : '⚠️'}
                  </div>
                  <div className="text-sm">
                    <div className="font-semibold mb-1">
                      {generated.validation.valid
                        ? 'Code Validated Successfully'
                        : 'Validation Warnings'}
                    </div>
                    {generated.validation.errors.length > 0 && (
                      <div className="text-red-300 mt-2">
                        <div className="font-medium mb-1">Errors:</div>
                        <ul className="list-disc list-inside">
                          {generated.validation.errors.map((e, i) => (
                            <li key={i}>{e}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {generated.validation.warnings.length > 0 && (
                      <div className="text-yellow-300 mt-2">
                        <div className="font-medium mb-1">Warnings:</div>
                        <ul className="list-disc list-inside">
                          {generated.validation.warnings.map((w, i) => (
                            <li key={i}>{w}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="font-semibold">👁️ Code Preview</h2>
                  <code className="text-xs text-blue-400">{generated.file}</code>
                </div>
                <div className="text-xs text-gray-400">
                  {generated.lines_before} → {generated.lines_after} lines
                </div>
              </div>

              <div className="bg-gray-950 border border-gray-800 rounded-lg p-4 max-h-96 overflow-auto">
                <pre className="text-xs text-gray-300 whitespace-pre-wrap font-mono">
                  {generated.new_code}
                </pre>
              </div>

              <div className="flex gap-3 mt-4">
                <button
                  onClick={() => handleApply(false)}
                  disabled={loading || (generated.validation && !generated.validation.valid)}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-700 text-white px-6 py-2 rounded-lg text-sm font-medium"
                >
                  {loading ? 'Applying...' : '✅ Apply Change'}
                </button>

                {generated.validation && !generated.validation.valid && (
                  <button
                    onClick={() => handleApply(true)}
                    disabled={loading}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg text-sm font-medium"
                  >
                    ⚠️ Force Apply
                  </button>
                )}

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