# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ ./

# Build for production
RUN npm run build


# Stage 2: Production image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && rm /etc/nginx/sites-enabled/default

# Install Python dependencies
COPY backend/requirements.txt ./backend/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r backend/requirements.txt -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY firefly_bill_sync/ ./firefly_bill_sync/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /app/static

# Copy nginx config
COPY nginx.conf /etc/nginx/sites-enabled/default

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create data directory for SQLite
RUN mkdir -p /app/data

# Expose port
EXPOSE 80

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:////app/data/family_spending.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
