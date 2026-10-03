# Multi-stage Dockerfile for KoreX Full-Stack Cloud Deployment
# 1. Build React Web SPA
FROM node:20-alpine AS frontend-builder
WORKDIR /app/apps/web
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web/ ./
RUN npm run build

# 2. Python Backend & Production Runtime
FROM python:3.12-slim AS runner
WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY . .

# Copy built frontend assets into the distribution directory
COPY --from=frontend-builder /app/apps/web/dist ./apps/web/dist

EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn services.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
