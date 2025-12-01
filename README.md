# ChatGPT Weather Routing

Server-side marine weather routing service for Gulf of Mexico routes. Downloads GFS/ECMWF GRIB data, interpolates along Lake Charles → Kemah route, builds JSON/HTML reports, and serves via FastAPI backend with a modern Vue 3 + TypeScript frontend.

## Features
- **Modern Vue 3 + TypeScript Frontend**: Interactive web interface with Pico CSS styling
  - View weather forecasts with route and model selection
  - Browse and list all GRIB files with metadata
  - Real-time updates and responsive design
- **Python Backend**: FastAPI server for weather data processing
  - GFS 0.25° and ECMWF open data downloaders with configurable bounding box and forecast hours
  - GRIB decoding via `xarray+cfgrib`, hazard detection, Go/Caution/No-Go scoring
  - Hourly vessel track generation at configurable speed
  - REST API endpoints for forecasts, latest reports, and GRIB file listing
  - Legacy HTML report viewer at `/web/<route_id>` for backward compatibility
- APScheduler for in-container automation every 6 hours
- Dockerized deployment with multi-stage builds
- Automated deployment to Narduk Cloud via GitHub Actions

## Requirements
- **Backend**: Python 3.11+, system packages: `libeccodes0 libeccodes-dev libopenjp2-7-dev`
- **Frontend**: Node.js 20+ (for development)

## Setup

### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with token/domain
```

### Frontend (Development)
```bash
cd frontend
npm install
npm run dev  # Runs on http://localhost:5173 with proxy to backend
```

### Frontend (Production Build)
```bash
cd frontend
npm run build  # Builds to frontend/dist/
```

## Running locally

### Development Mode
1. Start the backend:
```bash
uvicorn server.api:app --reload --host 0.0.0.0 --port 8000
```

2. In another terminal, start the frontend dev server:
```bash
cd frontend
npm run dev
```

Visit `http://localhost:5173` for the Vue app with hot reload.

### Production Mode
Build the frontend and run the backend:
```bash
cd frontend && npm run build && cd ..
uvicorn server.api:app --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` for the production app.

### API Endpoints
- Frontend: `http://localhost:8000/`
- Health: `http://localhost:8000/health`
- Routes: `http://localhost:8000/routes`
- GRIB Files: `http://localhost:8000/api/grib-files`
- Latest Report (JSON): `http://localhost:8000/api/latest-report/{route_id}?model=gfs`
- Legacy HTML View: `http://localhost:8000/web/lakecharles-kemah?model=gfs`
- Forecast (protected):
```bash
curl -X POST http://localhost:8000/forecast \
  -H "Authorization: Bearer $WX_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"route_id":"lakecharles-kemah","departure_time":"2024-05-01T12:00:00","speed_knots":6}'
```

## Scheduler
The API process can start APScheduler (see `server/scheduler.py`). You can also run manually:
```bash
python scripts/fetch_and_process.py --route lakecharles-kemah --departure 2024-05-01T12:00:00 --speed 6
```

## Docker
Build and run with Caddy TLS:
```bash
cp .env.example .env
# set WX_DOMAIN, WX_API_TOKEN, etc.
docker-compose up --build -d
```
Caddy terminates TLS for `$WX_DOMAIN` and proxies `/api/*` and `/web/*` to FastAPI. Forecast files are served under `/forecasts/`.

## Deployment on Ubuntu/Linode
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
# clone repo, set DNS A record for WX_DOMAIN to server IP
cd chatgpt-weather
cp .env.example .env
# edit values, especially WX_DOMAIN and WX_API_TOKEN
sudo docker compose up --build -d
```
Ensure port 80/443 are open. Caddy automatically provisions certificates.

## Deployment on Narduk Cloud
The repository includes a GitHub Actions workflow that builds and deploys the container to Narduk Cloud. To enable it:

1. Add a repository secret named `NARDUK_DEPLOY_TOKEN` with the deployment token provided by the repository owner.
2. Push to `main` (or trigger the **Deploy to Narduk Cloud** workflow manually). The action builds the image, pushes it to GHCR, and calls the Narduk Cloud deployment API.
3. The app will be available at `https://cloud.nard.uk/app/<owner>/chatgpt-weather/` with paths automatically rewritten (for example `/app/<owner>/chatgpt-weather/api/forecast` is forwarded to `/api/forecast`). The root path now returns a small JSON index of key endpoints to avoid a default 404.
4. Health checks use the existing `/health` endpoint and the container listens on `0.0.0.0:8000`.

## Notes
- GRIB decoding requires the system packages listed above.
- Model downloaders will skip missing hours; ensure outbound HTTPS is allowed.
- Reports are stored under `data/forecasts/<route_id>/latest_<model>.json|html`.
