# syntax=docker/dockerfile:1.7
# Single-service container: compiled React UI + Python FastAPI/Uvicorn API.
# Target: linux/amd64 only. Cross-architecture support is a stretch goal
# (see docs/parts/06-portability.md). Dependency locks are consumed as-is:
# uv.lock for Python, frontend/package-lock.json for npm.

##############################################################################
# Stage 1: build the React/Vite UI bundle from committed npm lockfile.
##############################################################################
FROM --platform=linux/amd64 node:22.12.0-bookworm-slim AS frontend-build
WORKDIR /work/frontend

# Prime the npm cache without executing package lifecycle scripts.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund --ignore-scripts

# Bring in source and produce ./dist through the committed build script.
COPY frontend/ ./
RUN npm run build

##############################################################################
# Stage 2: install the Python runtime dependencies through uv from uv.lock.
# The resulting virtualenv is copied verbatim into the runtime image.
##############################################################################
FROM --platform=linux/amd64 python:3.12.10-slim-bookworm AS python-build
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_CACHE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/ipam-venv \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build
COPY pyproject.toml uv.lock README.md ./
COPY backend ./backend
RUN uv sync --frozen --no-dev

##############################################################################
# Stage 3: minimal runtime image. Non-root user, /data mount, loopback default.
##############################################################################
FROM --platform=linux/amd64 python:3.12.10-slim-bookworm AS runtime

ARG APP_UID=10001
ARG APP_GID=10001

# tini for signal handling; curl for the container HEALTHCHECK.
RUN apt-get update \
 && apt-get install --no-install-recommends -y tini curl \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid ${APP_GID} ipam \
 && useradd  --system --uid ${APP_UID} --gid ${APP_GID} \
             --home-dir /app --shell /usr/sbin/nologin ipam \
 && mkdir -p /app /data \
 && chown -R ipam:ipam /app /data

WORKDIR /app

# Prebuilt virtualenv (Python deps) and the compiled UI assets.
COPY --from=python-build --chown=ipam:ipam /opt/ipam-venv /opt/ipam-venv
COPY --from=frontend-build --chown=ipam:ipam /work/frontend/dist /app/static

ENV PATH="/opt/ipam-venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    IPAM_DATA_DIR=/data \
    IPAM_STATIC_DIR=/app/static

VOLUME ["/data"]
EXPOSE 8000

USER ipam:ipam

# HEALTHCHECK reports readiness only; it does not drive restarts. An unseeded
# service returns 503 SETUP_NEEDED — reported as "unhealthy" by design.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl --fail --silent --show-error --max-time 3 \
      http://127.0.0.1:8000/healthz > /dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "-m", "ipam_demo", "serve", "--host", "0.0.0.0", "--port", "8000"]
