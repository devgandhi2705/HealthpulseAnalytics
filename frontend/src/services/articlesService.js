import api from './api'

/**
 * All article-related API calls.
 * Every method returns the unwrapped response payload (handled by the axios interceptor).
 */
export const articlesService = {
  /**
   * Fetch a paginated, optionally filtered list of articles.
   * @param {Object} params - { page, page_size, source, category, sort_by, sort_order }
   */
  getArticles(params = {}) {
    return api.get('/articles', { params })
  },

  /**
   * Fetch a single article by its numeric ID.
   * Throws if the article is not found (404 → Error from interceptor).
   * @param {number} id
   */
  getArticle(id) {
    return api.get(`/articles/${id}`)
  },

  /**
   * Search articles by title keyword with optional filters.
   * @param {string} q - search term (required, min 1 char)
   * @param {Object} params - { page, page_size, source, category, sort_by, sort_order }
   */
  searchArticles(q, params = {}) {
    return api.get('/articles/search', { params: { q, ...params } })
  },
}
