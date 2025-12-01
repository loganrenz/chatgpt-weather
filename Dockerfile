# Frontend builder stage
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Python builder stage
FROM python:3.11-slim AS python-builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libeccodes0 libeccodes-dev libopenjp2-7-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libeccodes0 libopenjp2-7-dev && rm -rf /var/lib/apt/lists/*
COPY --from=python-builder /install /usr/local
COPY . /app
COPY --from=frontend-builder /frontend/dist /app/frontend/dist
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "server.api:app", "--host", "0.0.0.0", "--port", "8000"]
