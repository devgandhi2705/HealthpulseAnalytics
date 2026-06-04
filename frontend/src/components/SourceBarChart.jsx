import {
  Bar, BarChart, CartesianGrid, Cell,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { CHART_COLORS, SOURCE_COLORS } from '../constants/colors'

// Re-export for charts that import PALETTE from here
export const PALETTE = CHART_COLORS

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

export default function SourceBarChart({ data = [] }) {
  if (!data.length) {
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

  const chartH = Math.max(220, data.length * 52 + 40)

  return (
    <ResponsiveContainer width="100%" height={chartH}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
        <XAxis
          type="number" axisLine={false} tickLine={false}
          tick={{ fontSize: 11, fill: '#94A3B8' }}
          tickFormatter={(v) => v.toLocaleString()}
        />
        <YAxis
          type="category" dataKey="source" axisLine={false} tickLine={false}
          tick={{ fontSize: 12, fill: '#475569', fontWeight: 600 }}
          width={86}
        />
        <Tooltip content={<BarTooltip />} cursor={{ fill: '#F8FAFC' }} />
        <Bar dataKey="count" radius={[0, 6, 6, 0]} maxBarSize={28}>
          {data.map((entry) => (
            <Cell
              key={entry.source}
              fill={SOURCE_COLORS[entry.source] ?? CHART_COLORS[0]}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
