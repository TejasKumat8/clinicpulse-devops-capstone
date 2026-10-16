# syntax=docker/dockerfile:1

# ---------- Stage 1: Build virtualenv (compilers and build artifacts do not reach runtime) ----------
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt \
 && pip uninstall -y pip

# ---------- Stage 2: Hardened, minimal runtime ----------
FROM python:3.12-slim AS runtime

LABEL org.opencontainers.image.title="clinicpulse-backend" \
      org.opencontainers.image.description="ClinicPulse Healthcare Scheduling API (FastAPI)" \
      org.opencontainers.image.authors="Tejas Kumat" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Upgrade OS packages and remove pip/ensurepip to eliminate CVEs in vendored dependencies (Trivy compliance)
RUN apt-get update \
 && apt-get upgrade -y \
 && rm -rf /var/lib/apt/lists/* \
 && python -m pip uninstall -y pip \
 && rm -rf /usr/local/lib/python3.12/ensurepip /usr/local/bin/pip* \
 && groupadd --gid 10001 app \
 && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh \
 && chmod 0755 /usr/local/bin/docker-entrypoint.sh

# Run as non-root user (UID 10001) for strict Kubernetes Pod Security Standards
USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]

ENTRYPOINT ["docker-entrypoint.sh"]
