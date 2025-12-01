"""Hazard detection logic."""
from __future__ import annotations

from typing import Dict, List

import pandas as pd


def detect_hazards(series: List[dict]) -> List[str]:
    notes: List[str] = []
    if not series:
        return notes
    df = pd.DataFrame(series)
    if "wind_speed" in df:
        if df["wind_speed"].max() >= 25:
            notes.append("Strong winds >25 kt expected")
    if "gust" in df and "wind_speed" in df:
        gust_factor = (df["gust"] / df["wind_speed"].clip(lower=1)).max()
        if gust_factor > 1.25:
            notes.append("Elevated gust factor > 1.25 (squally)")
    if "swh" in df:
        jumps = df["swh"].diff().fillna(0)
        if (jumps > df["swh"].shift(1) * 0.5).any():
            notes.append("Rapid wave height increase")
    if "prate" in df:
        if df["prate"].max() > 2e-4:
            notes.append("Heavy precipitation potential")
    if "cape" in df:
        if df["cape"].max() > 1000:
            notes.append("Convective instability (CAPE > 1000)")
    return notes


def compare_models(gfs: List[dict], ecmwf: List[dict]) -> List[str]:
    notes: List[str] = []
    if not gfs or not ecmwf:
        return notes
    g = pd.DataFrame(gfs)
    e = pd.DataFrame(ecmwf)
    merged = pd.merge(g, e, on="time_utc", suffixes=("_gfs", "_ecmwf"))
    if "wind_speed_gfs" in merged and "wind_speed_ecmwf" in merged:
        diff = (merged["wind_speed_gfs"] - merged["wind_speed_ecmwf"]).abs().max()
        if diff > 10:
            notes.append(f"Wind speed disagreement >10 kt (max diff {diff:.1f})")
    if "swh_gfs" in merged and "swh_ecmwf" in merged:
        diff = (merged["swh_gfs"] - merged["swh_ecmwf"]).abs().max()
        if diff > 1.5:
            notes.append(f"Wave height disagreement >1.5 m (max diff {diff:.1f})")
    return notes


def risk_assessment(series: List[dict]) -> str:
    if not series:
        return "No data"
    df = pd.DataFrame(series)
    max_wind = df.get("wind_speed", pd.Series(dtype=float)).max() or 0
    max_sea = df.get("swh", pd.Series(dtype=float)).max() or 0
    max_gust = df.get("gust", pd.Series(dtype=float)).max() or 0
    if max_wind < 15 and max_sea < 1.2:
        return "Go"
    if max_wind < 25 and max_sea < 2.5 and max_gust < 35:
        return "Caution"
    return "No-Go"


__all__ = ["detect_hazards", "compare_models", "risk_assessment"]
