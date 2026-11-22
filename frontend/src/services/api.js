const API_BASE = '/api';

export async function fetchApi(endpoint, options = {}) {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.message || errorData.error || `HTTP error ${res.status}`);
  }
  return res.json();
}

export const PostsAPI = {
  list: (params = '') => fetchApi(`/posts/${params}`),
  get: (id) => fetchApi(`/posts/${id}/`),
  create: (data) => fetchApi('/posts/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data) => fetchApi(`/posts/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => fetchApi(`/posts/${id}/`, { method: 'DELETE' }),
  duplicate: (id) => fetchApi(`/posts/${id}/duplicate/`, { method: 'POST' }),
  revisions: (id) => fetchApi(`/posts/${id}/revisions/`),
  rollback: (id, version) => fetchApi(`/posts/${id}/rollback/`, { method: 'POST', body: JSON.stringify({ version }) }),
};

export const CategoriesAPI = {
  list: () => fetchApi('/categories/'),
  create: (data) => fetchApi('/categories/', { method: 'POST', body: JSON.stringify(data) }),
  delete: (slug) => fetchApi(`/categories/${slug}/`, { method: 'DELETE' }),
};

export const AnalyticsAPI = {
  getDashboard: () => fetchApi('/analytics/dashboard/'),
};

export const AiAPI = {
  readability: (text) => fetchApi('/ai/readability/', { method: 'POST', body: JSON.stringify({ text }) }),
  seo: (payload) => fetchApi('/ai/seo/', { method: 'POST', body: JSON.stringify(payload) }),
  suggestTags: (title, content) => fetchApi('/ai/suggest-tags/', { method: 'POST', body: JSON.stringify({ title, content }) }),
  summarize: (content) => fetchApi('/ai/summarize/', { method: 'POST', body: JSON.stringify({ content }) }),
};
