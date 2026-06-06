import { useCallback, useEffect, useRef, useState } from 'react'
import { systemService } from '../services/systemService'

const ACTIVE_PHASES = ['initializing', 'collecting', 'processing', 'saving']

export default function useScrape({ onComplete } = {}) {
  const [phase, setPhase]     = useState('idle')
  const [message, setMessage] = useState('')
  const pollRef               = useRef(null)
  const onCompleteRef         = useRef(onComplete)

  useEffect(() => { onCompleteRef.current = onComplete }, [onComplete])

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
        if (s.phase === 'complete' || s.phase === 'error') {
          stopPolling()
          if (s.phase === 'complete') onCompleteRef.current?.()
        }
      } catch {
        // transient network hiccup — keep polling
      }
    }, 1200)
  }, [stopPolling])

  // On mount: resume if a scrape is already in progress (e.g. page refresh mid-run)
  useEffect(() => {
    systemService.getScrapeStatus().then((s) => {
      if (ACTIVE_PHASES.includes(s.phase)) {
        setPhase(s.phase)
        setMessage(s.message ?? '')
        startPolling()
      }
    }).catch(() => {})
  }, [startPolling])

  useEffect(() => () => stopPolling(), [stopPolling])

  const trigger = useCallback(async () => {
    setPhase('initializing')
    setMessage('Setting up data collection…')
    try {
      await systemService.triggerScrape()
    } catch (err) {
      if (err.message?.includes('already in progress')) {
        // already running — just attach the poller
      } else {
        setPhase('error')
        setMessage(err.message || 'Failed to start collection.')
        return
      }
    }
    startPolling()
  }, [startPolling])

  const running = ACTIVE_PHASES.includes(phase)

  return { phase, message, running, trigger }
}
