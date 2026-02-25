from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from api.mapillary_config import MAPILLARY_IMAGE_DIR, MAPILLARY_INDEX_PATH

INDEX_VERSION = 1


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _empty_index() -> dict[str, Any]:
    return {
        "version": INDEX_VERSION,
        "updated_at": _utc_now_iso(),
        "items": {},
    }


def ensure_store_dirs() -> None:
    MAPILLARY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not MAPILLARY_INDEX_PATH.exists():
        MAPILLARY_INDEX_PATH.write_text(
            json.dumps(_empty_index(), indent=2),
            encoding="utf-8",
        )


def load_index() -> dict[str, Any]:
    ensure_store_dirs()
    try:
        payload = json.loads(MAPILLARY_INDEX_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        payload = _empty_index()

    if not isinstance(payload, dict):
        payload = _empty_index()

    items = payload.get("items")
    if not isinstance(items, dict):
        payload["items"] = {}

    payload["version"] = INDEX_VERSION
    if not isinstance(payload.get("updated_at"), str):
        payload["updated_at"] = _utc_now_iso()
    return payload


def save_index(index: dict[str, Any]) -> None:
    ensure_store_dirs()
    index["version"] = INDEX_VERSION
    index["updated_at"] = _utc_now_iso()
    if not isinstance(index.get("items"), dict):
        index["items"] = {}

    MAPILLARY_INDEX_PATH.write_text(
        json.dumps(index, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def snapshot_filename(image_id: str) -> str:
    safe_image_id = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_"
        for char in str(image_id)
    )
    return f"{safe_image_id}_1024.jpg"


def snapshot_exists(image_id: str) -> bool:
    return (MAPILLARY_IMAGE_DIR / snapshot_filename(image_id)).exists()


def store_snapshot(image_id: str, image_bytes: bytes) -> str:
    filename = snapshot_filename(image_id)
    (MAPILLARY_IMAGE_DIR / filename).write_bytes(image_bytes)
    return filename


def upsert_metadata(record: dict[str, Any], index: dict[str, Any] | None = None) -> dict[str, Any]:
    owns_index = index is None
    if owns_index:
        index = load_index()

    assert index is not None
    items = index.setdefault("items", {})
    if not isinstance(items, dict):
        index["items"] = {}
        items = index["items"]

    normalized = dict(record)
    normalized["id"] = str(normalized["id"])
    normalized["ingested_at"] = _utc_now_iso()
    items[normalized["id"]] = normalized

    if owns_index:
        save_index(index)
    return normalized
