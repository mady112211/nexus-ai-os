const API_URL = 'http://localhost:5000';

export const getToken = () => localStorage.getItem('nexus_token');
export const setToken = (token: string) =>
  localStorage.setItem('nexus_token', token);
export const removeToken = () => localStorage.removeItem('nexus_token');

const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const token = getToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Something went wrong');
  }

  return data;
};

export const authAPI = {
  signup: (name: string, email: string, password: string) =>
    apiCall('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    }),

  login: (email: string, password: string) =>
    apiCall('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => apiCall('/api/auth/me'),
};

export const dashboardAPI = {
  get: () => apiCall('/api/dashboard/'),
};

export const missionAPI = {
  getAll: () => apiCall('/api/missions/'),

  create: (goal: string, title: string) =>
    apiCall('/api/missions/', {
      method: 'POST',
      body: JSON.stringify({ goal, title }),
    }),

  getOne: (id: number) => apiCall(`/api/missions/${id}`),

  execute: (id: number) =>
    apiCall(`/api/missions/${id}/execute`, {
      method: 'POST',
    }),
};

export const agentAPI = {
  getAll: () => apiCall('/api/agents/'),
};

export const memoryAPI = {
  getAll: () => apiCall('/api/memory/'),

  getLastContext: () => apiCall('/api/memory/context/last'),

  savePreference: (title: string, value: string) =>
    apiCall('/api/memory/preferences', {
      method: 'POST',
      body: JSON.stringify({ title, value }),
    }),

  saveMemory: (memory_type: string, content: string, importance = 5) =>
    apiCall('/api/memory/', {
      method: 'POST',
      body: JSON.stringify({ memory_type, content, importance }),
    }),

  search: (query: string) =>
    apiCall(`/api/memory/search?q=${encodeURIComponent(query)}`),
};

export const chatAPI = {
  sendMessage: (message: string) =>
    apiCall('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({ message }),
    }),
};

export const settingsAPI = {
  getProfile: () => apiCall('/api/settings/profile'),

  updateProfile: (name: string) =>
    apiCall('/api/settings/profile', {
      method: 'PUT',
      body: JSON.stringify({ name }),
    }),

  getAISettings: () => apiCall('/api/settings/ai'),

  updateAISettings: (model: string, style: string) =>
    apiCall('/api/settings/ai', {
      method: 'PUT',
      body: JSON.stringify({ default_model: model, response_style: style }),
    }),

  getStats: () => apiCall('/api/settings/stats'),
};

export const pluginAPI = {
  getAll: () => apiCall('/api/plugins/'),

  getByCategory: () => apiCall('/api/plugins/?by_category=true'),

  getOne: (slug: string) => apiCall(`/api/plugins/${slug}`),

  toggle: (slug: string, enabled: boolean) =>
    apiCall(`/api/plugins/${slug}/toggle`, {
      method: 'POST',
      body: JSON.stringify({ enabled }),
    }),

  updateConfig: (slug: string, config: Record<string, string>) =>
    apiCall(`/api/plugins/${slug}/config`, {
      method: 'PUT',
      body: JSON.stringify({ config }),
    }),

  getEnabled: () => apiCall('/api/plugins/enabled'),
};

export const toolsAPI = {
  search: (query: string) =>
    apiCall('/api/tools/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),

  quickSearch: (query: string) =>
    apiCall('/api/tools/search/quick', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),

  listFiles: () => apiCall('/api/tools/files'),

  writeFile: (filename: string, content: string) =>
    apiCall('/api/tools/files', {
      method: 'POST',
      body: JSON.stringify({ filename, content }),
    }),

  readFile: (filename: string) => apiCall(`/api/tools/files/${filename}`),

  deleteFile: (filename: string) =>
    apiCall(`/api/tools/files/${filename}`, {
      method: 'DELETE',
    }),

  getWeather: (city: string) =>
    apiCall(`/api/tools/weather?city=${encodeURIComponent(city)}`),

  getWeatherForecast: (city: string, days = 3) =>
    apiCall(
      `/api/tools/weather/forecast?city=${encodeURIComponent(city)}&days=${days}`
    ),
};

export const notificationAPI = {
  getAll: (unreadOnly = false) =>
    apiCall(`/api/notifications/?unread_only=${unreadOnly}`),

  getUnreadCount: () => apiCall('/api/notifications/unread-count'),

  markRead: (id: number) =>
    apiCall(`/api/notifications/${id}/read`, {
      method: 'POST',
    }),

  markAllRead: () =>
    apiCall('/api/notifications/mark-all-read', {
      method: 'POST',
    }),

  delete: (id: number) =>
    apiCall(`/api/notifications/${id}`, {
      method: 'DELETE',
    }),
};
export const analyticsAPI = {
  getOverview: () => apiCall('/api/analytics/overview'),
  getTimeline: () => apiCall('/api/analytics/timeline'),
};
export const workspaceAPI = {
  getAll: () => apiCall('/api/workspaces/'),

  create: (name: string, description: string, icon: string) =>
    apiCall('/api/workspaces/', {
      method: 'POST',
      body: JSON.stringify({ name, description, icon }),
    }),

  getOne: (id: number) => apiCall(`/api/workspaces/${id}`),

  invite: (id: number, email: string, role: string) =>
    apiCall(`/api/workspaces/${id}/invite`, {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    }),

  removeMember: (workspaceId: number, userId: number) =>
    apiCall(`/api/workspaces/${workspaceId}/members/${userId}`, {
      method: 'DELETE',
    }),

  delete: (id: number) =>
    apiCall(`/api/workspaces/${id}`, {
      method: 'DELETE',
    }),
};
export const selfModAPI = {
  getStructure: () => apiCall('/api/self-mod/structure'),

  readFile: (path: string) =>
    apiCall('/api/self-mod/read', {
      method: 'POST',
      body: JSON.stringify({ path }),
    }),

  planChange: (request: string) =>
    apiCall('/api/self-mod/plan', {
      method: 'POST',
      body: JSON.stringify({ request }),
    }),

  generateCode: (request: string, target_file: string) =>
    apiCall('/api/self-mod/generate', {
      method: 'POST',
      body: JSON.stringify({ request, target_file }),
    }),

  applyChange: (target_file: string, new_code: string) =>
    apiCall('/api/self-mod/apply', {
      method: 'POST',
      body: JSON.stringify({ target_file, new_code }),
    }),

  getBackups: () => apiCall('/api/self-mod/backups'),

  searchCode: (query: string) =>
    apiCall('/api/self-mod/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),
};