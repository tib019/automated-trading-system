# Trading System - Frontend Dockerfile
FROM node:18-alpine AS builder

# Metadata
LABEL maintainer="Manus AI"
LABEL description="Trading System React Dashboard"
LABEL version="1.0.0"

# Set work directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user
RUN addgroup -g 1001 -S trading && \
    adduser -S trading -u 1001

# Set proper permissions
RUN chown -R trading:trading /usr/share/nginx/html && \
    chown -R trading:trading /var/cache/nginx && \
    chown -R trading:trading /var/log/nginx && \
    chown -R trading:trading /etc/nginx/conf.d

# Switch to non-root user
USER trading

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

