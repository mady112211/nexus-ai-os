'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, brainAPI } from '@/lib/api';

interface BrainResult {
  type: string;
  success?: boolean;
  query?: string;
  summary?: string;
  results?: Array<{ title: string; snippet: string; url: string }>;
  image?: string;
  prompt?: string;
  title?: string;
  author?: string;
  thumbnail?: string;
  analysis?: string;
  topic?: string;
  ideas?: Array<{ title: string; description: string }>;
  content?: string;
  response?: string;
  error?: string;
}

interface Message {
  id: number;
  role: 'user' | 'brain';
  content: string;
  intent?: string;
  language?: string;
  results?: BrainResult[];
  timestamp: Date;
}

interface Capability {
  icon: string;
  name: string;
  example: string;
}

export default function BrainPage() {
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    // Load capabilities
    brainAPI.getCapabilities().then((data) => {
      setCapabilities(data.capabilities || []);
    }).catch(() => {});

    // Welcome message
    setMessages([{
      id: 1,
      role: 'brain',
      content: "🧠 NEXUS Core Brain activated!\n\nI can help you with:\n• Web search in any language\n• Generate images\n• Analyze YouTube videos\n• Create content ideas\n• Write scripts\n• Multi-step tasks\n\nSpeak or type in ANY language!",
      timestamp: new Date(),
    }]);
  }, [router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Voice input not supported in this browser. Use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = (window as unknown as { webkitSpeechRecognition: new () => SpeechRecognition; SpeechRecognition: new () => SpeechRecognition }).webkitSpeechRecognition || (window as unknown as { SpeechRecognition: new () => SpeechRecognition }).SpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'ur-PK';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = (event: { results: { transcript: string }[][] }) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setIsListening(false);
    };

    recognition.onerror = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input.trim();
    setInput('');
    setLoading(true);

    try {
      const result = await brainAPI.process(currentInput);

      const brainMsg: Message = {
        id: Date.now() + 1,
        role: 'brain',
        content: `Processed: ${result.intent}`,
        intent: result.intent,
        language: result.language,
        results: result.results,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, brainMsg]);
    } catch {
      setMessages((prev) => [...prev, {
        id: Date.now() + 1,
        role: 'brain',
        content: '❌ Error processing command',
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const useExample = (example: string) => {
    setInput(example);
  };

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 flex flex-col">
        <div className="border-b border-gray-800 p-6">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            🧠 NEXUS Core Brain
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            One brain. Any language. Any command. Any task.
          </p>
        </div>

        {/* Capabilities */}
        {messages.length === 1 && (
          <div className="p-6 border-b border-gray-800">
            <h3 className="text-sm font-semibold mb-3 text-gray-400">✨ Try these:</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {capabilities.map((cap) => (
                <button
                  key={cap.name}
                  onClick={() => useExample(cap.example)}
                  className="bg-gray-900 border border-gray-800 hover:border-purple-600 rounded-lg p-3 text-left transition-colors"
                >
                  <div className="text-2xl mb-1">{cap.icon}</div>
                  <div className="text-xs font-semibold text-white">{cap.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{cap.example}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-2xl p-4 ${
                  msg.role === 'user'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-900 border border-gray-800 text-white'
                }`}
              >
                {msg.role === 'brain' && (
                  <div className="flex items-center gap-2 mb-2">
                    <div className="text-xl">🧠</div>
                    <span className="text-xs text-purple-400 font-medium">NEXUS Brain</span>
                    {msg.language && (
                      <span className="text-xs bg-gray-800 px-2 py-0.5 rounded">
                        🌍 {msg.language}
                      </span>
                    )}
                    {msg.intent && (
                      <span className="text-xs bg-purple-900/30 text-purple-300 px-2 py-0.5 rounded">
                        {msg.intent}
                      </span>
                    )}
                  </div>
                )}

                <div className="text-sm whitespace-pre-wrap">{msg.content}</div>

                {/* Results */}
                {msg.results && msg.results.length > 0 && (
                  <div className="mt-4 space-y-4">
                    {msg.results.map((r, i) => (
                      <div key={i} className="bg-gray-800 rounded-xl p-4">
                        {/* Web Search Result */}
                        {r.type === 'web_search' && (
                          <div>
                            <div className="text-xs text-blue-400 mb-2">🔍 Search: {r.query}</div>
                            {r.summary && (
                              <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-3 mb-3">
                                <div className="text-xs text-blue-400 mb-1">📝 AI Summary</div>
                                <div className="text-sm text-gray-200">{r.summary}</div>
                              </div>
                            )}
                            {r.results?.map((res, j) => (
                              <div key={j} className="mb-2 pb-2 border-b border-gray-700 last:border-0">
                                <div className="text-sm font-semibold text-blue-300">{res.title}</div>
                                <div className="text-xs text-gray-400 mt-1">{res.snippet}</div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Image Generation */}
                        {r.type === 'image_generation' && r.image && (
                          <div>
                            <div className="text-xs text-purple-400 mb-2">🎨 Generated Image</div>
                            <img src={r.image} alt="Generated" className="w-full rounded-lg" />
                            {r.prompt && (
                              <div className="text-xs text-gray-500 mt-2">Prompt: {r.prompt}</div>
                            )}
                          </div>
                        )}

                        {/* YouTube Analysis */}
                        {r.type === 'youtube_analysis' && (
                          <div>
                            <div className="text-xs text-red-400 mb-2">🎬 YouTube Analysis</div>
                            {r.thumbnail && (
                              <img src={r.thumbnail} alt="" className="w-full rounded-lg mb-2" />
                            )}
                            <div className="text-sm font-semibold">{r.title}</div>
                            <div className="text-xs text-gray-400 mb-2">by {r.author}</div>
                            {r.analysis && (
                              <div className="bg-gray-900 rounded-lg p-3">
                                <div className="text-xs text-blue-400 mb-1">🧠 Analysis</div>
                                <div className="text-sm">{r.analysis}</div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Content Ideas */}
                        {r.type === 'content_ideas' && r.ideas && (
                          <div>
                            <div className="text-xs text-green-400 mb-2">💡 Content Ideas: {r.topic}</div>
                            {r.ideas.map((idea, k) => (
                              <div key={k} className="bg-gray-900 rounded-lg p-3 mb-2">
                                <div className="text-sm font-semibold text-green-300">{idea.title}</div>
                                <div className="text-xs text-gray-400 mt-1">{idea.description}</div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Content */}
                        {r.type === 'content' && r.content && (
                          <div>
                            <div className="text-xs text-yellow-400 mb-2">📝 Content</div>
                            <div className="text-sm whitespace-pre-wrap">{r.content}</div>
                          </div>
                        )}

                        {/* Chat */}
                        {r.type === 'chat' && r.response && (
                          <div className="text-sm whitespace-pre-wrap">{r.response}</div>
                        )}

                        {/* Error */}
                        {r.success === false && (
                          <div className="text-red-400 text-sm">❌ {r.error}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <div className="text-xs text-gray-500 mt-2" suppressHydrationWarning>
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-900 border border-gray-800 rounded-2xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="text-xl">🧠</div>
                  <span className="text-xs text-purple-400">Brain thinking...</span>
                </div>
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-100" />
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-200" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-800 p-4">
          <div className="flex gap-3 items-end">
            <button
              onClick={startVoiceInput}
              disabled={loading || isListening}
              className={`px-4 py-3 rounded-xl transition-colors ${
                isListening
                  ? 'bg-red-600 hover:bg-red-700 animate-pulse'
                  : 'bg-gray-800 hover:bg-gray-700'
              } text-white`}
              title="Voice input"
            >
              {isListening ? '🎤 Listening...' : '🎤'}
            </button>

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type in any language or speak... (Enter to send)"
              rows={2}
              className="flex-1 bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none text-sm"
            />

            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 text-white px-6 py-3 rounded-xl font-medium text-sm"
            >
              {loading ? '...' : '⚡ Send'}
            </button>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            🌍 Supports: English, Hindi, Urdu, Arabic, Spanish, French & 50+ languages
          </p>
        </div>
      </main>
    </div>
  );
}