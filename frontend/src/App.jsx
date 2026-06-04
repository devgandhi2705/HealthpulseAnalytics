import { useCallback, useEffect, useState } from 'react'
import AppLayout from './layouts/AppLayout'
import Articles from './pages/Articles'
import Dashboard from './pages/Dashboard'
import Onboarding from './pages/Onboarding'
import useAnalytics from './hooks/useAnalytics'
import { systemService } from './services/systemService'

// ---- Inner app (rendered after data exists) --------------------------------

function InnerApp() {
  const [activePage, setActivePage] = useState('dashboard')
  const { loading, overview, refetch } = useAnalytics()

  return (
    <AppLayout
      activePage={activePage}
      onNavigate={setActivePage}
      totalArticles={overview?.total_articles}
      sourcesCount={overview?.sources_count}
      onRefresh={refetch}
      refreshing={loading}
    >
      {activePage === 'dashboard' && <Dashboard />}
      {activePage === 'articles'  && <Articles />}
    </AppLayout>
  )
}

// ---- Root app (handles onboarding gate) ------------------------------------

export default function App() {
  const [checking, setChecking] = useState(true)
  const [hasData, setHasData]   = useState(false)

  const checkStatus = useCallback(async () => {
    try {
      const s = await systemService.getStatus()
      setHasData(s.total_articles > 0)
    } catch {
      setHasData(false)
    } finally {
      setChecking(false)
    }
  }, [])

  useEffect(() => { checkStatus() }, [checkStatus])

  if (checking) {
    return (
      <div className="state-center">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#1E40AF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="spin">
          <path d="M12 2a10 10 0 0 1 10 10" />
        </svg>
        <span style={{ color: 'var(--c-text-muted)', fontSize: '0.875rem' }}>Loading…</span>
      </div>
    )
  }

  if (!hasData) {
    return <Onboarding onComplete={() => setHasData(true)} />
  }

  return <InnerApp />
}
