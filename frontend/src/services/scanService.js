import api from './api'

export const scanService = {
  startScan: (awsAccountId, services) =>
    api.post('/api/scan/start', { aws_account_id: awsAccountId, services }),

  getLatest: () => api.get('/api/scan/latest'),

  getHistory: (limit = 20) => api.get(`/api/scan/history?limit=${limit}`),

  getScan: (scanId) => api.get(`/api/scan/${scanId}`),

  deleteScan: (scanId) => api.delete(`/api/scan/${scanId}`),
}

export const awsService = {
  connect: (data) => api.post('/api/aws/connect', data),
  getStatus: () => api.get('/api/aws/status'),
}

export const reportService = {
  generate: (scanId) => api.post(`/api/report/generate/${scanId}`),
  list: () => api.get('/api/report/list'),
  download: (reportId) => api.get(`/api/report/download/${reportId}`, { responseType: 'blob' }),
}

export const alertService = {
  list: (limit = 50) => api.get(`/api/alerts?limit=${limit}`),
  test: () => api.post('/api/alerts/test'),
}

export const adminService = {
  getUsers: () => api.get('/api/admin/users'),
  getScans: () => api.get('/api/admin/scans'),
  getReports: () => api.get('/api/admin/reports'),
  getStats: () => api.get('/api/admin/stats'),
  deleteUser: (userId) => api.delete(`/api/admin/user/${userId}`),
}
