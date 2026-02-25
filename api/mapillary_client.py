import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from api.mapillary_config import (
    GRAPH_BASE_URL,
    IMAGE_FIELDS,
    REQUEST_TIMEOUT_SECONDS,
)


class MapillaryAPIError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def _read_response_bytes(url: str, accept: str) -> bytes:
    request = Request(url, headers={"Accept": accept})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.read()
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        detail = body or str(exc.reason)
        raise MapillaryAPIError(status_code=exc.code, detail=detail) from exc
    except URLError as exc:
        raise MapillaryAPIError(status_code=0, detail=str(exc.reason)) from exc


def _read_json(url: str) -> dict:
    response_bytes = _read_response_bytes(url=url, accept="application/json")
    try:
        payload = json.loads(response_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MapillaryAPIError(status_code=0, detail=f"Invalid JSON response: {exc}") from exc

    if not isinstance(payload, dict):
        raise MapillaryAPIError(status_code=0, detail="Unexpected Mapillary response shape.")
    return payload


def fetch_images_in_bbox(
    token: str,
    bbox: dict[str, float],
    limit: int,
    image_type: str,
) -> list[dict]:
    params = {
        "access_token": token,
        "bbox": f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}",
        "fields": ",".join(IMAGE_FIELDS),
        "limit": str(limit),
    }
    if image_type != "all":
        params["image_type"] = image_type

    next_url = f"{GRAPH_BASE_URL}/images?{urlencode(params)}"
    images: list[dict] = []

    while next_url and len(images) < limit:
        payload = _read_json(next_url)
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise MapillaryAPIError(status_code=0, detail="Unexpected Mapillary data payload.")

        for item in data:
            if len(images) >= limit:
                break
            if isinstance(item, dict):
                images.append(item)

        paging = payload.get("paging", {})
        if not isinstance(paging, dict):
            break

        candidate_next = paging.get("next")
        if not isinstance(candidate_next, str) or not candidate_next:
            break
        next_url = candidate_next

    return images


def download_image_bytes(image_url: str) -> bytes:
    return _read_response_bytes(url=image_url, accept="image/*")
