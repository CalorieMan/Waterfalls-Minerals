#!/usr/bin/env python3
"""
Fetch waterfalls and drivable roads/tracks near Uvita / Dominical from OpenStreetMap
via the public Overpass API. Writes JSON under ../data/.

Usage (from repo root):
  python3 scripts/fetch_osm.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from storage import ROADS_PATH, WATERFALLS_PATH, ensure_data_dir  # noqa: E402

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# Public Overpass instances may return 406 for the default python-requests User-Agent.
OVERPASS_HEADERS = {
    "User-Agent": "uvita-waterfalls/0.1 (local OSM research; contact: local)",
}

# BBox around Uvita–Dominical–San Isidro foothills (south, west, north, east)
BBOX = (9.02, -84.05, 9.38, -83.52)
SOUTH, WEST, NORTH, EAST = BBOX

QUERY = f"""
[out:json][timeout:180];
(
  node["natural"="waterfall"]({SOUTH},{WEST},{NORTH},{EAST});
  way["natural"="waterfall"]({SOUTH},{WEST},{NORTH},{EAST});
  node["waterway"="waterfall"]({SOUTH},{WEST},{NORTH},{EAST});
  way["waterway"="waterfall"]({SOUTH},{WEST},{NORTH},{EAST});
  node["man_made"="waterfall"]({SOUTH},{WEST},{NORTH},{EAST});
  way["man_made"="waterfall"]({SOUTH},{WEST},{NORTH},{EAST});
);
out center tags;
(
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|track)$"]({SOUTH},{WEST},{NORTH},{EAST});
  /* Omit path/service/living_street here to keep downloads and the map light; add them if you need trail-level routing. */
);
out geom tags;
"""


def _coords_from_geometry(el: dict) -> list[tuple[float, float]]:
    geom = el.get("geometry") or []
    out: list[tuple[float, float]] = []
    for g in geom:
        if "lat" in g and "lon" in g:
            out.append((float(g["lat"]), float(g["lon"])))
    return out


def _waterfall_point(el: dict) -> tuple[float, float] | None:
    if "lat" in el and "lon" in el:
        return float(el["lat"]), float(el["lon"])
    c = el.get("center")
    if c and "lat" in c and "lon" in c:
        return float(c["lat"]), float(c["lon"])
    return None


def parse_waterfalls(elements: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for el in elements:
        if el.get("type") not in ("node", "way", "relation"):
            continue
        tags = el.get("tags") or {}
        if not any(
            tags.get(k) == "waterfall"
            for k in ("natural", "waterway", "man_made")
        ):
            continue
        pt = _waterfall_point(el)
        if pt is None:
            continue
        lat, lon = pt
        oid = el["id"]
        typ = el["type"]
        wid = f"{typ}/{oid}"
        name = tags.get("name") or tags.get("name:en") or ""
        rows.append(
            {
                "id": wid,
                "osm_type": typ,
                "osm_id": oid,
                "name": name or "Unnamed waterfall",
                "lat": lat,
                "lon": lon,
            }
        )
    # Dedupe by id (shouldn't happen)
    seen: set[str] = set()
    uniq: list[dict] = []
    for r in rows:
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        uniq.append(r)
    return uniq


def parse_roads(elements: list[dict]) -> list[list[tuple[float, float]]]:
    lines: list[list[tuple[float, float]]] = []
    for el in elements:
        if el.get("type") != "way":
            continue
        tags = el.get("tags") or {}
        if "highway" not in tags:
            continue
        coords = _coords_from_geometry(el)
        if len(coords) >= 2:
            lines.append(coords)
    return lines


def main() -> None:
    ensure_data_dir()
    print("Querying Overpass API (this can take a minute)…")
    r = requests.post(
        OVERPASS_URL,
        data={"data": QUERY},
        headers=OVERPASS_HEADERS,
        timeout=300,
    )
    r.raise_for_status()
    data = r.json()
    elements = data.get("elements") or []
    wfs = parse_waterfalls(elements)
    roads = parse_roads(elements)
    WATERFALLS_PATH.write_text(
        json.dumps(wfs, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ROADS_PATH.write_text(
        json.dumps({"lines": roads}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Wrote {len(wfs)} waterfalls → {WATERFALLS_PATH}")
    print(f"Wrote {len(roads)} road/track polylines → {ROADS_PATH}")


if __name__ == "__main__":
    main()
