from pathlib import Path

GRAPH_BASE_URL = "https://graph.mapillary.com"
DEFAULT_INGEST_LIMIT = 100
MAX_INGEST_LIMIT = 500
REQUEST_TIMEOUT_SECONDS = 15
THUMBNAIL_FIELD = "thumb_1024_url"
IMAGE_FIELDS = [
    "id",
    "captured_at",
    "camera_type",
    "computed_geometry",
    THUMBNAIL_FIELD,
]

MODULE_DIR = Path(__file__).resolve().parent
MAPILLARY_DATA_DIR = MODULE_DIR / "data" / "mapillary"
MAPILLARY_IMAGE_DIR = MAPILLARY_DATA_DIR / "images"
MAPILLARY_INDEX_PATH = MAPILLARY_DATA_DIR / "index.json"
