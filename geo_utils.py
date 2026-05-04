"""Small geo helpers — no GDAL/QGIS; good enough for a ~tens-of-km MVP."""

from __future__ import annotations

import math
from typing import Iterable, Sequence

EARTH_RADIUS_M = 6_371_000


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(min(1.0, math.sqrt(a)))


def min_distance_to_polyline_m(
    lat: float, lon: float, coords: Sequence[tuple[float, float]]
) -> float:
    """Minimum distance in meters from a point to a polyline (vertex + sampled segments)."""
    if len(coords) == 0:
        return float("inf")
    best = float("inf")
    for clat, clon in coords:
        best = min(best, haversine_m(lat, lon, clat, clon))
    for (a1, o1), (a2, o2) in zip(coords, coords[1:]):
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            slat = a1 + t * (a2 - a1)
            slon = o1 + t * (o2 - o1)
            best = min(best, haversine_m(lat, lon, slat, slon))
    return best


def min_distance_to_lines_m(
    lat: float, lon: float, lines: Iterable[Sequence[tuple[float, float]]]
) -> float:
    best = float("inf")
    for line in lines:
        best = min(best, min_distance_to_polyline_m(lat, lon, line))
    return best


def center_of_bbox(
    south: float, west: float, north: float, east: float
) -> tuple[float, float]:
    return (south + north) / 2, (west + east) / 2
