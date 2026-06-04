import { useMemo } from 'react'
import ArticleCard from '../components/ArticleCard'
import CategoryPieChart from '../components/CategoryPieChart'
import DailyTrendChart from '../components/DailyTrendChart'
import EDAInsights from '../components/EDAInsights'
import KeywordChart from '../components/KeywordChart'
import SourceBarChart from '../components/SourceBarChart'
import ChartWrapper from '../components/ui/ChartWrapper'
import { SkeletonCard } from '../components/ui/Skeleton'
import KpiCard from '../components/KpiCard'
import useAnalytics from '../hooks/useAnalytics'
import useArticles from '../hooks/useArticles'
import useEDA from '../hooks/useEDA'
import { SOURCE_COLORS } from '../constants/colors'

// ---- Icons -----------------------------------------------------------------

function ArticleIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  )
}
function GlobeIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  )
}
function TagIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
      <line x1="7" y1="7" x2="7.01" y2="7" />
    </svg>
  )
}
function CalendarIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  )
}
function StarIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
    </svg>
  )
}
function HashIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="4" y1="9" x2="20" y2="9" /><line x1="4" y1="15" x2="20" y2="15" />
      <line x1="10" y1="3" x2="8" y2="21" /><line x1="16" y1="3" x2="14" y2="21" />
    </svg>
  )
}

// ---- Source Leaderboard (sidebar of Source section) -----------------------

function SourceLeaderboard({ data = [], loading }) {
  if (loading) {
    return (
      <div className="source-leaderboard">
        {Array.from({ length: 4 }, (_, i) => (
          <div key={i} className="skeleton shimmer" style={{ height: 52, borderRadius: 10 }} />
        ))}
      </div>
    )
  }

  if (!data.length) {
    return <p style={{ color: 'var(--c-text-muted)', fontSize: '0.85rem', padding: '1rem 0' }}>No source data yet.</p>
  }

  const maxCount = data[0]?.count ?? 1
  return (
    <div className="source-leaderboard">
      {data.map((item, i) => {
        const color = SOURCE_COLORS[item.source] ?? '#1E40AF'
        return (
          <div
            className="source-row"
            key={item.source}
            style={{ '--source-color': color }}
          >
            <span className="source-row__rank">#{i + 1}</span>
            <span className="source-row__dot" />
            <span className="source-row__name">{item.source}</span>
            <div className="source-row__bar-wrap">
              <div
                className="source-row__bar"
                style={{ width: `${(item.count / maxCount) * 100}%` }}
              />
            </div>
            <span className="source-row__count">{item.count.toLocaleString()}</span>
            <span className="source-row__pct">{item.percentage}%</span>
          </div>
        )
      })}
    </div>
  )
}

// ---- Latest Headlines (mini preview) --------------------------------------

function LatestHeadlines() {
  const { loading, error, articles } = useArticles({ pageSize: 6 })

  if (loading) {
    return (
      <div className="articles-grid">
        {Array.from({ length: 6 }, (_, i) => (
          <div key={i} className="skeleton shimmer" style={{ height: 180, borderRadius: 14 }} />
        ))}
      </div>
    )
  }

  if (error || !articles.length) return null

  return (
    <div className="articles-grid">
      {articles.map((a) => <ArticleCard key={a.id} article={a} />)}
    </div>
  )
}

// ---- Dashboard (main export) ----------------------------------------------

