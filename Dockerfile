# Multi-stage build for Context OS

# ── Stage 1: Build ──────────────────────────────────────────────────────
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY packages/context-core/pyproject.toml /app/packages/context-core/
COPY packages/context-db/ /app/packages/context-db/
COPY apps/server/pyproject.toml /app/apps/server/
COPY pyproject.toml /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -e "packages/context-core[dev]"
RUN pip install --no-cache-dir -e "apps/server[dev]"

# ── Stage 2: Runtime ───────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY packages/context-core/ /app/packages/context-core/
COPY packages/context-db/ /app/packages/context-db/
COPY apps/server/ /app/apps/server/

# Set working directory
WORKDIR /app/apps/server

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; r = httpx.get('http://localhost:8000/api/v1/health'); assert r.status_code == 200"

# Run server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]