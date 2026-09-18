FROM node:22-alpine AS frontend-builder
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS backend-builder
WORKDIR /build/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev
COPY backend/ ./

FROM python:3.12-slim AS app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/backend/.venv/bin:$PATH"
WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default
COPY --from=backend-builder /build/backend /app/backend
COPY --from=frontend-builder /build/frontend/dist /usr/share/nginx/html
COPY infra/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY infra/supervisord/supervisord.conf /etc/supervisor/conf.d/series-atlas.conf
COPY infra/entrypoint.sh /app/entrypoint.sh
COPY infra/db_wait.py /app/db_wait.py
RUN chmod +x /app/entrypoint.sh
EXPOSE 7777
ENTRYPOINT ["/app/entrypoint.sh"]
