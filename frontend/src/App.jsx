import { useCallback, useEffect, useState } from 'react'
import AppLayout from './layouts/AppLayout'
import Articles from './pages/Articles'
import Dashboard from './pages/Dashboard'
import Onboarding from './pages/Onboarding'
import useAnalytics from './hooks/useAnalytics'
import useScrape from './hooks/useScrape'
import { systemService } from './services/systemService'

// ---- Inner app (rendered after data exists) --------------------------------

function InnerApp() {
  const [activePage, setActivePage] = useState('dashboard')
  const analytics = useAnalytics()
  const scrape = useScrape({ onComplete: analytics.refetch })

  return (
    <AppLayout
      activePage={activePage}
      onNavigate={setActivePage}
      totalArticles={analytics.overview?.total_articles}
      sourcesCount={analytics.overview?.sources_count}
      onRefresh={analytics.refetch}
      refreshing={analytics.loading}
      onCollect={scrape.trigger}
      collecting={scrape.running}
      collectMessage={scrape.message}
      collectPhase={scrape.phase}
    >
      {activePage === 'dashboard' && <Dashboard analytics={analytics} />}
      {activePage === 'articles'  && <Articles />}
    </AppLayout>
  )
}

// ---- Root app (handles onboarding gate) ------------------------------------

export default function App() {
  const [checking, setChecking]     = useState(true)
  const [hasData, setHasData]       = useState(false)
  const [serverDown, setServerDown] = useState(false)

  const checkStatus = useCallback(async () => {
    setChecking(true)
    setServerDown(false)
    try {
      const s = await systemService.getStatus()
      setHasData(s.total_articles > 0)
    } catch {
      // Network error or server not running — show a clear error, not silent onboarding
      setServerDown(true)
      setHasData(false)
    } finally {
      setChecking(false)
    }
  }, [])

  useEffect(() => { checkStatus() }, [checkStatus])

  if (checking) {
    return (
      <div className="state-center">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1E40AF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="spin">
          <path d="M12 2a10 10 0 0 1 10 10" />
        </svg>
        <span style={{ color: 'var(--c-text-muted)', fontSize: '0.875rem' }}>Connecting…</span>
      </div>
    )
  }

  if (serverDown) {
    return (
      <div className="state-center" style={{ flexDirection: 'column', gap: '1rem' }}>
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#EF4444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ opacity: 0.75 }}>
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--c-text-primary)', marginBottom: '0.4rem' }}>
            Cannot reach the backend server
          </p>
          <p style={{ fontSize: '0.82rem', color: 'var(--c-text-secondary)', lineHeight: 1.6, marginBottom: '0.25rem' }}>
            Make sure the server is running, then click Retry.
          </p>
          <code style={{ display: 'block', fontSize: '0.75rem', background: '#F1F5F9', border: '1px solid #E2E8F0', borderRadius: 6, padding: '6px 12px', color: '#475569', marginTop: '0.75rem', marginBottom: '1.25rem', fontFamily: 'monospace' }}>
            uvicorn server:app --host 0.0.0.0 --port 7860
          </code>
        </div>
        <button
          className="btn btn--primary"
          onClick={checkStatus}
          style={{ padding: '10px 28px', borderRadius: 10, fontWeight: 700 }}
        >
          Retry Connection
        </button>
      </div>
    )
  }

  if (!hasData) {
    return <Onboarding onComplete={() => setHasData(true)} />
  }

  return <InnerApp />
}
