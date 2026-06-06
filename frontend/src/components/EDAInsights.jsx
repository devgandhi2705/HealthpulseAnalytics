import { useMemo } from 'react'
import { SkeletonCard } from './ui/Skeleton'

function InsightCard({ icon, label, value, sub, accentBg, accentColor }) {
  return (
    <div
      className="insight-card"
      style={{ '--insight-bg': accentBg, '--insight-color': accentColor }}
    >
      <div className="insight-card__icon">{icon}</div>
      <p className="insight-card__label">{label}</p>
      <p className="insight-card__value" title={value}>{value ?? '—'}</p>
      {sub && <p className="insight-card__sub">{sub}</p>}
    </div>
  )
}

// ---- Icons -----------------------------------------------------------------

function ActivityIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  )
}
function ZapIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
    </svg>
  )
}
function PieIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
      <path d="M22 12A10 10 0 0 0 12 2v10z" />
    </svg>
  )
}
function CalendarIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  )
}
function DatabaseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  )
}

// ---- Main ------------------------------------------------------------------

export default function EDAInsights({
  overview,
  trend = [],
  categoryDist = [],
  sourceDist = [],
  loading = false,
}) {
  const insights = useMemo(() => {
    if (!overview) return null

    // Publication velocity: avg articles/day over last 30 days
    const last30 = trend.filter((d) => {
      const cutoff = new Date()
      cutoff.setDate(cutoff.getDate() - 30)
      return new Date(`${d.date}T00:00:00`) >= cutoff
    })
    const velocity = last30.length > 0
      ? (last30.reduce((s, d) => s + d.count, 0) / 30).toFixed(1)
      : '0.0'

    // Top category percentage
    const topCatPct = categoryDist.length > 0
      ? categoryDist[0].percentage
      : null

    // Latest article date
    const latestDate = trend.length > 0
      ? new Date(`${trend[trend.length - 1].date}T00:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
      : null

    // This week articles
    const weekCutoff = new Date()
    weekCutoff.setDate(weekCutoff.getDate() - 7)
    const thisWeek = trend
      .filter((d) => new Date(`${d.date}T00:00:00`) >= weekCutoff)
      .reduce((s, d) => s + d.count, 0)

    return {
      mostActive:      overview.most_active_source?.source ?? null,
      mostActiveCount: overview.most_active_source?.count  ?? null,
      velocity,
      topCatPct,
      latestDate,
      thisWeek,
    }
  }, [overview, trend, categoryDist])

  if (loading) {
    return (
      <div className="insight-grid">
        {Array.from({ length: 5 }, (_, i) => <SkeletonCard key={i} />)}
      </div>
    )
  }

  if (!insights) return null

  return (
    <div className="insight-grid">
      <InsightCard
        icon={<ActivityIcon />}
        label="Top Publisher"
        value={insights.mostActive}
        sub={insights.mostActiveCount != null ? `${insights.mostActiveCount.toLocaleString()} articles` : ''}
        accentBg="#DBEAFE" accentColor="#1E40AF"
      />
      <InsightCard
        icon={<ZapIcon />}
        label="Collection Velocity"
        value={`${insights.velocity}/day`}
        sub="30-day rolling average"
        accentBg="#D1FAE5" accentColor="#065F46"
      />
      <InsightCard
        icon={<PieIcon />}
        label="Top Keyword Share"
        value={insights.topCatPct != null ? `${insights.topCatPct}%` : '—'}
        sub={categoryDist[0]?.category ?? ''}
        accentBg="#CFFAFE" accentColor="#155E75"
      />
      <InsightCard
        icon={<CalendarIcon />}
        label="This Week"
        value={insights.thisWeek.toLocaleString()}
        sub="articles collected"
        accentBg="#FEF3C7" accentColor="#92400E"
      />
      <InsightCard
        icon={<DatabaseIcon />}
        label="Latest Article"
        value={insights.latestDate ?? '—'}
        sub="most recent publication"
        accentBg="#EDE9FE" accentColor="#5B21B6"
      />
    </div>
  )
}
