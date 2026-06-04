---
title: HealthPulse Analytics
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# HealthPulse Analytics

A full-stack healthcare news intelligence platform that scrapes, stores, and visualises health news from WHO, CDC, NIH, and HealthIT.gov.

[![CI](https://github.com/devgandhi2705/HealthpulseAnalytics/actions/workflows/ci.yml/badge.svg)](https://github.com/devgandhi2705/HealthpulseAnalytics/actions/workflows/ci.yml)

---

## Features

- **Multi-source scraping** — WHO, CDC, NIH, HealthIT.gov
- **Full article extraction** — fetches and cleans body text from each article
- **REST API** — articles, analytics, EDA, SQL analytics
- **Interactive dashboard** — KPI cards, bar chart, donut chart, trend line
- **Exploratory data analysis** — keyword frequency, source growth, category trends
- **SQL vs Pandas benchmark** — compare analytics implementations

---

## Architecture

```
HealthpulseAnalytics/
├── app.py                  # Production entry point (HF Spaces / Docker)
├── Dockerfile              # Container build
├── requirements.txt        # Root Python deps (HF Spaces)
│
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI app, CORS, static file mount
│   │   ├── api/            # Route handlers
│   │   ├── analytics/      # Pandas + EDA analytics services
│   │   ├── database/       # SQLAlchemy engine, session, migrations
│   │   ├── models/         # ORM models (Article)
│   │   ├── scraper/        # BaseScraper + 4 source scrapers
│   │   └── services/       # Ingestion + SQL analytics
│   ├── data/               # SQLite database (auto-created, git-ignored)
│   └── requirements.txt    # Backend Python dependencies
│
└── frontend/
    ├── src/
    │   ├── pages/          # Dashboard
    │   ├── components/     # KpiCard, charts
    │   ├── hooks/          # useAnalytics
    │   └── services/       # api.js, analyticsService, articlesService
    └── package.json
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Scraping | requests, BeautifulSoup4, lxml |
| Analytics | pandas, SQLAlchemy aggregations |
| Frontend | React 18, Vite 5 |
| Charts | Recharts 2 |
| HTTP client | axios |
| CI/CD | GitHub Actions |
| Container | Docker |

---

## Installation

### Prerequisites
- Python 3.11+
- Node.js 20+ (for frontend)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env as needed (defaults work out-of-the-box for local dev)
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
# Edit VITE_API_BASE_URL if your backend runs on a different port
```

---

## Running Locally

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the dashboard.
Open [http://localhost:8000/docs](http://localhost:8000/docs) for the API docs.

---

## First Run — Seed Data

The database starts empty. Trigger a scrape to populate it:

```bash
curl -X POST http://localhost:8000/scrape
```

Or open [http://localhost:8000/docs](http://localhost:8000/docs) → POST /scrape → Execute.

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/articles` | Paginated article list (supports filtering, sorting) |
| GET | `/articles/search?q=covid` | Title search |
| GET | `/articles/{id}` | Single article |
| POST | `/scrape` | Trigger scrape cycle |
| GET | `/analytics/overview` | Dashboard KPIs |
| GET | `/analytics/source-distribution` | Articles by source + % |
| GET | `/analytics/category-distribution` | Articles by category + % |
| GET | `/analytics/daily-trend` | Daily publishing trend |
| GET | `/eda/report` | Full EDA report |
| GET | `/eda/keywords?top_n=30` | Top keywords |
| GET | `/eda/monthly-trend` | Monthly article counts |
| GET | `/eda/source-growth` | Per-source monthly growth |
| GET | `/eda/category-over-time` | Category distribution over time |
| GET | `/sql-analytics/summary` | SQL-based analytics |
| GET | `/sql-analytics/benchmark` | SQL vs pandas performance comparison |

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | SQLite auto | PostgreSQL DSN or leave unset for SQLite |
| `CORS_ORIGINS` | `localhost:3000,localhost:5173` | Allowed browser origins |
| `FRONTEND_DIST` | `<repo>/frontend/dist` | Path to Vite build output |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend URL (empty = same-origin) |

---

## Deployment

### Docker (recommended)

```bash
# Build and run
docker build -t healthpulse .
docker run -p 7860:7860 healthpulse

# With persistent database
docker run -p 7860:7860 -v $(pwd)/data:/app/backend/data healthpulse
```

### Hugging Face Spaces

1. Push this repository to [https://huggingface.co/spaces/Devg-01/HealthPulseAnalytics](https://huggingface.co/spaces/Devg-01/HealthPulseAnalytics)
2. Set Space SDK to **Docker** in the Space settings
3. The `Dockerfile` handles everything automatically:
   - Installs Python dependencies
   - Installs Node.js and builds the React frontend
   - Starts the FastAPI server on port 7860

**Required Space secrets** (Settings → Variables and secrets):
- `DATABASE_URL` — optional; leave unset for SQLite
- `CORS_ORIGINS` — optional; leave unset for default

### Single-Server Production

```bash
# Build frontend for same-origin deployment
cd frontend && VITE_API_BASE_URL= npm run build && cd ..

# Start the combined server
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`
Ensure you're running uvicorn from the `backend/` directory when using `app.main:app`, or from the repo root when using `app:app`.

### Database directory not found
The `backend/data/` directory is created automatically on startup. If you see errors, check write permissions.

### CORS errors in browser
Set `CORS_ORIGINS` in `backend/.env` to include your frontend's origin.

### Frontend shows "Failed to load dashboard"
Ensure the backend is running and `VITE_API_BASE_URL` points to it. Run `POST /scrape` to populate the database.

### Charts are empty
No data has been scraped yet. Run `POST /scrape` via the API docs at `/docs`.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes — the CI pipeline validates both backend and frontend automatically
4. Open a pull request

---

## License

MIT
