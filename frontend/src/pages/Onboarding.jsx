import { useCallback, useEffect, useRef, useState } from 'react'
import { systemService } from '../services/systemService'

// ---- Phase metadata --------------------------------------------------------

const PHASES = [
  { id: 'initializing', label: 'Initializing',         step: 1 },
  { id: 'collecting',   label: 'Collecting articles',  step: 2 },
  { id: 'processing',   label: 'Processing',           step: 3 },
  { id: 'saving',       label: 'Saving to database',   step: 4 },
  { id: 'complete',     label: 'Complete',             step: 5 },
]

function phaseStep(phaseId) {
  return PHASES.find((p) => p.id === phaseId)?.step ?? 0
}

// ---- Icons -----------------------------------------------------------------

function PulseIcon() {
  return (
    <svg className="ob-hero-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function SpinnerIcon() {
  return (
    <svg className="ob-spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
      <path d="M12 2a10 10 0 0 1 10 10" />
    </svg>
  )
}

// ---- Progress step row -----------------------------------------------------

function ProgressStep({ label, state }) {
  // state: 'done' | 'active' | 'pending'
  return (
    <li className={`ob-step ob-step--${state}`}>
      <span className="ob-step__dot">
        {state === 'done'   && <CheckIcon />}
        {state === 'active' && <SpinnerIcon />}
      </span>
      <span className="ob-step__label">{label}</span>
    </li>
  )
}

// ---- Main component --------------------------------------------------------

export default function Onboarding({ onComplete }) {
  const [phase, setPhase]     = useState('idle')
  const [message, setMessage] = useState('')
  const [result, setResult]   = useState(null)
  const [error, setError]     = useState(null)
  const pollRef               = useRef(null)

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }, [])

  const startPolling = useCallback(() => {
    pollRef.current = setInterval(async () => {
      try {
        const s = await systemService.getScrapeStatus()
        setPhase(s.phase)
        setMessage(s.message ?? '')
        if (s.phase === 'complete') {
          setResult(s.result)
          stopPolling()
          // Brief pause so the user sees "Complete" before the dashboard appears
          setTimeout(() => onComplete(), 1800)
        } else if (s.phase === 'error') {
          setError(s.error || 'Something went wrong. Please try again.')
          stopPolling()
        }
      } catch {
        // transient network hiccup — keep polling
      }
    }, 1200)
  }, [stopPolling, onComplete])

  // On mount, check if a scrape is already running (e.g. page refreshed mid-scrape)
  useEffect(() => {
    systemService.getScrapeStatus().then((s) => {
      const running = ['initializing', 'collecting', 'processing', 'saving']
      if (running.includes(s.phase)) {
        setPhase(s.phase)
        setMessage(s.message ?? '')
        startPolling()
      }
    }).catch(() => {})
  }, [startPolling])

  useEffect(() => () => stopPolling(), [stopPolling])

  const handleStart = useCallback(async () => {
    setError(null)
    setPhase('initializing')
    setMessage('Setting up data collection…')
    try {
      await systemService.triggerScrape()
    } catch (err) {
      // 409 means already running — just start polling
      if (!err.message?.includes('already in progress')) {
        setError(err.message)
        setPhase('idle')
        return
      }
    }
    startPolling()
  }, [startPolling])

  const isRunning = ['initializing', 'collecting', 'processing', 'saving'].includes(phase)
  const isDone    = phase === 'complete'
  const currentStep = phaseStep(phase)

  return (
    <div className="ob-root">
      <div className="ob-card">

        {/* Hero */}
        <div className="ob-hero">
          <PulseIcon />
        </div>

        {/* Heading */}
        <h1 className="ob-title">Welcome to HealthPulse Analytics</h1>
        <p className="ob-subtitle">
          Real-time intelligence from WHO, CDC, NIH, and HealthIT.gov — all in one place.
          Your database is empty. Click below to collect your first batch of articles.
        </p>

        {/* Error banner */}
        {error && (
          <div className="ob-error">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* CTA button — hidden while running or complete */}
        {!isRunning && !isDone && (
          <button className="ob-cta" onClick={handleStart}>
            Start Data Collection
          </button>
        )}

        {/* Progress steps */}
        {(isRunning || isDone) && (
          <div className="ob-progress">
            <p className="ob-progress__msg">{message}</p>
            <ol className="ob-steps">
              {PHASES.map((p) => {
                let state = 'pending'
                if (p.step < currentStep)  state = 'done'
                if (p.step === currentStep) state = isDone ? 'done' : 'active'
                return <ProgressStep key={p.id} label={p.label} state={state} />
              })}
            </ol>
          </div>
        )}

        {/* Completion summary */}
        {isDone && result && (
          <div className="ob-result">
            <span className="ob-result__item"><strong>{result.inserted}</strong> new articles</span>
            <span className="ob-result__sep">·</span>
            <span className="ob-result__item"><strong>{result.sources_scraped?.length ?? 0}</strong> sources</span>
            <span className="ob-result__sep">·</span>
            <span className="ob-result__item"><strong>{result.duration_seconds}s</strong></span>
          </div>
        )}

        {isDone && (
          <p className="ob-redirect">Loading dashboard…</p>
        )}

      </div>
    </div>
  )
}
