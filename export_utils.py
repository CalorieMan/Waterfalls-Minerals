"""GPX (gpxpy) and KML (stdlib) export for shortlisted waterfalls."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import gpxpy
import gpxpy.gpx


def _waterfalls_by_id(waterfalls: list[dict], ids: Sequence[str]) -> list[dict]:
    by = {w["id"]: w for w in waterfalls}
    return [by[i] for i in ids if i in by]


def export_gpx(
    waterfalls: list[dict], selected_ids: Sequence[str], dest: Path
) -> None:
    rows = _waterfalls_by_id(waterfalls, selected_ids)
    gpx = gpxpy.gpx.GPX()
    gpx.name = "Uvita / Dominical waterfall shortlist"
    gpx.description = "Exported from uvita-waterfalls MVP"
    gpx.time = datetime.now(timezone.utc)
    for w in rows:
        pt = gpxpy.gpx.GPXWaypoint(
            latitude=w["lat"],
            longitude=w["lon"],
            name=w.get("name") or "Waterfall",
            description=w["id"],
        )
        gpx.waypoints.append(pt)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(gpx.to_xml(), encoding="utf-8")


def export_kml(
    waterfalls: list[dict], selected_ids: Sequence[str], dest: Path
) -> None:
    rows = _waterfalls_by_id(waterfalls, selected_ids)
    kml_ns = "http://www.opengis.net/kml/2.2"
    ET.register_namespace("", kml_ns)

    root = ET.Element(f"{{{kml_ns}}}kml")
    doc = ET.SubElement(root, f"{{{kml_ns}}}Document")
    name_el = ET.SubElement(doc, f"{{{kml_ns}}}name")
    name_el.text = "Waterfall shortlist"
    for w in rows:
        pm = ET.SubElement(doc, f"{{{kml_ns}}}Placemark")
        n = ET.SubElement(pm, f"{{{kml_ns}}}name")
        n.text = w.get("name") or "Waterfall"
        desc = ET.SubElement(pm, f"{{{kml_ns}}}description")
        desc.text = w["id"]
        pt = ET.SubElement(pm, f"{{{kml_ns}}}Point")
        coords = ET.SubElement(pt, f"{{{kml_ns}}}coordinates")
        coords.text = f"{w['lon']},{w['lat']},0"
    tree = ET.ElementTree(root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tree.write(dest, encoding="utf-8", xml_declaration=True)
