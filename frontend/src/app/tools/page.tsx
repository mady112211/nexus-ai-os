'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import { getToken, toolsAPI } from '@/lib/api';

interface SearchResult {
  title: string;
  snippet: string;
  url: string;
  source: string;
}

interface FileItem {
  name: string;
  size: number;
  modified: string;
}

interface WeatherData {
  success: boolean;
  city?: string;
  country?: string;
  temperature?: number;
  feels_like?: number;
  humidity?: number;
  description?: string;
  icon?: string;
  wind_speed?: number;
  visibility?: number;
  min_temp?: number;
  max_temp?: number;
  error?: string;
}

interface ForecastDay {
  date: string;
  min_temp: number;
  max_temp: number;
  description: string;
  icon: string;
}

async function fetchFiles() {
  return await toolsAPI.listFiles();
}

export default function ToolsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('search');
  const [loading, setLoading] = useState(false);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchDone, setSearchDone] = useState(false);

  const [files, setFiles] = useState<FileItem[]>([]);
  const [newFileName, setNewFileName] = useState('');
  const [newFileContent, setNewFileContent] = useState('');
  const [fileMessage, setFileMessage] = useState('');

  const [weatherCity, setWeatherCity] = useState('Karachi');
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<ForecastDay[]>([]);
  const [weatherLoading, setWeatherLoading] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/');
      return;
    }
    fetchFiles()
      .then((data) => setFiles(data.files || []))
      .catch(() => {});
  }, [router]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setLoading(true);
    setSearchDone(false);
    try {
      const data = await toolsAPI.search(searchQuery);
      setSearchResults(data.results || []);
      setSearchDone(true);
    } catch {
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleWriteFile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFileName || !newFileContent) return;
    setLoading(true);
    try {
      const data = await toolsAPI.writeFile(newFileName, newFileContent);
      setFileMessage(data.message || 'File saved!');
      setNewFileName('');
      setNewFileContent('');
      const updated = await fetchFiles();
      setFiles(updated.files || []);
    } catch {
      setFileMessage('Failed to save file');
    } finally {
      setLoading(false);
      setTimeout(() => setFileMessage(''), 3000);
    }
  };

  const handleDeleteFile = async (filename: string) => {
    try {
      await toolsAPI.deleteFile(filename);
      const updated = await fetchFiles();
      setFiles(updated.files || []);
    } catch {
      // ignore
    }
  };

  const handleWeatherSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!weatherCity.trim()) return;
    setWeatherLoading(true);
    try {
      const [weather, forecastData] = await Promise.all([
        toolsAPI.getWeather(weatherCity),
        toolsAPI.getWeatherForecast(weatherCity, 3),
      ]);
      setWeatherData(weather);
      setForecast(forecastData.forecast || []);
    } catch {
      setWeatherData({ success: false, error: 'Failed to fetch weather' });
    } finally {
      setWeatherLoading(false);
    }
  };

  const tabs = [
    { id: 'search', label: '🔍 Web Search' },
    { id: 'weather', label: '🌤️ Weather' },
    { id: 'files', label: '📁 File Manager' },
  ];

  return (
    <div className="flex min-h-screen bg-gray-950">
      <Sidebar />

      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold">Plugin Tools</h1>
          <p className="text-gray-400 mt-1">Use your enabled plugins directly</p>
        </div>

        <div className="flex gap-2 mb-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Web Search */}
        {activeTab === 'search' && (
          <div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
              <h2 className="font-semibold mb-4">🔍 Web Search</h2>
              <form onSubmit={handleSearch} className="flex gap-3">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search the internet..."
                  className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-3 rounded-lg font-medium"
                >
                  {loading ? '...' : 'Search'}
                </button>
              </form>
            </div>

            {searchDone && searchResults.length === 0 && (
              <div className="text-gray-400 text-sm">No results found.</div>
            )}

            {searchResults.length > 0 && (
              <div className="space-y-4">
                {searchResults.map((result, index) => (
                  <div key={index} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h3 className="font-medium text-blue-400">{result.title}</h3>
                      <span className="text-xs text-gray-500 shrink-0">{result.source}</span>
                    </div>
                    <p className="text-sm text-gray-300 mb-3">{result.snippet}</p>
                    {result.url && (
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-blue-500 hover:text-blue-400"
                      >
                        {result.url}
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Weather */}
        {activeTab === 'weather' && (
          <div>
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-6">
              <h2 className="font-semibold mb-4">🌤️ Weather</h2>
              <form onSubmit={handleWeatherSearch} className="flex gap-3">
                <input
                  type="text"
                  value={weatherCity}
                  onChange={(e) => setWeatherCity(e.target.value)}
                  placeholder="Enter city name..."
                  className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                />
                <button
                  type="submit"
                  disabled={weatherLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-3 rounded-lg font-medium"
                >
                  {weatherLoading ? '...' : 'Get Weather'}
                </button>
              </form>
            </div>

            {weatherData && !weatherData.success && (
              <div className="bg-red-900/20 border border-red-800 rounded-xl p-4 text-red-400 text-sm">
                ❌ {weatherData.error}
              </div>
            )}

            {weatherData && weatherData.success && (
              <div className="space-y-4">
                {/* Current Weather */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h2 className="text-2xl font-bold">
                        {weatherData.city}, {weatherData.country}
                      </h2>
                      <p className="text-gray-400 mt-1">{weatherData.description}</p>
                    </div>
                    <div className="text-6xl">{weatherData.icon}</div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-800 rounded-xl p-4 text-center">
                      <div className="text-3xl font-bold text-blue-400">
                        {weatherData.temperature}°C
                      </div>
                      <div className="text-xs text-gray-400 mt-1">Temperature</div>
                    </div>

                    <div className="bg-gray-800 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-yellow-400">
                        {weatherData.feels_like}°C
                      </div>
                      <div className="text-xs text-gray-400 mt-1">Feels Like</div>
                    </div>

                    <div className="bg-gray-800 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-green-400">
                        {weatherData.humidity}%
                      </div>
                      <div className="text-xs text-gray-400 mt-1">Humidity</div>
                    </div>

                    <div className="bg-gray-800 rounded-xl p-4 text-center">
                      <div className="text-2xl font-bold text-purple-400">
                        {weatherData.wind_speed} m/s
                      </div>
                      <div className="text-xs text-gray-400 mt-1">Wind Speed</div>
                    </div>
                  </div>

                  <div className="flex gap-4 mt-4 text-sm text-gray-400">
                    <span>⬇️ Min: {weatherData.min_temp}°C</span>
                    <span>⬆️ Max: {weatherData.max_temp}°C</span>
                    <span>👁️ Visibility: {weatherData.visibility}km</span>
                  </div>
                </div>

                {/* Forecast */}
                {forecast.length > 0 && (
                  <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h3 className="font-semibold mb-4">📅 3-Day Forecast</h3>
                    <div className="grid grid-cols-3 gap-4">
                      {forecast.map((day) => (
                        <div
                          key={day.date}
                          className="bg-gray-800 rounded-xl p-4 text-center"
                        >
                          <div className="text-2xl mb-2">{day.icon}</div>
                          <div className="text-xs text-gray-400 mb-1">{day.date}</div>
                          <div className="text-sm font-medium mb-1">{day.description}</div>
                          <div className="text-xs text-gray-400">
                            {day.min_temp}° / {day.max_temp}°C
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* File Manager */}
        {activeTab === 'files' && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold mb-4">📝 Create File</h2>
              {fileMessage && (
                <div className="bg-gray-800 rounded-lg p-3 mb-4 text-sm text-gray-300">
                  {fileMessage}
                </div>
              )}
              <form onSubmit={handleWriteFile} className="space-y-4">
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">File Name</label>
                  <input
                    type="text"
                    value={newFileName}
                    onChange={(e) => setNewFileName(e.target.value)}
                    placeholder="example.txt"
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-400 mb-1 block">Content</label>
                  <textarea
                    value={newFileContent}
                    onChange={(e) => setNewFileContent(e.target.value)}
                    placeholder="File content here..."
                    rows={5}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 resize-none font-mono text-sm"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-6 py-2 rounded-lg text-sm font-medium"
                >
                  {loading ? 'Saving...' : '💾 Save File'}
                </button>
              </form>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="font-semibold mb-4">📁 Saved Files</h2>
              {files.length === 0 ? (
                <div className="text-gray-500 text-sm">No files yet.</div>
              ) : (
                <div className="space-y-2">
                  {files.map((file) => (
                    <div
                      key={file.name}
                      className="flex items-center justify-between bg-gray-800 rounded-lg p-3"
                    >
                      <div>
                        <div className="text-sm font-medium">{file.name}</div>
                        <div className="text-xs text-gray-500">
                          {file.size} bytes • {file.modified}
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteFile(file.name)}
                        className="text-red-400 hover:text-red-300 text-xs px-2 py-1 rounded"
                      >
                        Delete
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}