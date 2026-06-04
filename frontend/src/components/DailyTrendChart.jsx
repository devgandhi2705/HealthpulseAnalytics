import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

const STROKE = '#3b82f6'
const GRADIENT_ID = 'dailyTrendFill'

// Append 'T00:00:00' to avoid UTC-to-local shifts when parsing date-only strings.
function formatAxisDate(dateStr) {
  const d = new Date(`${dateStr}T00:00:00`)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// ---- Tooltip ---------------------------------------------------------------

function TrendTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip__label">{label}</p>
      <p className="chart-tooltip__value">
        {payload[0].value.toLocaleString()} articles
      </p>
    </div>
  )
}

// ---- Empty state -----------------------------------------------------------

function EmptyState() {
  return (
    <div className="chart-empty">
      <svg className="chart-empty__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
      <p>No trend data yet</p>
    </div>
  )
}

// ---- Chart -----------------------------------------------------------------

/**
 * DailyTrendChart — area chart of published articles per day.
 *
 * Props:
 *   data {Array<{ date: string, count: number }>}
 *        Matches the `items` array from GET /analytics/daily-trend.
 *        `date` is an ISO date string e.g. "2025-05-14".
 */
export default function DailyTrendChart({ data = [] }) {
  if (!data.length) return <EmptyState />

  const formatted = data.map((item) => ({
    ...item,
    label: formatAxisDate(item.date),
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart
        data={formatted}
        margin={{ top: 4, right: 16, bottom: 0, left: 0 }}
      >
        <defs>
          <linearGradient id={GRADIENT_ID} x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%"  stopColor={STROKE} stopOpacity={0.15} />
            <stop offset="95%" stopColor={STROKE} stopOpacity={0} />
          </linearGradient>
        </defs>

        <CartesianGrid
          strokeDasharray="3 3"
          vertical={false}
          stroke="#f3f4f6"
        />
        <XAxis
          dataKey="label"
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11, fill: '#9ca3af' }}
          interval="preserveStartEnd"
          minTickGap={40}
        />
        <YAxis
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 11, fill: '#9ca3af' }}
          tickFormatter={(v) => v.toLocaleString()}
          width={36}
          allowDecimals={false}
        />
        <Tooltip
          content={<TrendTooltip />}
          cursor={{
            stroke: STROKE,
            strokeWidth: 1,
            strokeDasharray: '4 4',
          }}
        />
        <Area
          type="monotone"
          dataKey="count"
          stroke={STROKE}
          strokeWidth={2}
          fill={`url(#${GRADIENT_ID})`}
          dot={false}
          activeDot={{ r: 4, fill: STROKE, strokeWidth: 2, stroke: '#fff' }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
