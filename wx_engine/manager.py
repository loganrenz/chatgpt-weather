"""High-level orchestration for forecast generation."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from wx_engine.analysis.hazards import compare_models
from wx_engine.config import Config
from wx_engine.data_sources.ecmwf import ECMWFDownloader
from wx_engine.data_sources.gfs import GFSDownloader
from wx_engine.data_sources.grib import GribDecoder, wind_dir_speed
from wx_engine.interp.interpolator import interpolate_fields
from wx_engine.reports.briefing import build_markdown, markdown_to_html
from wx_engine.reports.timeline import annotate_timeline
from wx_engine.routing.track import generate_track
from wx_engine.routes import Route, get_route

logger = logging.getLogger(__name__)


class ForecastManager:
    def __init__(self, config: Config):
        self.config = config
        self.decoder = GribDecoder(config.bbox)
        self.gfs = GFSDownloader(config.grib_dir, config.bbox, config.gfs.hours)
        self.ecmwf = ECMWFDownloader(config.grib_dir, config.bbox, config.ecmwf.hours)

    def run(self, route_id: str, departure: datetime, speed_knots: float) -> Dict[str, dict]:
        route = get_route(route_id)
        track = generate_track(route, departure, speed_knots)

        model_results: Dict[str, dict] = {}
        for model_name, downloader in [("gfs", self.gfs), ("ecmwf", self.ecmwf)]:
            if not getattr(self.config, model_name).enabled:
                continue
            files = downloader.fetch(None)
            if not files:
                logger.warning("No files fetched for %s", model_name)
                continue
            ds = self.decoder.load_dataset(files)
            if "u10" in ds and "v10" in ds:
                wind = wind_dir_speed(ds["u10"], ds["v10"])
                ds = ds.assign({"wind_speed": wind["wind_speed"], "wind_dir": wind["wind_dir"]})
            points = interpolate_fields(ds, track)
            annotated = annotate_timeline(points)
            md = build_markdown(route.name, model_name, annotated)
            html = markdown_to_html(md)
            model_results[model_name] = {
                "route": route_id,
                "model": model_name,
                "departure": departure.isoformat(),
                "track": annotated,
                "markdown": md,
                "html": html,
            }
            self._persist(route_id, model_name, model_results[model_name])

        # model comparison notes
        if "gfs" in model_results and "ecmwf" in model_results:
            notes = compare_models(model_results["gfs"]["track"], model_results["ecmwf"]["track"])
            model_results["comparison"] = {"notes": notes}
        return model_results

    def _persist(self, route_id: str, model: str, payload: dict) -> None:
        ts = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M")
        out_dir = Path(self.config.forecast_dir) / route_id
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / f"{model}_{ts}.json"
        html_path = out_dir / f"{model}_{ts}.html"
        json_path.write_text(json.dumps(payload, default=str, indent=2))
        html_page = payload["html"]
        html_path.write_text(html_page)
        (out_dir / f"latest_{model}.json").write_text(json.dumps(payload, default=str, indent=2))
        (out_dir / f"latest_{model}.html").write_text(html_page)


__all__ = ["ForecastManager"]
