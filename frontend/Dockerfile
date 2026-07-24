# Trading System - Frontend Dockerfile (React 19 / Vite 6 / Tailwind 4, pnpm)
# Build stage: glibc-based Node so the prebuilt esbuild/oxide (linux-x64-gnu)
# binaries from the lockfile match the platform.
FROM node:22-bookworm-slim AS builder

WORKDIR /app

# Enable pnpm via corepack
RUN corepack enable

# Copy manifests first for better layer caching
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Install exactly what the lockfile pins.
# --ignore-scripts: skip package postinstall/build scripts. esbuild and the
# tailwind oxide engine ship prebuilt platform binaries via their optional
# dependencies, so no native build step is needed and the install stays
# deterministic and non-interactive in CI.
RUN pnpm install --frozen-lockfile --ignore-scripts

# Copy the rest of the source and build
COPY . .
RUN node node_modules/vite/bin/vite.js build

# Production stage: static files served by nginx
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# SPA + API-proxy config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

# nginx:alpine ships wget (busybox), not curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:3000/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
