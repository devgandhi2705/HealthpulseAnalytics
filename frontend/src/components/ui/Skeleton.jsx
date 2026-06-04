export default function Skeleton({ height = 240, className = '' }) {
  return (
    <div
      className={`skeleton shimmer ${className}`}
      style={{ height, borderRadius: 10 }}
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-card__label shimmer" />
      <div className="skeleton-card__value shimmer" />
    </div>
  )
}
