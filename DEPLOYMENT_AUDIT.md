# HealthPulse Analytics — Deployment Audit

**Audit Date:** 2026-06-04
**Auditor:** Senior Full-Stack / DevOps Engineer
**Status:** ✅ Resolved — deployment-ready

---

## BACKEND ANALYSIS

| Item | Detail |
|------|--------|
| Framework | FastAPI 0.111+ |
| Entry point | `backend/app/main.py` → `app` object |
| Production entry | `app.py` at repo root (for HF Spaces / Docker) |
| Startup process | `lifespan` context manager → `init_db()` → SQLAlchemy `create_all()` + column migrations |
| API architecture | Modular routers in `app/api/` — health, articles, analytics, eda, scrape, sql-analytics |

### API Endpoints
| Prefix | Module | Description |
|--------|--------|-------------|
| `/`, `/health` | `api/health.py` | Root (serves React SPA if built), health check |
| `/articles` | `api/articles.py` | Paginated list, search, single article |
| `/analytics/*` | `api/analytics.py` | Dashboard KPIs, distributions, trend |
| `/eda/*` | `api/eda.py` | Full-text keyword analysis, monthly trends |
| `/scrape` | `api/scrape.py` | Trigger scrape cycle |
| `/sql-analytics/*` | `api/sql_analytics.py` | SQL-based analytics + benchmark |

### Dependency Analysis
All dependencies declared in `backend/requirements.txt`.
No missing required dependencies at the time of audit.

### Environment Variables Required
| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `sqlite:///backend/data/healthpulse.db` | Database connection string |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Allowed browser origins |
| `FRONTEND_DIST` | `<repo>/frontend/dist` | Path to React build output |
| `LOG_LEVEL` | `INFO` | Python logging level |

### Database Architecture
- **ORM:** SQLAlchemy 2.0
- **Default:** SQLite (file-based, zero-config)
- **Production-ready:** PostgreSQL (change `DATABASE_URL`)
- **Schema migrations:** Handled at startup via `init_db._migrate_schema()`
- **Models:** `Article` — 10 fields, 4 indexes, URL unique constraint

### Security Concerns — Pre-audit
| Concern | Severity | Status |
|---------|----------|--------|
| Hardcoded CORS origins | Medium | ✅ Fixed — now reads from `CORS_ORIGINS` env var |
| No `.gitignore` | High | ✅ Fixed — created `.gitignore` |
| Secrets in `.env` committed | High | ✅ Fixed — `.env` files in `.gitignore` |
| `data/` directory not auto-created | Medium | ✅ Fixed — `session.py` creates it |

### Production Readiness Concerns — Pre-audit
| Concern | Status |
|---------|--------|
| No structured logging | ✅ Fixed — `basicConfig` in `main.py` |
| Static file serving not configured | ✅ Fixed — optional mount via `FRONTEND_DIST` |
| No Dockerfile | ✅ Fixed — `Dockerfile` created |
| No CI/CD pipeline | ✅ Fixed — `.github/workflows/ci.yml` created |

---

## FRONTEND ANALYSIS

| Item | Detail |
|------|--------|
| Framework | React 18 |
| Build tool | Vite 5 |
| Routing | None (single-page, no React Router) |
| API client | axios with response interceptor (unwraps `.data`) |
| Charts | Recharts 2 |

### API Integration Strategy
`src/services/api.js` creates a central axios instance.
- **Development:** `VITE_API_BASE_URL=http://localhost:8000`
- **Production:** `VITE_API_BASE_URL=` (empty → same-origin relative paths)

### Environment Variables
| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

### Build Readiness Issues — Pre-audit
| Issue | Status |
|-------|--------|
| Fallback URL `/api` invalid (no `/api` prefix on backend) | ✅ Fixed — fallback changed to `''` (same-origin) |
| No `.env.example` for production docs | ✅ Fixed — updated with production notes |

---

## DEPLOYMENT ANALYSIS

### File Inspection Results

| File | Pre-audit | Post-audit |
|------|-----------|------------|
| `requirements.txt` | Present (backend only) | + root `requirements.txt` for HF Spaces |
| `package.json` | Present | No changes needed |
| `vite.config.js` | Dev proxy hardcoded to `:8000` | Acceptable (dev only) |
| `frontend/.env` | `VITE_API_BASE_URL=http://localhost:8000` | Correct for dev, in `.gitignore` |
| `frontend/.env.example` | Minimal | ✅ Expanded with production docs |
| `backend/.env.example` | Missing | ✅ Created |
| `.gitignore` | Missing | ✅ Created |
| `Dockerfile` | Missing | ✅ Created |
| `Procfile` | Missing | ✅ Created |
| `runtime.txt` | Missing | ✅ Created |
| `.github/workflows/ci.yml` | Missing | ✅ Created |
| `app.py` (root) | Missing | ✅ Created (HF Spaces entry point) |

### Identified Issues and Resolutions

| Issue | Impact | Resolution |
|-------|--------|------------|
| `backend/data/` not auto-created | App crashes on fresh machine | Auto-created in `session.py` |
| CORS origins hardcoded | Cannot configure without code change | Reads from `CORS_ORIGINS` env var |
| No logging configuration | Debugging in prod impossible | `basicConfig` added to `main.py` |
| Frontend fallback URL `/api` incorrect | All prod API calls fail with 404 | Changed to `''` (same-origin) |
| No deployment entry point | HF Spaces / Docker unusable | `app.py` created at root |
| No Docker image | Cannot containerize | `Dockerfile` created |
| No CI/CD | No automated validation | GitHub Actions workflow created |
| No `.gitignore` | DB files, `node_modules`, `.env` would be committed | Created with comprehensive rules |
| No README | No onboarding docs | `README.md` created |

### Hardcoded Values Remaining (Acceptable)
| Location | Value | Reason Acceptable |
|----------|-------|-------------------|
| `vite.config.js` | `proxy target: http://localhost:8000` | Dev-only file, never used in production builds |
| `frontend/.env` | `http://localhost:8000` | Local dev default, in `.gitignore`, not committed |
| `scraper/sources/*.py` | Source URLs (WHO, CDC, NIH) | These are public API endpoints, not configuration |

---

## PLATFORM-SPECIFIC NOTES

### Hugging Face Spaces
- Entry: `uvicorn app:app --host 0.0.0.0 --port 7860`
- The `app.py` at root sets `FRONTEND_DIST` and re-exports the FastAPI `app`
- `frontend/dist/` must be pre-built before deployment (Dockerfile handles this)
- Use Docker SDK for full build automation

### Local Development
```bash
# Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm run dev  # port 3000
```

### Single-Server Production
```bash
cd frontend && VITE_API_BASE_URL= npm run build
uvicorn app:app --host 0.0.0.0 --port 8000
```