export default function Dashboard() {
  const {
    loading, error, overview, sourceDist, categoryDist, trend, refetch,
  } = useAnalytics()

  const {
    loading: edaLoading, error: edaError, keywords,
  } = useEDA()

  // Derived: articles this week
  const thisWeek = useMemo(() => {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - 7)
    return trend.reduce((sum, d) => {
      return new Date(`${d.date}T00:00:00`) >= cutoff ? sum + d.count : sum
    }, 0)
  }, [trend])

  const topCategory = categoryDist[0]?.category ?? null

  if (error) {
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
        <p className="error-page__message">{error}</p>
        <button className="error-page__btn" onClick={refetch}>Try again</button>
      </div>
    )
  }

  const KPI_CARDS = [
    {
      label: 'Total Articles',
      value: overview?.total_articles,
      icon: <ArticleIcon />,
      accent: '#1E40AF',
    },
    {
      label: 'Active Sources',
      value: overview?.sources_count,
      icon: <GlobeIcon />,
      accent: '#10B981',
    },
    {
      label: 'Categories Tracked',
      value: overview?.categories_count,
      icon: <TagIcon />,
      accent: '#06B6D4',
    },
    {
      label: 'Published This Week',
      value: loading ? undefined : thisWeek,
      icon: <CalendarIcon />,
      accent: '#F59E0B',
    },
    {
      label: 'Most Active Source',
      value: overview?.most_active_source,
      icon: <StarIcon />,
      accent: '#8B5CF6',
    },
    {
      label: 'Top Category',
      value: topCategory,
      icon: <HashIcon />,
      accent: '#4F46E5',
    },
  ]

  return (
    <div>
      {/* ── Page title ── */}
      <div className="page-title-row">
        <h1 className="page-title">Healthcare Intelligence Overview</h1>
        <p className="page-subtitle">
          Aggregated from WHO, CDC, NIH &amp; HealthIT.gov · {overview?.total_articles?.toLocaleString() ?? '…'} articles indexed
        </p>
      </div>

      {/* ── Section 1: KPI Cards ── */}
      <section className="section">
        <div className="kpi-grid">
          {KPI_CARDS.map((kpi) => (
            <KpiCard key={kpi.label} {...kpi} loading={loading} />
          ))}
        </div>
      </section>

      {/* ── Section 2: Publication Intelligence ── */}
      <section className="section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Publication Intelligence</h2>
            <p className="section-subtitle">Trend analysis and source contribution</p>
          </div>
        </div>
        <div className="panel-grid panel-grid--2col">
          <div className="panel">
            <div className="panel__header">
              <div>
                <p className="panel__title">Daily Publishing Trend</p>
                <p className="panel__subtitle">Articles published per day</p>
              </div>
            </div>
            <ChartWrapper loading={loading} empty={!trend.length}>
              <DailyTrendChart data={trend} />
            </ChartWrapper>
          </div>

          <div className="panel">
            <div className="panel__header">
              <div>
                <p className="panel__title">Source Leaderboard</p>
                <p className="panel__subtitle">Articles by news organization</p>
              </div>
            </div>
            <SourceLeaderboard data={sourceDist} loading={loading} />
          </div>
        </div>
      </section>

      {/* ── Section 3: Content Analysis ── */}
      <section className="section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Content Analysis</h2>
            <p className="section-subtitle">Category breakdown and keyword intelligence</p>
          </div>
        </div>
        <div className="panel-grid panel-grid--2col">
          <div className="panel">
            <div className="panel__header">
              <p className="panel__title">Category Distribution</p>
            </div>
            <ChartWrapper loading={loading} empty={!categoryDist.length}>
              <CategoryPieChart data={categoryDist} />
            </ChartWrapper>
          </div>

          <div className="panel">
            <div className="panel__header">
              <div>
                <p className="panel__title">Keyword Intelligence</p>
                <p className="panel__subtitle">Top 20 terms across all articles</p>
              </div>
            </div>
            <KeywordChart data={keywords} loading={edaLoading} error={edaError} />
          </div>
        </div>
      </section>

      {/* ── Section 4: Source Coverage (full-width bar chart) ── */}
      <section className="section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Source Coverage</h2>
            <p className="section-subtitle">Volume comparison across all monitored organizations</p>
          </div>
        </div>
        <div className="panel">
          <ChartWrapper loading={loading} empty={!sourceDist.length}>
            <SourceBarChart data={sourceDist} />
          </ChartWrapper>
        </div>
      </section>

      {/* ── Section 5: Intelligence Insights ── */}
      <section className="section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Intelligence Insights</h2>
            <p className="section-subtitle">Computed analytics at a glance</p>
          </div>
        </div>
        <EDAInsights
          overview={overview}
          trend={trend}
          categoryDist={categoryDist}
          sourceDist={sourceDist}
          loading={loading}
        />
      </section>

      {/* ── Section 6: Latest Headlines ── */}
      <section className="section">
        <div className="section-header">
          <div>
            <h2 className="section-title">Latest Headlines</h2>
            <p className="section-subtitle">Most recently published articles</p>
          </div>
        </div>
        <LatestHeadlines />
      </section>
    </div>
  )
}
