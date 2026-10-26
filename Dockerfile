# Multi-stage production Dockerfile for ClientOps AI
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Runtime Stage
FROM python:3.12-slim AS runner

WORKDIR /app

# Create non-root user for enterprise container security compliance
RUN groupadd -r clientops && useradd -r -g clientops -d /app -s /sbin/nologin clientops

# Install runtime libpq for PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed wheels/packages from builder
COPY --from=builder /root/.local /home/clientops/.local
ENV PATH=/home/clientops/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copy application files
COPY app/ /app/app/
COPY data/ /app/data/
COPY run_demo.py /app/run_demo.py

RUN chown -R clientops:clientops /app
USER clientops

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
