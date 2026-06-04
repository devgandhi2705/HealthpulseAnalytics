import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'
import { CHART_COLORS } from '../constants/colors'

function PieTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { category, count, percentage } = payload[0].payload
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip__label">{category}</p>
      <p className="chart-tooltip__value">{count.toLocaleString()} articles</p>
      <p className="chart-tooltip__sub">{percentage}% of total</p>
    </div>
  )
}

function CustomLegend({ payload = [] }) {
  return (
    <ul className="pie-legend">
      {payload.map((entry) => (
        <li key={entry.value} className="pie-legend__item">
          <span className="pie-legend__dot" style={{ background: entry.color }} />
          <span className="pie-legend__label">{entry.value}</span>
        </li>
      ))}
    </ul>
  )
}

export default function CategoryPieChart({ data = [] }) {
  if (!data.length) {
    return (
      <div className="chart-empty">
        <svg className="chart-empty__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="12" r="9" /><path d="M12 3v9l5.5 5.5" />
        </svg>
        <p>No category data yet</p>
      </div>
    )
  }

  const mapped = data.map((d) => ({ ...d, name: d.category }))

  return (
    <ResponsiveContainer width="100%" height={290}>
      <PieChart>
        <Pie
          data={mapped} dataKey="count" nameKey="name"
          cx="50%" cy="44%"
          outerRadius={100} innerRadius={58}
          paddingAngle={2} strokeWidth={0}
        >
          {mapped.map((entry, i) => (
            <Cell key={entry.category} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<PieTooltip />} />
        <Legend content={<CustomLegend />} />
      </PieChart>
    </ResponsiveContainer>
  )
}
