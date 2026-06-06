import { useState } from 'react'

// ---- Inline SVG icons -------------------------------------------------------

function PulseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  )
}

function GridIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" />
      <rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" />
    </svg>
  )
}

function FileTextIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
    </svg>
  )
}

function MenuIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  )
}

function RefreshIcon({ spinning }) {
  return (
    <svg
      viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
      className={spinning ? 'spin' : ''}
    >
      <path d="M23 4v6h-6" />
      <path d="M1 20v-6h6" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
  )
}

function CollectIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}

function DatabaseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  )
}

// ---- Nav config -------------------------------------------------------------

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Overview',         icon: <GridIcon /> },
  { id: 'articles',  label: 'Article Explorer', icon: <FileTextIcon /> },
]

// ---- Sidebar ----------------------------------------------------------------

function Sidebar({ activePage, onNavigate, totalArticles }) {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar__logo">
        <div className="sidebar__logo-icon"><PulseIcon /></div>
        <div className="sidebar__logo-text">
          <span className="sidebar__logo-name">HealthPulse</span>
          <span className="sidebar__logo-tag">Analytics</span>
        </div>
      </div>

      {/* Nav */}
      <nav className="sidebar__nav">
        <div className="sidebar__nav-group">
          <span className="sidebar__nav-group-label">Platform</span>
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`sidebar__nav-btn${activePage === item.id ? ' sidebar__nav-btn--active' : ''}`}
              onClick={() => onNavigate(item.id)}
            >
              <span className="sidebar__nav-btn-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="sidebar__footer">
        <div className="sidebar__status-row">
          <span className="sidebar__status-dot" />
          <span className="sidebar__status-label">System Online</span>
        </div>
        {totalArticles != null && (
          <p className="sidebar__db-info">
            {totalArticles.toLocaleString()} articles indexed
          </p>
        )}
      </div>
    </aside>
  )
}

// ---- AppLayout (exported) ---------------------------------------------------

export default function AppLayout({
  activePage,
  onNavigate,
  totalArticles,
  sourcesCount,
  onRefresh,
  refreshing,
  onCollect,
  collecting,
  collectMessage,
  collectPhase,
  children,
}) {
  const [mobileOpen, setMobileOpen] = useState(false)

  function navigate(id) {
    onNavigate(id)
    setMobileOpen(false)
  }

  return (
    <div className="app-layout">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />
      )}

      {/* Fixed sidebar */}
      <div className={mobileOpen ? 'sidebar sidebar--open' : 'sidebar'}>
        <Sidebar
          activePage={activePage}
          onNavigate={navigate}
          totalArticles={totalArticles}
        />
      </div>

      {/* Main */}
      <div className="main-content">
        {/* Top bar */}
        <header className="topbar">
          <button
            className="topbar__hamburger"
            onClick={() => setMobileOpen(true)}
            aria-label="Open navigation"
          >
            <MenuIcon />
          </button>

          <div className="topbar__brand">
            <span className="topbar__brand-name">HealthPulse Analytics</span>
            <span className="topbar__brand-tag">Healthcare Intelligence Platform</span>
          </div>

          <div className="topbar__actions">
            {sourcesCount != null && sourcesCount > 0 && (
              <span className="topbar__chip">
                <DatabaseIcon />
                {sourcesCount} source{sourcesCount !== 1 ? 's' : ''}
              </span>
            )}

            {/* Collect Data — shows live status while running */}
            {collecting ? (
              <span className="topbar__collecting">
                <RefreshIcon spinning />
                <span>{collectMessage || 'Collecting…'}</span>
              </span>
            ) : (
              <button
                className="topbar__collect-btn"
                onClick={onCollect}
                title={collectPhase === 'error' ? 'Last collection failed — click to retry' : 'Run a new data collection'}
              >
                <CollectIcon />
                <span>{collectPhase === 'error' ? 'Retry Collection' : 'Collect Data'}</span>
              </button>
            )}

            {/* Refresh analytics from DB */}
            <button
              className="topbar__refresh-btn"
              onClick={onRefresh}
              disabled={refreshing || collecting}
            >
              <RefreshIcon spinning={refreshing} />
              <span>{refreshing ? 'Refreshing…' : 'Refresh'}</span>
            </button>
          </div>
        </header>

        {/* Page content */}
        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  )
}
