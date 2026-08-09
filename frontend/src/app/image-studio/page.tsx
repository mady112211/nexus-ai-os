'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, imageAIAPI } from '@/lib/api';

interface Style {
  id: string;
  name: string;
  icon: string;
}

export default function ImageStudioPage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('');
  const [styles, setStyles] = useState<Style[]>([]);
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [enhancing, setEnhancing] = useState(false);
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<{ prompt: string; image: string }[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }

    imageAIAPI.getStyles().then((data) => setStyles(data.styles || [])).catch(() => {});
  }, [router]);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setLoading(true);
    setMessage('🎨 Generating image... (30-60s)');
    setImage(null);

    try {
      const result = await imageAIAPI.generate(prompt, selectedStyle);
      if (result.success) {
        setImage(result.image);
        setMessage(`✅ Generated with ${result.model}`);
        setHistory((prev) => [{ prompt: result.prompt, image: result.image }, ...prev].slice(0, 6));
      } else {
        setMessage(`❌ ${result.error}`);
      }
    } catch {
      setMessage('❌ Generation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleEnhance = async () => {
    if (!prompt.trim()) return;
    setEnhancing(true);
    try {
      const result = await imageAIAPI.enhancePrompt(prompt);
      if (result.success) {
        setPrompt(result.enhanced);
        setMessage('✨ Prompt enhanced!');
      }
    } catch {
      setMessage('Failed to enhance');
    } finally {
      setEnhancing(false);
    }
  };

  const downloadImage = () => {
    if (!image) return;
    const link = document.createElement('a');
    link.href = image;
    link.download = `nexus-ai-${Date.now()}.png`;
    link.click();
  };

  const examples = [
    'A futuristic city at sunset',
    'Cute robot playing with cat',
    'Ancient dragon in mountains',
    'Astronaut floating in space',
    'Magical forest with glowing mushrooms',
  ];

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            🎨 Image AI Studio
          </h1>
          <p className="text-gray-400 mt-1">
            Generate stunning images with AI - unlimited & free
          </p>
        </div>

        <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 border border-purple-800 rounded-xl p-4 mb-6">
          <div className="flex items-start gap-3">
            <div className="text-3xl">✨</div>
            <div className="text-sm text-purple-100">
              <strong>Powered by Gemini + Pollinations:</strong> Generate unlimited FREE images. High quality, multiple styles, instant results.
            </div>
          </div>
        </div>

        {message && (
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-3 mb-6 text-sm text-white">
            {message}
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left - Input */}
          <div className="space-y-4">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold mb-4">📝 Describe Your Image</h2>

              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="A beautiful sunset over mountains with dragons flying..."
                rows={4}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none text-sm"
              />

              <div className="flex gap-2 mt-3">
                <button
                  onClick={handleGenerate}
                  disabled={loading || !prompt.trim()}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white px-6 py-3 rounded-lg text-sm font-medium"
                >
                  {loading ? '🎨 Generating...' : '🎨 Generate Image'}
                </button>

                <button
                  onClick={handleEnhance}
                  disabled={enhancing || !prompt.trim()}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-4 py-3 rounded-lg text-sm font-medium"
                  title="AI enhance prompt"
                >
                  {enhancing ? '✨' : '✨ Enhance'}
                </button>
              </div>
            </div>

            {/* Styles */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold mb-4">🎭 Style (Optional)</h2>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setSelectedStyle('')}
                  className={`p-3 rounded-lg text-xs transition-colors ${
                    !selectedStyle ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  Default
                </button>
                {styles.map((style) => (
                  <button
                    key={style.id}
                    onClick={() => setSelectedStyle(style.id)}
                    className={`p-3 rounded-lg text-xs transition-colors ${
                      selectedStyle === style.id
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                    }`}
                  >
                    <div className="text-lg mb-1">{style.icon}</div>
                    <div>{style.name}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Examples */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold mb-4">💡 Try Examples</h2>
              <div className="space-y-2">
                {examples.map((ex) => (
                  <button
                    key={ex}
                    onClick={() => setPrompt(ex)}
                    className="w-full text-left bg-gray-800 hover:bg-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 transition-colors"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right - Output */}
          <div className="space-y-4">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 min-h-[400px]">
              <h2 className="font-semibold mb-4">🖼️ Generated Image</h2>

              {loading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="text-6xl mb-4 animate-pulse">🎨</div>
                  <p className="text-gray-400 text-sm">Creating your masterpiece...</p>
                  <div className="flex gap-2 mt-4">
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-100" />
                    <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              ) : image ? (
                <div className="space-y-4">
                  <img
                    src={image}
                    alt="Generated"
                    className="w-full rounded-lg border border-gray-700"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={downloadImage}
                      className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                    >
                      💾 Download
                    </button>
                    <button
                      onClick={handleGenerate}
                      className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                    >
                      🔄 Regenerate
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                  <div className="text-6xl mb-2">🖼️</div>
                  <p className="text-sm">Your image will appear here</p>
                </div>
              )}
            </div>

            {/* History */}
            {history.length > 0 && (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="font-semibold mb-4">📚 Recent Images</h2>
                <div className="grid grid-cols-3 gap-2">
                  {history.map((item, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        setImage(item.image);
                        setPrompt(item.prompt);
                      }}
                      className="aspect-square rounded-lg overflow-hidden border border-gray-700 hover:border-purple-500 transition-colors"
                    >
                      <img src={item.image} alt="" className="w-full h-full object-cover" />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}