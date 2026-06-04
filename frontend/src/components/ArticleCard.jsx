import { CategoryBadge, SourceBadge } from './ui/Badge'

function ExternalLinkIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  )
}

function formatDate(dateStr) {
  if (!dateStr) return null
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function ArticleCard({ article }) {
  const date = formatDate(article.published_date ?? article.scraped_date)

  return (
    <div className="article-card">
      {/* Badges */}
      <div className="article-card__meta">
        <SourceBadge source={article.source} />
        {article.category && <CategoryBadge category={article.category} />}
      </div>

      {/* Title */}
      <p className="article-card__title">
        {article.url ? (
          <a href={article.url} target="_blank" rel="noopener noreferrer">
            {article.title}
          </a>
        ) : (
          article.title
        )}
      </p>

      {/* Summary */}
      {article.summary && (
        <p className="article-card__summary">{article.summary}</p>
      )}

      {/* Footer */}
      <div className="article-card__footer">
        <span className="article-card__date">{date}</span>
        {article.url && (
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="article-card__link"
          >
            Read article <ExternalLinkIcon />
          </a>
        )}
      </div>
    </div>
  )
}
