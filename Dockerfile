# HealthPulse Analytics — Production Docker Image
# Builds the React frontend and serves everything through a single FastAPI process.
#
# Build:  docker build -t healthpulse .
# Run:    docker run -p 7860:7860 healthpulse

FROM python:3.11-slim

WORKDIR /app

# ---------------------------------------------------------------------------
# System dependencies — Node.js for the frontend build
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Python dependencies
# ---------------------------------------------------------------------------
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------------------------------
# Application source
# ---------------------------------------------------------------------------
COPY . .

# ---------------------------------------------------------------------------
# Frontend build
# ---------------------------------------------------------------------------
WORKDIR /app/frontend

# Production build: VITE_API_BASE_URL left empty so API calls are same-origin
# Use npm install (not npm ci) because package-lock.json is git-ignored
RUN npm install && VITE_API_BASE_URL= npm run build

WORKDIR /app

# ---------------------------------------------------------------------------
# Runtime setup
# ---------------------------------------------------------------------------
# Create the SQLite data directory (persists across restarts via a volume)
RUN mkdir -p backend/data

ENV FRONTEND_DIST=/app/frontend/dist
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# HF Spaces requires port 7860; override with PORT env var for other platforms
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
