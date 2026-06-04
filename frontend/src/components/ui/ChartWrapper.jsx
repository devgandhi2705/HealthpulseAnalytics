import EmptyState from './EmptyState'
import Skeleton from './Skeleton'

export default function ChartWrapper({
  loading,
  error,
  empty,
  height = 260,
  emptyTitle,
  emptyMessage,
  children,
}) {
  if (loading) return <Skeleton height={height} />

  if (error) {
    return (
      <div className="error-block" style={{ minHeight: height }}>
        <div className="error-block__icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <p className="error-block__msg">{error}</p>
      </div>
    )
  }

  if (empty) {
    return (
      <EmptyState
        title={emptyTitle}
        message={emptyMessage}
        icon={
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M8 17v-4M12 17V7M16 17v-2" />
          </svg>
        }
      />
    )
  }

  return children
}
