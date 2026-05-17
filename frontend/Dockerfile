# syntax=docker/dockerfile:1.7
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    npm ci --prefer-offline --no-audit --no-fund

FROM node:20-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN --mount=type=cache,target=/root/.npm \
    --mount=type=cache,target=/app/node_modules/.cache \
    npm run build

# Runtime: tiny nginx serving static files. ~25MB vs ~200MB for the `serve` image.
FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback — every unknown path serves index.html so React Router works.
RUN printf 'server { listen 8001; root /usr/share/nginx/html; index index.html; location / { try_files $uri /index.html; } }' \
    > /etc/nginx/conf.d/default.conf \
    && rm -f /etc/nginx/conf.d/default.conf.bak
EXPOSE 8001
CMD ["nginx", "-g", "daemon off;"]
