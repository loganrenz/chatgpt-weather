"""Route definitions and helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Waypoint:
    name: str
    lat: float
    lon: float


@dataclass
class Route:
    id: str
    name: str
    waypoints: List[Waypoint]
    description: str = ""


DEFAULT_ROUTES: Dict[str, Route] = {
    "lakecharles-kemah": Route(
        id="lakecharles-kemah",
        name="Lake Charles to Kemah",
        description="Bord du Lac Marina → Calcasieu Pass → Galveston Entrance → Kemah Boardwalk Marina",
        waypoints=[
            Waypoint("Bord du Lac Marina", 30.2247, -93.2174),
            Waypoint("Calcasieu Pass", 29.7681, -93.3432),
            Waypoint("Galveston Entrance", 29.3567, -94.7210),
            Waypoint("Kemah Boardwalk Marina", 29.5420, -95.0185),
        ],
    )
}


def get_route(route_id: str) -> Route:
    if route_id in DEFAULT_ROUTES:
        return DEFAULT_ROUTES[route_id]
    raise KeyError(f"Route {route_id} not found")


def list_routes() -> List[Route]:
    return list(DEFAULT_ROUTES.values())


__all__ = ["Waypoint", "Route", "DEFAULT_ROUTES", "get_route", "list_routes"]
