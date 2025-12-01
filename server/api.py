from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles

from wx_engine.config import load_config
from wx_engine.manager import ForecastManager
from wx_engine.routes import get_route, list_routes

app = FastAPI(title="Marine Weather Routing API")
security = HTTPBearer(auto_error=False)
config = load_config()
manager = ForecastManager(config)


def auth(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    if credentials.scheme.lower() != "bearer" or credentials.credentials != config.api_token:
        raise HTTPException(status_code=403, detail="Invalid token")


@app.get("/api")
def api_root():
    base_path_hint = "Specify your deployment base path (e.g. /app/<owner>/chatgpt-weather) when applicable."
    return {
        "message": "ChatGPT Weather Routing API",
        "endpoints": {
            "health": "/health",
            "routes": "/routes",
            "forecast": "/forecast",
            "latest_report": "/latest-report/{route_id}",
            "web_view": "/web/{route_id}",
        },
        "note": base_path_hint,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/routes")
def routes():
    return [r.__dict__ for r in list_routes()]


@app.post("/forecast")
def forecast(request: Request, body: dict, _: None = Depends(auth)):
    route_id = body.get("route_id", config.default_route)
    departure_raw = body.get("departure_time")
    if not departure_raw:
        raise HTTPException(status_code=400, detail="departure_time required")
    try:
        departure = datetime.fromisoformat(departure_raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid departure_time")
    speed = float(body.get("speed_knots", config.vessel_speed))
    try:
        result = manager.run(route_id, departure, speed)
    except KeyError:
        raise HTTPException(status_code=404, detail="Route not found")
    return result


@app.get("/latest-report/{route_id}")
def latest_report(route_id: str, model: str = "gfs", fmt: str = "json", _: None = Depends(auth)):
    folder = Path(config.forecast_dir) / route_id
    path = folder / f"latest_{model}.{fmt}"
    if not path.exists():
        raise HTTPException(status_code=404, detail="No report available")
    if fmt == "html":
        return HTMLResponse(path.read_text())
    return JSONResponse(json.loads(path.read_text()))


@app.get("/web/{route_id}", response_class=HTMLResponse)
async def web_view(route_id: str, model: str = "gfs"):
    folder = Path(config.forecast_dir) / route_id
    path = folder / f"latest_{model}.html"
    if not path.exists():
        return HTMLResponse("<h1>No report available yet</h1>", status_code=404)
    html = path.read_text()
    page = Path("templates/report_wrapper.html").read_text().replace("{{content}}", html)
    return HTMLResponse(page)


@app.get("/api/latest-report/{route_id}")
def api_latest_report(route_id: str, model: str = "gfs", fmt: str = "json"):
    """Public endpoint for getting latest report (used by Vue frontend)"""
    folder = Path(config.forecast_dir) / route_id
    path = folder / f"latest_{model}.{fmt}"
    if not path.exists():
        raise HTTPException(status_code=404, detail="No report available")
    if fmt == "html":
        return HTMLResponse(path.read_text())
    return JSONResponse(json.loads(path.read_text()))


@app.get("/api/grib-files")
def grib_files():
    """List all GRIB files in the grib directory"""
    grib_dir = Path(config.grib_dir)
    if not grib_dir.exists():
        return []
    
    files = []
    for file_path in grib_dir.rglob("*.grib*"):
        if file_path.is_file():
            stat = file_path.stat()
            # Try to extract model and forecast hour from filename
            # Common patterns: gfs_0.25_20240501_00_f000.grib2, ecmwf_f003.grib
            name = file_path.name
            model = None
            forecast_hour = None
            
            if "gfs" in name.lower():
                model = "GFS"
            elif "ecmwf" in name.lower():
                model = "ECMWF"
            
            # Look for forecast hour pattern like f000, f003, etc.
            match = re.search(r'_f(\d+)', name)
            if match:
                forecast_hour = int(match.group(1))
            
            files.append({
                "name": name,
                "path": str(file_path.relative_to(grib_dir)),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "model": model,
                "forecast_hour": forecast_hour,
            })
    
    # Sort by modified time, most recent first
    files.sort(key=lambda x: x["modified"], reverse=True)
    return files


# Mount static assets first
if Path("frontend/dist/assets").exists():
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")


# Serve the Vue frontend
@app.get("/")
async def serve_spa():
    """Serve the Vue SPA index.html"""
    index_path = Path("frontend/dist/index.html")
    if index_path.exists():
        return HTMLResponse(index_path.read_text())
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}


# Serve other static files from dist
@app.get("/{filename}")
async def serve_static_file(filename: str):
    """Serve static files from frontend/dist"""
    file_path = Path(f"frontend/dist/{filename}")
    if file_path.exists() and file_path.is_file():
        from fastapi.responses import FileResponse
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Not found")
