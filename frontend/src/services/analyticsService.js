import api from './api'

/**
 * All analytics-related API calls.
 * Every method returns the unwrapped response payload (handled by the axios interceptor).
 */
export const analyticsService = {
  /** High-level stats for dashboard summary cards. */
  getOverview() {
    return api.get('/analytics/overview')
  },

  /** Article counts + percentage share per news source. */
  getSourceDistribution() {
    return api.get('/analytics/source-distribution')
  },

  /** Article counts + percentage share per category. */
  getCategoryDistribution() {
    return api.get('/analytics/category-distribution')
  },

  /** Daily publishing trend (oldest → newest). */
  getDailyTrend() {
    return api.get('/analytics/daily-trend')
  },
}
