"""
Streamlit MVP: waterfalls near Uvita / Dominical with OSM data, filters, and shortlist.
Run: streamlit run app.py
"""

from __future__ import annotations

import io
import zipfile
from datetime import datetime
from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

import export_utils
import geo_utils
from storage import (
    DATA,
    ROADS_PATH,
    USER_PATH,
    WATERFALLS_PATH,
    ensure_data_dir,
    load_json,
    load_user_state,
    save_user_state,
)

# Map center between Uvita and Dominical
DEFAULT_CENTER = (9.21, -83.80)
DEFAULT_ZOOM = 11

DARK_TILE = "CartoDB dark_matter"
LIGHT_TILE = "OpenStreetMap"


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
          --uw-bg: #0e1117;
          --uw-card: #161b22;
          --uw-accent: #58a6ff;
          --uw-muted: #8b949e;
        }
        [data-testid="stSidebar"] {
          background: linear-gradient(180deg, #12151c 0%, #0e1117 100%);
        }
        [data-testid="stAppViewContainer"] .block-container {
          padding-top: 1rem;
        }
        div[data-testid="stExpander"] details {
          border: 1px solid #30363d;
          border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _load_waterfalls() -> list[dict]:
    return list(load_json(WATERFALLS_PATH, []))


@st.cache_data(show_spinner=False)
def _load_road_lines() -> list[list[tuple[float, float]]]:
    raw = load_json(ROADS_PATH, {})
    lines = raw.get("lines") or []
    out: list[list[tuple[float, float]]] = []
    for line in lines:
        parsed: list[tuple[float, float]] = []
        for pair in line:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                parsed.append((float(pair[0]), float(pair[1])))
        if len(parsed) >= 2:
            out.append(parsed)
    return out


def _category(wid: str, user: dict[str, list[str]]) -> str:
    if wid in user["saved_ids"]:
        return "saved"
    if wid in user["ignored_ids"]:
        return "ignored"
    return "known"


def _nearest_waterfall(
    lat: float, lon: float, waterfalls: list[dict], max_m: float = 400.0
) -> dict | None:
    best: dict | None = None
    best_d = float("inf")
    for w in waterfalls:
        d = geo_utils.haversine_m(lat, lon, w["lat"], w["lon"])
        if d < best_d:
            best_d = d
            best = w
    if best is None or best_d > max_m:
        return None
    return best


def _filtered(
    waterfalls: list[dict],
    road_lines: list[list[tuple[float, float]]],
    user: dict[str, list[str]],
    radius_km: float,
    max_road_km: float | None,
    categories: set[str],
    center: tuple[float, float],
) -> list[dict]:
    out: list[dict] = []
    for w in waterfalls:
        cat = _category(w["id"], user)
        if cat not in categories:
            continue
        d_center = geo_utils.haversine_m(center[0], center[1], w["lat"], w["lon"])
        if d_center > radius_km * 1000:
            continue
        d_road: float | None = None
        if road_lines:
            d_road = geo_utils.min_distance_to_lines_m(w["lat"], w["lon"], road_lines)
        if max_road_km is not None and d_road is not None and d_road > max_road_km * 1000:
            continue
        out.append({**w, "_cat": cat, "_d_road_m": d_road})
    return out


def _thin_polyline(line: list[tuple[float, float]], max_pts: int) -> list[tuple[float, float]]:
    if len(line) <= max_pts:
        return line
    n = len(line)
    return [line[round(i * (n - 1) / (max_pts - 1))] for i in range(max_pts)]


def _roads_for_display(
    road_lines: list[list[tuple[float, float]]],
    max_lines: int = 1400,
    max_pts_per_line: int = 36,
) -> list[list[tuple[float, float]]]:
    """Subset + vertex cap so Folium stays responsive (full geometry still used for filters)."""
    lines = road_lines
    if len(lines) > max_lines:
        step = max(1, len(lines) // max_lines)
        lines = lines[::step][:max_lines]
    return [_thin_polyline(list(line), max_pts_per_line) for line in lines]


def _build_map(
    rows: list[dict],
    road_lines: list[list[tuple[float, float]]],
    dark: bool,
    center: tuple[float, float],
    zoom: int,
) -> folium.Map:
    tiles = DARK_TILE if dark else LIGHT_TILE
    m = folium.Map(location=list(center), zoom_start=zoom, tiles=tiles)
    if dark:
        folium.TileLayer(LIGHT_TILE, name="Light (OSM)", overlay=False, control=True).add_to(m)
    fg_roads = folium.FeatureGroup(name="Roads & tracks (simplified view)")
    for line in _roads_for_display(road_lines):
        folium.PolyLine(
            locations=[(lat, lon) for lat, lon in line],
            color="#6e7681",
            weight=2,
            opacity=0.65,
        ).add_to(fg_roads)
    fg_roads.add_to(m)

    for w in rows:
        cat = w.get("_cat", "known")
        if cat == "saved":
            color, radius = "#3fb950", 9
        elif cat == "ignored":
            color, radius = "#484f58", 7
        else:
            color, radius = "#58a6ff", 8
        folium.CircleMarker(
            location=(w["lat"], w["lon"]),
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=1,
            popup=folium.Popup(
                f"<b>{w.get('name','')}</b><br/><code>{w['id']}</code>",
                max_width=240,
            ),
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m


def main() -> None:
    st.set_page_config(
        page_title="Uvita & Dominical waterfalls",
        page_icon="💧",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_css()
    ensure_data_dir()

    if "user" not in st.session_state:
        st.session_state.user = load_user_state()
    if "last_click" not in st.session_state:
        st.session_state.last_click = None

    user = st.session_state.user
    waterfalls = _load_waterfalls()
    road_lines = _load_road_lines()

    st.title("Waterfalls near Uvita & Dominical")
    st.caption("Local MVP — OSM via Overpass, no Docker / QGIS.")

    with st.sidebar:
        st.subheader("Filters")
        radius_km = st.slider("Radius from map center (km)", 1, 60, 25, 1)
        road_filter_enabled = st.checkbox("Limit by distance to a road/track", value=False)
        max_road_km = None
        if road_filter_enabled:
            max_road_km = st.slider("Max distance to nearest road (km)", 0.1, 15.0, 3.0, 0.1)
        cat_options = st.multiselect(
            "Categories",
            options=["known", "saved", "ignored"],
            default=["known", "saved"],
            help="Known = from OSM and not in your lists. Saved / ignored are your tags.",
        )
        categories = set(cat_options) if cat_options else {"known", "saved", "ignored"}

        st.divider()
        dark_mode = st.toggle("Dark map tiles", value=True)
        use_gps_center = st.checkbox("Use default Uvita–Dominical center", value=True)
        if not use_gps_center:
            c1, c2 = st.columns(2)
            with c1:
                clat = st.number_input(
                    "Center lat", value=DEFAULT_CENTER[0], format="%.5f", key="filter_center_lat"
                )
            with c2:
                clon = st.number_input(
                    "Center lon", value=DEFAULT_CENTER[1], format="%.5f", key="filter_center_lon"
                )
            center = (float(clat), float(clon))
        else:
            center = DEFAULT_CENTER

        st.divider()
        st.subheader("Data")
        st.text(f"{WATERFALLS_PATH.name}: {len(waterfalls)} rows")
        st.text(f"{ROADS_PATH.name}: {len(road_lines)} lines")
        if not WATERFALLS_PATH.exists():
            st.warning("No waterfall file yet. Run `python3 scripts/fetch_osm.py` from the repo root.")
        if st.button("Reload OSM files from disk", help="Run after fetch_osm.py updates JSON"):
            _load_waterfalls.clear()
            _load_road_lines.clear()
            st.rerun()

    rows = _filtered(
        waterfalls,
        road_lines,
        user,
        radius_km=radius_km,
        max_road_km=max_road_km,
        categories=categories,
        center=center,
    )

    col_map, col_panel = st.columns([2.2, 1], gap="medium")

    with col_map:
        m = _build_map(rows, road_lines, dark_mode, center, DEFAULT_ZOOM)
        out = st_folium(
            m,
            width=None,
            height=520,
            returned_objects=["last_object_clicked"],
            key="folium_map",
        )
        if out and out.get("last_object_clicked"):
            lc = out["last_object_clicked"]
            lat, lng = lc.get("lat"), lc.get("lng")
            if lat is not None and lng is not None:
                st.session_state.last_click = (float(lat), float(lng))

    with col_panel:
        st.subheader("Map click → shortlist")
        if st.session_state.last_click:
            lat, lon = st.session_state.last_click
            hit = _nearest_waterfall(lat, lon, waterfalls)
            st.write(f"Last click: `{lat:.5f}, {lon:.5f}`")
            if hit:
                st.write(f"Nearest waterfall: **{hit['name']}** (`{hit['id']}`)")
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button("Save", type="primary", key="btn_save"):
                        ids = list(dict.fromkeys(user["saved_ids"] + [hit["id"]]))
                        user["saved_ids"] = ids
                        user["ignored_ids"] = [i for i in user["ignored_ids"] if i != hit["id"]]
                        save_user_state(user)
                        st.session_state.user = user
                        st.rerun()
                with b2:
                    if st.button("Ignore", key="btn_ignore"):
                        ids = list(dict.fromkeys(user["ignored_ids"] + [hit["id"]]))
                        user["ignored_ids"] = ids
                        user["saved_ids"] = [i for i in user["saved_ids"] if i != hit["id"]]
                        save_user_state(user)
                        st.session_state.user = user
                        st.rerun()
                with b3:
                    if st.button("Clear click", key="btn_clear"):
                        st.session_state.last_click = None
                        st.rerun()
            else:
                st.caption("No waterfall within ~400 m of that click.")
        else:
            st.caption("Click the map near a marker to select a waterfall.")

        st.divider()
        st.subheader("Shortlist")
        saved = [w for w in waterfalls if w["id"] in user["saved_ids"]]
        if not saved:
            st.caption("No saved waterfalls yet.")
        else:
            for w in saved:
                rr = st.columns([4, 1])
                with rr[0]:
                    st.markdown(f"**{w['name']}**  \n`{w['id']}`")
                with rr[1]:
                    if st.button("✕", key=f"rm_{w['id']}", help="Remove from shortlist"):
                        user["saved_ids"] = [i for i in user["saved_ids"] if i != w["id"]]
                        save_user_state(user)
                        st.session_state.user = user
                        st.rerun()

        st.divider()
        st.subheader("Export")
        if user["saved_ids"]:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            p_gpx = Path(f"shortlist_{ts}.gpx")
            p_kml = Path(f"shortlist_{ts}.kml")
            tmp_root = DATA / "_export_tmp"
            tmp_root.mkdir(parents=True, exist_ok=True)
            gpx_path = tmp_root / p_gpx.name
            kml_path = tmp_root / p_kml.name
            export_utils.export_gpx(waterfalls, user["saved_ids"], gpx_path)
            export_utils.export_kml(waterfalls, user["saved_ids"], kml_path)
            zbuf = io.BytesIO()
            with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(gpx_path, arcname=p_gpx.name)
                zf.write(kml_path, arcname=p_kml.name)
            st.download_button(
                label="Download GPX + KML (zip)",
                data=zbuf.getvalue(),
                file_name=f"waterfall_shortlist_{ts}.zip",
                mime="application/zip",
            )
            st.download_button(
                label="Download GPX only",
                data=gpx_path.read_bytes(),
                file_name=p_gpx.name,
                mime="application/gpx+xml",
            )
            st.download_button(
                label="Download KML only",
                data=kml_path.read_bytes(),
                file_name=p_kml.name,
                mime="application/vnd.google-earth.kml+xml",
            )
        else:
            st.caption("Save at least one waterfall to enable export.")

        st.divider()
        with st.expander("Paths"):
            st.code(str(WATERFALLS_PATH))
            st.code(str(ROADS_PATH))
            st.code(str(USER_PATH))


if __name__ == "__main__":
    main()
