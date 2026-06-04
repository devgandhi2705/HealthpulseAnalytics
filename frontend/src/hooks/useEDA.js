import { useCallback, useEffect, useState } from 'react'
import { analyticsService } from '../services/analyticsService'

export default function useEDA() {
  const [loading, setLoading]           = useState(true)
  const [error, setError]               = useState(null)
  const [keywords, setKeywords]         = useState([])
  const [monthlyTrend, setMonthlyTrend] = useState([])
  const [sourceGrowth, setSourceGrowth] = useState(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    Promise.all([
      analyticsService.getKeywords(25),
      analyticsService.getMonthlyTrend(),
      analyticsService.getSourceGrowth(),
    ])
      .then(([kw, mt, sg]) => {
        setKeywords(kw.items ?? [])
        setMonthlyTrend(mt.items ?? [])
        setSourceGrowth(sg)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  return { loading, error, keywords, monthlyTrend, sourceGrowth, refetch: load }
}
