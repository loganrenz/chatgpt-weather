"""GRIB decoding utilities using xarray + cfgrib."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


VARIABLE_MAP = {
    "10u": "u10",
    "10v": "v10",
    "msl": "mslp",
    "prate": "prate",
    "gust": "gust",
    "cape": "cape",
    "swh": "swh",
    "pp1d": "dwp",
    "mwd": "mwd",
}


class GribDecoder:
    def __init__(self, bbox):
        self.bbox = bbox

    def load_dataset(self, file_paths: Dict[int, Path]) -> xr.Dataset:
        datasets = []
        for hour, path in file_paths.items():
            try:
                ds = xr.open_dataset(path, engine="cfgrib")
            except Exception as exc:
                logger.warning("Failed to open %s: %s", path, exc)
                continue
            ds = self._rename_variables(ds)
            ds = self._subset_bbox(ds)
            ds = ds.assign_coords(fhour=hour)
            datasets.append(ds)
        if not datasets:
            raise FileNotFoundError("No GRIB datasets decoded")
        combined = xr.concat(datasets, dim="fhour")
        return combined

    def _rename_variables(self, ds: xr.Dataset) -> xr.Dataset:
        rename = {k: v for k, v in VARIABLE_MAP.items() if k in ds}
        return ds.rename(rename)

    def _subset_bbox(self, ds: xr.Dataset) -> xr.Dataset:
        west, east, south, north = self.bbox
        lon_name = "longitude" if "longitude" in ds.coords else "lon"
        lat_name = "latitude" if "latitude" in ds.coords else "lat"
        lon = ds[lon_name]
        lat = ds[lat_name]
        subset = ds.where(
            (lon >= west) & (lon <= east) & (lat >= south) & (lat <= north), drop=True
        )
        return subset


def wind_dir_speed(u: xr.DataArray, v: xr.DataArray) -> xr.Dataset:
    speed = np.sqrt(u ** 2 + v ** 2)
    direction = (270 - np.rad2deg(np.arctan2(v, u))) % 360
    return xr.Dataset({"wind_speed": speed, "wind_dir": direction})


__all__ = ["GribDecoder", "wind_dir_speed"]
