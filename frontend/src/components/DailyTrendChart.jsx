import { useMemo, useState } from 'react'
import {
  Area, AreaChart, CartesianGrid, ResponsiveContainer,
  Tooltip, XAxis, YAxis,
} from 'recharts'

const STROKE     = '#1E40AF'
const GRADIENT   = 'trendGrad'

const RANGES = [
  { label: '7D',  days: 7   },
  { label: '30D', days: 30  },
  { label: '90D', days: 90  },
  { label: 'All', days: null },
]

function formatLabel(dateStr) {
  const d = new Date(`${dateStr}T00:00:00`)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

function TrendTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip__label">{label}</p>
      <p className="chart-tooltip__value">{payload[0].value.toLocaleString()} articles</p>
    </div>
  )
}

export default function DailyTrendChart({ data = [] }) {
  const [range, setRange] = useState(RANGES[1]) // default 30D

  const filtered = useMemo(() => {
    if (!range.days) return data
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - range.days)
    return data.filter((d) => new Date(`${d.date}T00:00:00`) >= cutoff)
  }, [data, range])

  const formatted = useMemo(
    () => filtered.map((d) => ({ ...d, label: formatLabel(d.date) })),
    [filtered],
  )

  return (
    <div>
      {/* Range filter tabs */}
      <div className="time-filters" style={{ marginBottom: 16 }}>
        {RANGES.map((r) => (
          <button
            key={r.label}
            className={`time-filter-btn${range.label === r.label ? ' time-filter-btn--active' : ''}`}
            onClick={() => setRange(r)}
          >
            {r.label}
          </button>
        ))}
      </div>

      {formatted.length === 0 ? (
        <div className="chart-empty">
          <svg className="chart-empty__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
          </svg>
          <p>No data for this range</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={formatted} margin={{ top: 4, right: 12, bottom: 0, left: -4 }}>
            <defs>
              <linearGradient id={GRADIENT} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor={STROKE} stopOpacity={0.18} />
                <stop offset="95%" stopColor={STROKE} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
            <XAxis
              dataKey="label"
              axisLine={false} tickLine={false}
              tick={{ fontSize: 11, fill: '#94A3B8' }}
              interval="preserveStartEnd" minTickGap={40}
            />
            <YAxis
              axisLine={false} tickLine={false}
              tick={{ fontSize: 11, fill: '#94A3B8' }}
              tickFormatter={(v) => v.toLocaleString()}
              width={34} allowDecimals={false}
            />
            <Tooltip
              content={<TrendTooltip />}
              cursor={{ stroke: STROKE, strokeWidth: 1, strokeDasharray: '4 4' }}
            />
            <Area
              type="monotone" dataKey="count"
              stroke={STROKE} strokeWidth={2.5}
              fill={`url(#${GRADIENT})`}
              dot={false}
              activeDot={{ r: 5, fill: STROKE, strokeWidth: 2, stroke: '#fff' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  )
}
