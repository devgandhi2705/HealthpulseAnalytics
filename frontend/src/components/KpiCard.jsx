import { SkeletonCard } from './ui/Skeleton'

function TrendTag({ value }) {
  if (value == null) return null
  const positive = value >= 0
  const cls = positive ? 'kpi-trend--up' : 'kpi-trend--down'
  return (
    <span className={`kpi-trend ${cls}`}>
      {positive ? '↑' : '↓'} {Math.abs(value).toLocaleString()}
    </span>
  )
}

export default function KpiCard({
  label,
  value,
  icon,
  accent   = '#1E40AF',
  trend,
  sublabel,
  loading  = false,
}) {
  if (loading) return <SkeletonCard />

  const isText = typeof value === 'string'

  return (
    <div className="kpi-card" style={{ '--kpi-accent': accent }}>
      <div className="kpi-card__icon-wrap">{icon}</div>
      <div className="kpi-card__body">
        <p className="kpi-card__label">{label}</p>
        <p className={`kpi-card__value${isText ? ' kpi-card__value--text' : ''}`}>
          {typeof value === 'number'
            ? value.toLocaleString()
            : (value ?? '—')}
        </p>
        {sublabel && <p className="kpi-card__sublabel">{sublabel}</p>}
      </div>
      {trend != null && <TrendTag value={trend} />}
    </div>
  )
}
