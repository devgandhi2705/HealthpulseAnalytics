import { useCallback, useEffect, useState } from 'react'
import { articlesService } from '../services/articlesService'

export default function useArticles({
  page      = 1,
  pageSize  = 12,
  source    = '',
  category  = '',
  search    = '',
  sortBy    = 'published_date',
  sortOrder = 'desc',
} = {}) {
  const [loading, setLoading]   = useState(true)
  const [error, setError]       = useState(null)
  const [articles, setArticles] = useState([])
  const [total, setTotal]       = useState(0)
  const [pages, setPages]       = useState(0)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)

    const params = {
      page,
      page_size: pageSize,
      sort_by: sortBy,
      sort_order: sortOrder,
      ...(source   && { source }),
      ...(category && { category }),
    }

    const req = search
      ? articlesService.searchArticles(search, params)
      : articlesService.getArticles(params)

    req
      .then((res) => {
        setArticles(res.items ?? [])
        setTotal(res.total ?? 0)
        setPages(res.pages ?? 0)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [page, pageSize, source, category, search, sortBy, sortOrder])

  useEffect(() => { load() }, [load])

  return { loading, error, articles, total, pages, refetch: load }
}
