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