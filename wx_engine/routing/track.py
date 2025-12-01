"""Track generation utilities."""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Iterable, List

from wx_engine.routes import Route, Waypoint


EARTH_RADIUS_NM = 3440.065  # nautical miles


def haversine_distance_nm(a: Waypoint, b: Waypoint) -> float:
    """Great-circle distance between two waypoints in nautical miles."""
    lat1, lon1, lat2, lon2 = map(math.radians, [a.lat, a.lon, b.lat, b.lon])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(h))


def interpolate_point(a: Waypoint, b: Waypoint, fraction: float) -> Waypoint:
    """Interpolate along a great-circle path between two waypoints."""
    lat1, lon1, lat2, lon2 = map(math.radians, [a.lat, a.lon, b.lat, b.lon])
    delta = haversine_distance_nm(a, b) / EARTH_RADIUS_NM
    if delta == 0:
        return a
    sin_delta = math.sin(delta)
    factor_a = math.sin((1 - fraction) * delta) / sin_delta
    factor_b = math.sin(fraction * delta) / sin_delta
    x = factor_a * math.cos(lat1) * math.cos(lon1) + factor_b * math.cos(lat2) * math.cos(lon2)
    y = factor_a * math.cos(lat1) * math.sin(lon1) + factor_b * math.cos(lat2) * math.sin(lon2)
    z = factor_a * math.sin(lat1) + factor_b * math.sin(lat2)
    lat = math.atan2(z, math.sqrt(x ** 2 + y ** 2))
    lon = math.atan2(y, x)
    return Waypoint(name=f"interp-{fraction:.2f}", lat=math.degrees(lat), lon=math.degrees(lon))


def generate_track(route: Route, departure: datetime, speed_knots: float, step_hours: float = 1.0) -> List[dict]:
    """Generate a time-stamped polyline along the route."""
    if departure.tzinfo is None:
        departure = departure.replace(tzinfo=timezone.utc)
    points: List[dict] = []
    for i in range(len(route.waypoints) - 1):
        start = route.waypoints[i]
        end = route.waypoints[i + 1]
        leg_distance = haversine_distance_nm(start, end)
        leg_hours = leg_distance / speed_knots
        steps = max(1, int(math.ceil(leg_hours / step_hours)))
        for step in range(steps + 1):
            fraction = min(1.0, step / steps)
            wp = interpolate_point(start, end, fraction)
            eta = departure + timedelta(hours=sum(
                haversine_distance_nm(route.waypoints[j], route.waypoints[j + 1])
                for j in range(i)
            ) / speed_knots + fraction * leg_hours)
            points.append({
                "name": start.name if step == 0 else (end.name if fraction >= 0.999 else "leg"),
                "lat": wp.lat,
                "lon": wp.lon,
                "time_utc": eta,
            })
    return points


__all__ = ["generate_track", "haversine_distance_nm", "interpolate_point"]
