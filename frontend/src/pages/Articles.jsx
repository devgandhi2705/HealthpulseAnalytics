import { useCallback, useEffect, useRef, useState } from 'react'
import ArticleCard from '../components/ArticleCard'
import Skeleton from '../components/ui/Skeleton'
import EmptyState from '../components/ui/EmptyState'
import useArticles from '../hooks/useArticles'

// ---- Icons -----------------------------------------------------------------

function SearchIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" /><line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  )
}
function ChevronLeftIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="15 18 9 12 15 6" />
    </svg>
  )
}
function ChevronRightIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="9 18 15 12 9 6" />
    </svg>
  )
}

// ---- Debounce hook ---------------------------------------------------------

function useDebounce(value, delay = 350) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

// ---- Page ------------------------------------------------------------------

const PAGE_SIZE = 12

export default function Articles() {
  const [rawSearch, setRawSearch] = useState('')
  const [source, setSource]       = useState('')
  const [category, setCategory]   = useState('')
  const [sortBy, setSortBy]       = useState('published_date')
  const [page, setPage]           = useState(1)
  const search = useDebounce(rawSearch)

  // Reset to page 1 whenever filters change
  const prevFilters = useRef({ search, source, category, sortBy })
  useEffect(() => {
    const prev = prevFilters.current
    if (prev.search !== search || prev.source !== source || prev.category !== category || prev.sortBy !== sortBy) {
      setPage(1)
      prevFilters.current = { search, source, category, sortBy }
    }
  }, [search, source, category, sortBy])

  const { loading, error, articles, total, pages } = useArticles({
    page, pageSize: PAGE_SIZE, source, category, search, sortBy,
  })

  const handleSearchChange = useCallback((e) => setRawSearch(e.target.value), [])

  function buildPageNumbers() {
    if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1)
    if (page <= 4)       return [1, 2, 3, 4, 5, '…', pages]
    if (page >= pages - 3) return [1, '…', pages - 4, pages - 3, pages - 2, pages - 1, pages]
    return [1, '…', page - 1, page, page + 1, '…', pages]
  }

  return (
    <div>
      {/* Page title */}
      <div className="page-title-row">
        <h1 className="page-title">Article Explorer</h1>
        <p className="page-subtitle">
          Search and filter across all collected healthcare news articles.
        </p>
      </div>

      {/* Toolbar */}
      <div className="explorer-toolbar">
        {/* Search */}
        <div className="search-input-wrap">
          <SearchIcon />
          <input
            className="search-input"
            type="text"
            placeholder="Search article titles…"
            value={rawSearch}
            onChange={handleSearchChange}
          />
        </div>

        {/* Source filter */}
        <select
          className="filter-select"
          value={source}
          onChange={(e) => setSource(e.target.value)}
        >
          <option value="">All Sources</option>
          <option value="WHO">WHO</option>
          <option value="CDC">CDC</option>
          <option value="NIH">NIH</option>
          <option value="HealthIT.gov">HealthIT.gov</option>
        </select>

        {/* Sort */}
        <select
          className="filter-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="published_date">Sort by Date</option>
          <option value="title">Sort by Title</option>
          <option value="source">Sort by Source</option>
        </select>

        {/* Result count */}
        {!loading && (
          <span className="explorer-count">
            {total.toLocaleString()} article{total !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {/* Results */}
      {error && (
        <div className="error-block">
          <div className="error-block__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <p className="error-block__msg">{error}</p>
        </div>
      )}

      {loading && (
        <div className="articles-grid">
          {Array.from({ length: PAGE_SIZE }, (_, i) => (
            <Skeleton key={i} height={180} />
          ))}
        </div>
      )}

      {!loading && !error && articles.length === 0 && (
        <EmptyState
          title="No articles found"
          message={
            search || source
              ? 'Try adjusting your search or filters.'
              : 'Run a data collection to import articles.'
          }
          icon={
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
          }
        />
      )}

      {!loading && !error && articles.length > 0 && (
        <>
          <div className="articles-grid">
            {articles.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div className="pagination">
              <button
                className="pagination__btn"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                <ChevronLeftIcon />
              </button>

              {buildPageNumbers().map((pg, i) =>
                pg === '…' ? (
                  <span key={`ell-${i}`} className="pagination__info">…</span>
                ) : (
                  <button
                    key={pg}
                    className={`pagination__btn${page === pg ? ' pagination__btn--active' : ''}`}
                    onClick={() => setPage(pg)}
                  >
                    {pg}
                  </button>
                )
              )}

              <button
                className="pagination__btn"
                onClick={() => setPage((p) => Math.min(pages, p + 1))}
                disabled={page === pages}
              >
                <ChevronRightIcon />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
