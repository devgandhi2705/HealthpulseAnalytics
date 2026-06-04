import api from './api'

export const systemService = {
  getStatus:       () => api.get('/system/status'),
  getScrapeStatus: () => api.get('/scrape/status'),
  triggerScrape:   () => api.post('/scrape'),
}
