# syntax=docker/dockerfile:1

# ---------- Stage 1: Build the static React application ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm test && npm run build

# ---------- Stage 2: Serve via unprivileged Nginx ----------
FROM nginxinc/nginx-unprivileged:1.29-alpine AS runtime

LABEL org.opencontainers.image.title="clinicpulse-frontend" \
      org.opencontainers.image.description="ClinicPulse React dashboard served by unprivileged Nginx" \
      org.opencontainers.image.authors="Tejas Kumat" \
      org.opencontainers.image.licenses="MIT"

# Patch OS packages to keep security vulnerability scans clean
USER root
RUN apk upgrade --no-cache
USER 101

ENV BACKEND_URL=http://backend:8000

COPY --chown=101:101 nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build --chown=101:101 /app/dist /usr/share/nginx/html

# Non-root user binds to 8080
EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --retries=3 CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
