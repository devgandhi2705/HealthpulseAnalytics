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
# On HuggingFace Spaces, /data is the persistent storage mount point (enable
# "Persistent Storage" in the Space settings). The app auto-detects the
# environment via SPACE_ID and writes the SQLite DB there.
# For local Docker use, mount a host directory: -v /host/data:/data
VOLUME ["/data"]

ENV FRONTEND_DIST=/app/frontend/dist
ENV LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1
# Belt-and-suspenders: ensures backend/app is importable even before server.py
# adds it to sys.path programmatically.
ENV PYTHONPATH=/app/backend

# HF Spaces requires port 7860; override with PORT env var for other platforms
EXPOSE 7860

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
