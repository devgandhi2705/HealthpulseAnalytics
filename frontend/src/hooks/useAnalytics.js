import { useCallback, useEffect, useState } from 'react'
import { analyticsService } from '../services/analyticsService'

/**
 * Fetches all four analytics endpoints in parallel and exposes
 * a refetch() function so the Dashboard can retry on error or
 * refresh manually.
 *
 * Returns:
 *   loading      {boolean}
 *   error        {string|null}
 *   overview     {object|null}    — /analytics/overview payload
 *   sourceDist   {Array}          — source-distribution items
 *   categoryDist {Array}          — category-distribution items
 *   trend        {Array}          — daily-trend items
 *   refetch      {function}       — re-run all four calls
 */
export default function useAnalytics() {
  const [loading, setLoading]           = useState(true)
  const [error, setError]               = useState(null)
  const [overview, setOverview]         = useState(null)
  const [sourceDist, setSourceDist]     = useState([])
  const [categoryDist, setCategoryDist] = useState([])
  const [trend, setTrend]               = useState([])

  const load = useCallback(() => {
    setLoading(true)
    setError(null)

    Promise.all([
      analyticsService.getOverview(),
      analyticsService.getSourceDistribution(),
      analyticsService.getCategoryDistribution(),
      analyticsService.getDailyTrend(),
    ])
      .then(([ov, src, cat, tr]) => {
        setOverview(ov)
        setSourceDist(src.items  ?? [])
        setCategoryDist(cat.items ?? [])
        setTrend(tr.items         ?? [])
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  return { loading, error, overview, sourceDist, categoryDist, trend, refetch: load }
}
