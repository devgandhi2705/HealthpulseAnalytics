# Cleanup Candidates

These items were identified during the repository audit as potentially improvable
but were NOT removed because confidence was not high enough, or removal would
change existing behaviour. Review before the next major release.

---

## Low-priority / Safe to remove later

| File | Issue | Recommendation |
|------|-------|----------------|
| `backend/app/api/health.py` | `GET /` now returns `index.html` in production, making the route dual-purpose | Consider separating into `GET /` (SPA) and `GET /api/` (JSON) once frontend routing is added |
| `frontend/vite.config.js` | Proxy target `http://localhost:8000` is hardcoded | Extract to `VITE_PROXY_TARGET` env var if backend port changes frequently |

## Medium-priority / Needs investigation

| File | Issue | Recommendation |
|------|-------|----------------|
| `backend/app/api/schemas/analytics.py` | `AnalyticsSummary` bundles all analytics for a single call but this duplicates the EDA report structure | Consider consolidating `AnalyticsSummary` and `EDAReport` if both serve the same dashboard |
| `backend/app/analytics/service.py` | `daily_trend()` returns daily granularity while `eda.py` returns monthly — inconsistency | Standardise on monthly; daily may be too granular for real data |
| `backend/app/scraper/sources/*.py` | CSS selectors are based on observed patterns, not validated against live pages | Validate and update selectors against live WHO/CDC/NIH/HealthIT.gov pages before production launch |

## Monitoring points (not cleanup, but worth tracking)

| Area | Note |
|------|------|
| `backend/app/api/scrape.py` | In-memory `threading.Lock` is reset on process restart — concurrent scrape guard only works in single-process deployments |
| `backend/app/database/init_db.py` | `_migrate_schema()` uses raw SQL `ALTER TABLE` — should be migrated to Alembic before multi-developer workflows or frequent schema changes |
| `frontend/src/hooks/useAnalytics.js` | Fetches all 4 analytics endpoints on every mount — consider caching with React Query or SWR to reduce API load |
| Article text fetching in scrapers | Each scraper makes N additional HTTP requests (one per article) during scraping — this is slow at scale; consider a queue-based approach |

---

*Last reviewed: 2026-06-04*
