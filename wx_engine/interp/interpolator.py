"""Interpolation helpers for model data to track points."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd
import xarray as xr


def interpolate_fields(ds: xr.Dataset, points: List[dict]) -> List[dict]:
    results: List[dict] = []
    if ds is None:
        return results
    lon_name = "longitude" if "longitude" in ds.coords else "lon"
    lat_name = "latitude" if "latitude" in ds.coords else "lat"
    for pt in points:
        time_hour = getattr(pt.get("time_utc"), "hour", 0)
        fhour = min(ds.fhour.values, key=lambda h: abs(h - time_hour))
        subset = ds.sel({lon_name: pt["lon"], lat_name: pt["lat"]}, method="nearest").sel(fhour=fhour)
        row = {
            "time_utc": pt["time_utc"],
            "lat": pt["lat"],
            "lon": pt["lon"],
            "source_fhour": int(fhour),
        }
        for var in ["wind_speed", "wind_dir", "gust", "mslp", "prate", "swh", "dwp", "mwd", "cape"]:
            if var in subset:
                val = subset[var].item() if hasattr(subset[var], "item") else float(subset[var])
                row[var] = float(val)
        results.append(row)
    return results


def summarize_series(series: List[dict]) -> Dict[str, float]:
    if not series:
        return {}
    df = pd.DataFrame(series)
    return {
        "max_wind": float(df.get("wind_speed", pd.Series(dtype=float)).max() or 0),
        "max_gust": float(df.get("gust", pd.Series(dtype=float)).max() or 0),
        "max_swh": float(df.get("swh", pd.Series(dtype=float)).max() or 0),
    }


__all__ = ["interpolate_fields", "summarize_series"]
