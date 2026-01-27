import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Wizard API
export const wizardApi = {
  start: () => api.post('/wizard/start'),
  updateStep: (setupId: string, step: number, data: Record<string, unknown>) =>
    api.put(`/wizard/${setupId}/step/${step}`, { step_data: data }),
  getSummary: (setupId: string) => api.get(`/wizard/${setupId}/summary`),
  delete: (setupId: string) => api.delete(`/wizard/${setupId}`),
}

// Components API
export const componentsApi = {
  list: (params?: Record<string, unknown>) => api.get('/components', { params }),
  get: (id: number) => api.get(`/components/${id}`),
  getCategories: () => api.get('/components/categories'),
  getSo101Defaults: (armType: 'single' | 'dual') =>
    api.get('/components/so101-defaults', { params: { arm_type: armType } }),
}

// Recommendations API
export const recommendationsApi = {
  generate: (setupId: string, focusAreas?: string[], constraints?: Record<string, unknown>) =>
    api.post('/recommendations/generate', {
      setup_id: setupId,
      focus_areas: focusAreas,
      constraints,
    }),
  chat: (setupId: string, message: string, history: Array<{ role: string; content: string }>) =>
    api.post('/recommendations/chat', {
      setup_id: setupId,
      message,
      history,
    }),
}

// Pricing API
export const pricingApi = {
  getComponentPrices: (componentId: number) => api.get(`/pricing/component/${componentId}`),
  searchPrices: (componentName: string, vendorPreference?: string) =>
    api.post('/pricing/search', {
      component_name: componentName,
      vendor_preference: vendorPreference,
    }),
  getSetupPricing: (setupId: string) => api.get(`/pricing/setup/${setupId}`),
  refreshPrices: (componentId: number) => api.post(`/pricing/refresh/${componentId}`),
}

// Comparison API
export const comparisonApi = {
  compare: (componentIds: number[]) =>
    api.post('/comparison/compare', { component_ids: componentIds }),
}

// Export API
export const exportApi = {
  pdf: (setupId: string, options?: Record<string, unknown>) =>
    api.post('/export/pdf', { setup_id: setupId, ...options }, { responseType: 'blob' }),
  json: (setupId: string, options?: Record<string, unknown>) =>
    api.post('/export/json', { setup_id: setupId, ...options }),
  shoppingList: (setupId: string) => api.post(`/export/shopping-list?setup_id=${setupId}`),
}

// Docs API
export const docsApi = {
  list: (params?: Record<string, unknown>) => api.get('/docs', { params }),
  get: (slug: string) => api.get(`/docs/${slug}`),
  search: (query: string) => api.get('/docs/search/fulltext', { params: { q: query } }),
  getCategories: () => api.get('/docs/categories'),
}
