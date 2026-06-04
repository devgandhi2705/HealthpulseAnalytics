/**
 * KpiCard — a single metric display card.
 *
 * Props:
 *   label   {string}      — metric name, e.g. "Total Articles"
 *   value   {number|string} — the metric value; numbers are formatted with toLocaleString
 *   icon    {ReactNode}   — SVG or element shown in the accent icon area
 *   accent  {string}      — CSS colour used for the top border and icon tint (default blue)
 *   loading {boolean}     — show shimmer skeleton instead of real data (default false)
 */
export default function KpiCard({
  label,
  value,
  icon,
  accent = '#3b82f6',
  loading = false,
}) {
  return (
    <div className="kpi-card" style={{ '--kpi-accent': accent }}>
      {loading ? (
        <Skeleton />
      ) : (
        <>
          <div className="kpi-card__header">
            {icon && <span className="kpi-card__icon">{icon}</span>}
            <span className="kpi-card__label">{label}</span>
          </div>
          <p className="kpi-card__value">
            {typeof value === 'number' ? value.toLocaleString() : (value ?? '—')}
          </p>
        </>
      )}
    </div>
  )
}

function Skeleton() {
  return (
    <div className="kpi-skeleton">
      <div className="kpi-skeleton__label shimmer" />
      <div className="kpi-skeleton__value shimmer" />
    </div>
  )
}
