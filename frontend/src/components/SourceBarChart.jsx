import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

// Shared across all distribution charts for visual consistency.
export const PALETTE = [
  '#3b82f6', '#10b981', '#8b5cf6', '#f59e0b',
  '#ef4444', '#06b6d4', '#f97316', '#84cc16',
]

// ---- Tooltip ---------------------------------------------------------------

function BarTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const { count, percentage } = payload[0].payload
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip__label">{label}</p>
      <p className="chart-tooltip__value">{count.toLocaleString()} articles</p>
      <p className="chart-tooltip__sub">{percentage}% of total</p>
    </div>
  )
}

// ---- Empty state -----------------------------------------------------------

function EmptyState() {
  return (
    <div className="chart-empty">
      <svg className="chart-empty__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <rect x="3" y="3" width="18" height="18" rx="2" />
        <path d="M8 17v-4M12 17v-8M16 17v-2" />
      </svg>
      <p>No source data yet</p>
    </div>
  )
}

// ---- Chart -----------------------------------------------------------------

/**
 * SourceBarChart
 *
 * Props:
 *   data {Array<{ source: string, count: number, percentage: number }>}
 *        Matches the `items` array from GET /analytics/source-distribution.
 */
export default function SourceBarChart({ data = [] }) {
  if (!data.length) return <EmptyState />

  // Grow the chart height with the number of sources so bars stay readable.
  const chartHeight = Math.max(220, data.length * 44 + 48)

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          horizontal={false}
          stroke="#f3f4f6"
        />
        <XAxis
          type="number"
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11, fill: '#9ca3af' }}
          tickFormatter={(v) => v.toLocaleString()}
        />
        <YAxis
          type="category"
          dataKey="source"
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12, fill: '#374151', fontWeight: 500 }}
          width={80}
        />
        <Tooltip
          content={<BarTooltip />}
          cursor={{ fill: '#f9fafb' }}
        />
        <Bar dataKey="count" radius={[0, 6, 6, 0]} maxBarSize={26}>
          {data.map((entry, i) => (
            <Cell key={entry.source} fill={PALETTE[i % PALETTE.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
