import { Component } from 'react'

/**
 * Top-level error boundary.
 * Catches any unhandled render error and shows a recovery UI
 * instead of a blank white page.
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary]', error, info.componentStack)
  }

  render() {
    if (this.state.error) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', minHeight: '100vh', gap: '1rem',
          padding: '2rem', textAlign: 'center', background: '#F1F5F9',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
        }}>
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none"
            stroke="#EF4444" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
            style={{ opacity: 0.75 }}>
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <p style={{ fontWeight: 700, fontSize: '1rem', color: '#0F172A', margin: 0 }}>
            Dashboard encountered an error
          </p>
          <p style={{ fontSize: '0.8rem', color: '#64748B', maxWidth: 380, lineHeight: 1.6, margin: 0 }}>
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <button
            onClick={() => { this.setState({ error: null }); window.location.reload() }}
            style={{
              padding: '10px 24px', borderRadius: 10, border: 'none',
              background: '#1E40AF', color: '#fff', fontWeight: 700,
              fontSize: '0.875rem', cursor: 'pointer',
            }}
          >
            Reload
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
