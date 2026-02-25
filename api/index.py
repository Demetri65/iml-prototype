from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

from api.mapillary_client import MapillaryAPIError, download_image_bytes, fetch_images_in_bbox
from api.mapillary_config import (
    DEFAULT_INGEST_LIMIT,
    MAPILLARY_IMAGE_DIR,
    MAX_INGEST_LIMIT,
    THUMBNAIL_FIELD,
)
from api.mapillary_store import (
    ensure_store_dirs,
    load_index,
    save_index,
    snapshot_exists,
    snapshot_filename,
    store_snapshot,
    upsert_metadata,
)

load_dotenv()


class BBox(BaseModel):
    west: float
    south: float
    east: float
    north: float

    @model_validator(mode="after")
    def validate_order(self):
        if self.west >= self.east:
            raise ValueError("west must be less than east")
        if self.south >= self.north:
            raise ValueError("south must be less than north")

        width = self.east - self.west
        height = self.north - self.south
        area = width * height
        if area > 0.01:
            raise ValueError("bbox area must be <= 0.01 square degrees for Mapillary API")
        return self


class IngestRequest(BaseModel):
    bbox: BBox
    limit: int = Field(default=DEFAULT_INGEST_LIMIT, ge=1, le=MAX_INGEST_LIMIT)
    image_type: Literal["all", "flat", "pano"] = "all"


def _extract_coordinates(image_payload: dict) -> tuple[float | None, float | None]:
    geometry = image_payload.get("computed_geometry")
    if not isinstance(geometry, dict):
        return None, None

    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        return None, None

    try:
        lng = float(coordinates[0])
        lat = float(coordinates[1])
    except (TypeError, ValueError):
        return None, None

    return lng, lat


ensure_store_dirs()
app = FastAPI()
app.mount("/api/mapillary/files", StaticFiles(directory=str(MAPILLARY_IMAGE_DIR)), name="mapillary-files")


@app.get("/")
def root():
    return {"message": "Backend is running."}


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/mapillary/ingest")
def ingest_snapshots(payload: IngestRequest):
    token = os.getenv("MAPILLARY_ACCESS_TOKEN")
    if not token:
        raise HTTPException(
            status_code=400,
            detail="MAPILLARY_ACCESS_TOKEN is not set. Configure it before ingesting.",
        )

    try:
        images = fetch_images_in_bbox(
            token=token,
            bbox=payload.bbox.model_dump(),
            limit=payload.limit,
            image_type=payload.image_type,
        )
    except MapillaryAPIError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Mapillary API request failed (status={exc.status_code}): {exc.detail}",
        ) from exc

    index = load_index()
    ingested = 0
    skipped_existing = 0
    failed = 0

    for image in images:
        image_id = str(image.get("id", "")).strip()
        thumb_url = image.get(THUMBNAIL_FIELD)

        if not image_id or not isinstance(thumb_url, str) or not thumb_url:
            failed += 1
            continue

        filename = snapshot_filename(image_id)
        if snapshot_exists(image_id):
            skipped_existing += 1
        else:
            try:
                image_bytes = download_image_bytes(thumb_url)
                filename = store_snapshot(image_id=image_id, image_bytes=image_bytes)
            except (MapillaryAPIError, OSError):
                failed += 1
                continue
            ingested += 1

        lng, lat = _extract_coordinates(image)
        captured_at = image.get("captured_at") if isinstance(image.get("captured_at"), str) else None
        camera_type = image.get("camera_type")
        if camera_type is not None:
            camera_type = str(camera_type)

        upsert_metadata(
            {
                "id": image_id,
                "captured_at": captured_at,
                "lng": lng,
                "lat": lat,
                "camera_type": camera_type,
                "thumb_url_source": thumb_url,
                "stored_filename": filename,
                "stored_url": f"/api/mapillary/files/{filename}",
            },
            index=index,
        )

    save_index(index)
    return {
        "query": {
            "bbox": payload.bbox.model_dump(),
            "limit": payload.limit,
            "image_type": payload.image_type,
        },
        "fetched": len(images),
        "ingested": ingested,
        "skipped_existing": skipped_existing,
        "failed": failed,
    }


@app.get("/api/mapillary/snapshots")
def list_snapshots(
    limit: int = Query(default=60, ge=1, le=MAX_INGEST_LIMIT),
    offset: int = Query(default=0, ge=0),
):
    index = load_index()
    items_payload = index.get("items", {})
    if not isinstance(items_payload, dict):
        items_payload = {}

    items = [item for item in items_payload.values() if isinstance(item, dict)]
    items.sort(key=lambda item: str(item.get("ingested_at", "")), reverse=True)
    return {
        "total": len(items),
        "items": items[offset : offset + limit],
    }


@app.get("/api/mapillary/snapshots/{image_id}")
def get_snapshot(image_id: str):
    index = load_index()
    items_payload = index.get("items", {})
    if not isinstance(items_payload, dict):
        items_payload = {}

    item = items_payload.get(image_id)
    if not isinstance(item, dict):
        raise HTTPException(status_code=404, detail=f"Snapshot {image_id} not found.")
    return item
