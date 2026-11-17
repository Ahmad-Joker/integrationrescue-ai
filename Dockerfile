# IntegrationRescue competition demo: one container serving the API, the simulated services and the dashboard.
# All data is fictional and generated at runtime; no secrets are baked in (set them as platform env vars).
#
#   docker build -t integrationrescue .
#   docker run -p 8000:8000 -e IR_ACCESS_TOKEN=... -e IR_ADMIN_TOKEN=... -e GEMINI_API_KEY=... integrationrescue

# ---- build the dashboard
FROM node:24-slim AS frontend
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---- runtime
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    IR_DEMO_MODE=1 \
    IR_STATIC_DIR=/app/static \
    IR_EVIDENCE_DIR=/app/evidence/eval \
    IR_VAR_DIR=/data \
    IR_SKIP_DOTENV=1 \
    PORT=8000
WORKDIR /app
COPY backend/ /app/backend/
RUN pip install --upgrade pip && pip install /app/backend && rm -rf /app/backend/build
COPY evidence/ /app/evidence/
COPY --from=frontend /src/frontend/dist /app/static
# Unprivileged user; the only writable location is the fictional state directory.
RUN useradd --create-home --uid 10001 ir && mkdir -p /data && chown ir:ir /data
USER ir
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s \
  CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/api/health', timeout=4)"
CMD ["sh", "-c", "exec uvicorn integrationrescue.api:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
