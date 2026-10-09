# syntax=docker/dockerfile:1
# Multi-stage container build (REQ-TECH-040/042, REQ-CICD-020/021/022).
# Stage 1: node:20-alpine builds the Vite frontend.
# Stage 2: python:3.12-slim installs uv + the production backend deps and
# copies the built frontend into ./static so one container serves the
# whole stack (REQ-TECH-042). Migrations run before the server starts
# (REQ-CICD-035, REQ-DB-082).

FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json ./

RUN npm ci

COPY frontend/ ./

RUN npm run build

FROM python:3.12-slim AS runtime

ENV UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /app/backend

# curl backs the compose app healthcheck; -rm keeps the layer slim.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system app && useradd --system --gid app --home-dir /app/backend app

RUN pip install --no-cache-dir uv==0.12.13

COPY backend/pyproject.toml backend/uv.lock ./

RUN uv sync --frozen --no-dev

COPY backend/alembic.ini ./alembic.ini

COPY backend/alembic ./alembic

COPY backend/app ./app

COPY --from=frontend-build /app/frontend/dist ./static

RUN chown -R app:app /app/backend

USER app

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
