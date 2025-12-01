from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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


@app.get("/")
def root():
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
