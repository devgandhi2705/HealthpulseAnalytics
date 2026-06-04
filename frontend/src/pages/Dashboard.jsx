import CategoryPieChart from '../components/CategoryPieChart'
import DailyTrendChart from '../components/DailyTrendChart'
import KpiCard from '../components/KpiCard'
import SourceBarChart from '../components/SourceBarChart'
import useAnalytics from '../hooks/useAnalytics'

// ---- Icons ---------------------------------------------------------------

function ArticleIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  )
}

function SourceIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  )
}

function CategoryIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" />
      <rect x="14" y="3" width="7" height="7" />
      <rect x="14" y="14" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" />
    </svg>
  )
}

function RefreshIcon({ spinning }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={spinning ? { animation: 'spin 0.9s linear infinite' } : undefined}
    >
      <path d="M23 4v6h-6" />
      <path d="M1 20v-6h6" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
  )
}

// ---- KPI configuration ---------------------------------------------------
// One entry = one card. Add or remove entries here to change the KPI row.

const KPI_CONFIG = [
  {
    key: 'articles',
    label: 'Total Articles',
    getValue: (d) => d.total_articles,
    icon: <ArticleIcon />,
    accent: '#3b82f6',
  },
  {
    key: 'sources',
    label: 'Total Sources',
    getValue: (d) => d.sources_count,
    icon: <SourceIcon />,
    accent: '#10b981',
  },
  {
    key: 'categories',
    label: 'Total Categories',
    getValue: (d) => d.categories_count,
    icon: <CategoryIcon />,
    accent: '#8b5cf6',
  },
]

// ---- Page-local UI helpers -----------------------------------------------

/**
 * Wraps a chart in a panel card.
 * Shows a shimmer skeleton in place of the chart while data is loading.
 */
function ChartPanel({ title, loading, fullWidth = false, children }) {
  return (
    <div
      className="panel"
      style={fullWidth ? { gridColumn: '1 / -1' } : undefined}
    >
      <p className="panel__title">{title}</p>
      {loading
        ? <div className="panel-skeleton shimmer" />
        : children}
    </div>
  )
}

/** Full-page error display with a retry action. */
function ErrorPage({ message, onRetry }) {
  return (
    <div className="error-page">
      <div className="error-page__icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
      </div>
      <h2 className="error-page__title">Unable to load dashboard</h2>
      <p className="error-page__message">{message}</p>
      <button className="error-page__btn" onClick={onRetry}>
        Try again
      </button>
    </div>
  )
}

// ---- Dashboard -----------------------------------------------------------

export default function Dashboard() {
  const {
    loading,
    error,
    overview,
    sourceDist,
    categoryDist,
    trend,
    refetch,
  } = useAnalytics()

  if (error) {
    return <ErrorPage message={error} onRetry={refetch} />
  }

  return (
    <div className="page">

      {/* ── Header ── */}
      <header className="page-header">
        <div>
          <h1>HealthPulse Analytics</h1>
          <p>Real-time healthcare news intelligence</p>
        </div>
        <button
          className="refresh-btn"
          onClick={refetch}
          disabled={loading}
          aria-label="Refresh dashboard"
          title="Refresh"
        >
          <RefreshIcon spinning={loading} />
        </button>
      </header>

      {/* ── KPI cards ── */}
      <div className="kpi-grid">
        {KPI_CONFIG.map((kpi) => (
          <KpiCard
            key={kpi.key}
            label={kpi.label}
            value={loading ? undefined : kpi.getValue(overview)}
            icon={kpi.icon}
            accent={kpi.accent}
            loading={loading}
          />
        ))}
      </div>

      {/* ── Charts ── */}
      <div className="panel-grid">
        <ChartPanel title="Articles by Source" loading={loading}>
          <SourceBarChart data={sourceDist} />
        </ChartPanel>

        <ChartPanel title="Articles by Category" loading={loading}>
          <CategoryPieChart data={categoryDist} />
        </ChartPanel>

        <ChartPanel title="Daily Publishing Trend" loading={loading} fullWidth>
          <DailyTrendChart data={trend} />
        </ChartPanel>
      </div>

    </div>
  )
}
