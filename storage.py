"""Local JSON persistence under data/."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

WATERFALLS_PATH = DATA / "osm_waterfalls.json"
ROADS_PATH = DATA / "osm_roads.json"
USER_PATH = DATA / "user_state.json"


def ensure_data_dir() -> None:
    DATA.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    ensure_data_dir()
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    tmp.replace(path)


def load_user_state() -> dict[str, list[str]]:
    raw = load_json(USER_PATH, {})
    return {
        "saved_ids": list(raw.get("saved_ids", [])),
        "ignored_ids": list(raw.get("ignored_ids", [])),
    }


def save_user_state(state: dict[str, list[str]]) -> None:
    save_json(USER_PATH, state)
