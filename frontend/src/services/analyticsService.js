import api from './api'

export const analyticsService = {
  getOverview:             () => api.get('/analytics/overview'),
  getSourceDistribution:   () => api.get('/analytics/source-distribution'),
  getCategoryDistribution: () => api.get('/analytics/category-distribution'),
  getDailyTrend:           () => api.get('/analytics/daily-trend'),
  getKeywords:             (topN = 25) => api.get('/eda/keywords', { params: { top_n: topN } }),
  getMonthlyTrend:         () => api.get('/eda/monthly-trend'),
  getSourceGrowth:         () => api.get('/eda/source-growth'),
  getCategoryOverTime:     () => api.get('/eda/category-over-time'),
}
