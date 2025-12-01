"""Configuration utilities for the weather routing engine."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Tuple


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def _env_list(name: str, default: List[int]) -> List[int]:
    raw = os.getenv(name)
    if not raw:
        return default
    parts = []
    for part in raw.split(","):
        try:
            parts.append(int(part.strip()))
        except ValueError:
            continue
    return parts or default


@dataclass
class ModelConfig:
    name: str
    enabled: bool = True
    hours: List[int] = field(default_factory=lambda: [0, 3, 6, 9, 12, 15, 18, 21, 24, 30, 36, 42, 48, 54, 60, 66, 72])


@dataclass
class Config:
    bbox: Tuple[float, float, float, float]
    data_dir: str
    grib_dir: str
    forecast_dir: str
    domain: str
    api_token: str
    gfs: ModelConfig
    ecmwf: ModelConfig
    scheduler_cron: str
    default_route: str = "lakecharles-kemah"
    vessel_speed: float = 6.0


DEFAULT_BBOX = (-98.0, -90.0, 27.0, 31.0)


def load_config() -> Config:
    west = _env_float("WX_BBOX_W", DEFAULT_BBOX[0])
    east = _env_float("WX_BBOX_E", DEFAULT_BBOX[1])
    south = _env_float("WX_BBOX_S", DEFAULT_BBOX[2])
    north = _env_float("WX_BBOX_N", DEFAULT_BBOX[3])

    base_data_dir = os.getenv("WX_DATA_DIR", "data")
    grib_dir = os.getenv("WX_GRIB_DIR", os.path.join(base_data_dir, "grib"))
    forecast_dir = os.getenv("WX_FORECAST_DIR", os.path.join(base_data_dir, "forecasts"))

    gfs_hours = _env_list("WX_GFS_HOURS", [0, 3, 6, 9, 12, 15, 18, 21, 24, 30, 36, 42, 48, 54, 60, 66, 72])
    ecmwf_hours = _env_list("WX_ECMWF_HOURS", [0, 3, 6, 9, 12, 15, 18, 21, 24, 30, 36, 42, 48, 54, 60])

    config = Config(
        bbox=(west, east, south, north),
        data_dir=base_data_dir,
        grib_dir=grib_dir,
        forecast_dir=forecast_dir,
        domain=os.getenv("WX_DOMAIN", "localhost"),
        api_token=os.getenv("WX_API_TOKEN", "changeme"),
        gfs=ModelConfig(name="gfs", enabled=os.getenv("WX_GFS_ENABLED", "1") == "1", hours=gfs_hours),
        ecmwf=ModelConfig(name="ecmwf", enabled=os.getenv("WX_ECMWF_ENABLED", "1") == "1", hours=ecmwf_hours),
        scheduler_cron=os.getenv("WX_SCHEDULER_CRON", "0 */6 * * *"),
        default_route=os.getenv("WX_DEFAULT_ROUTE", "lakecharles-kemah"),
        vessel_speed=_env_float("WX_DEFAULT_SPEED", 6.0),
    )
    os.makedirs(config.grib_dir, exist_ok=True)
    os.makedirs(config.forecast_dir, exist_ok=True)
    return config


__all__ = ["Config", "ModelConfig", "load_config"]
