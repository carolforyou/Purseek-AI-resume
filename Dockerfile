# ---- Stage 1: Build frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Runtime ----
FROM python:3.12-slim
WORKDIR /app

# Install system deps for potential Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend — main.py looks for <project_root>/frontend/dist/
COPY --from=frontend-builder /frontend/dist /app/frontend/dist/

# Railway injects $PORT automatically
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
