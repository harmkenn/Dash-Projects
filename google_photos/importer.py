import json
import zipfile
from pathlib import Path
from typing import Any


MAX_SIDECAR_BYTES = 4 * 1024 * 1024
METADATA_KEYS = {
    "creationTime",
    "description",
    "geoData",
    "geoDataExif",
    "googlePhotosOrigin",
    "photoTakenTime",
    "title",
    "url",
}


def _value(container: Any, key: str, nested_key: str = "formatted") -> str:
    if not isinstance(container, dict):
        return ""
    value = container.get(key)
    if isinstance(value, dict):
        value = value.get(nested_key, "")
    if value is None:
        return ""
    return str(value)


def _location(container: Any, key: str) -> tuple[str, str, str]:
    location = container.get(key, {}) if isinstance(container, dict) else {}
    if not isinstance(location, dict):
        return "", "", ""
    return (
        str(location.get("latitude", "")),
        str(location.get("longitude", "")),
        str(location.get("altitude", "")),
    )


def _media_filename(sidecar_name: str) -> str:
    suffix = ".supplemental-metadata.json"
    if sidecar_name.lower().endswith(suffix):
        return sidecar_name[: -len(suffix)]
    if sidecar_name.lower().endswith(".json"):
        return sidecar_name[:-5]
    return ""


def _record(metadata: dict[str, Any], source_file: str) -> dict[str, str] | None:
    if not METADATA_KEYS.intersection(metadata):
        return None

    geo_latitude, geo_longitude, geo_altitude = _location(metadata, "geoData")
    exif_latitude, exif_longitude, exif_altitude = _location(metadata, "geoDataExif")
    origin = metadata.get("googlePhotosOrigin", {})
    if not isinstance(origin, dict):
        origin = {}
    mobile_upload = origin.get("mobileUpload", {})
    if not isinstance(mobile_upload, dict):
        mobile_upload = {}

    return {
        "source_file": source_file,
        "media_filename": _media_filename(Path(source_file).name),
        "title": _value(metadata, "title", ""),
        "description": _value(metadata, "description", ""),
        "creation_time": _value(metadata, "creationTime", "formatted"),
        "creation_timestamp": _value(metadata, "creationTime", "timestamp"),
        "photo_taken_time": _value(metadata, "photoTakenTime", "formatted"),
        "photo_taken_timestamp": _value(metadata, "photoTakenTime", "timestamp"),
        "latitude": geo_latitude,
        "longitude": geo_longitude,
        "altitude": geo_altitude,
        "latitude_exif": exif_latitude,
        "longitude_exif": exif_longitude,
        "altitude_exif": exif_altitude,
        "url": _value(metadata, "url", ""),
        "image_views": _value(metadata, "imageViews", ""),
        "device_type": str(mobile_upload.get("deviceType", "")),
        "device_folder": str(mobile_upload.get("deviceFolder", "")),
        "camera_make": _value(metadata, "cameraMake", ""),
        "camera_model": _value(metadata, "cameraModel", ""),
        "raw_metadata_json": json.dumps(metadata, ensure_ascii=False, separators=(",", ":")),
    }


def _parse_sidecar(data: bytes, source_file: str) -> dict[str, str] | None:
    metadata = json.loads(data.decode("utf-8-sig"))
    if not isinstance(metadata, dict):
        return None
    return _record(metadata, source_file)


def scan_source(source: str) -> dict[str, Any]:
    """Read Google Photos JSON sidecars from a Takeout folder or ZIP archive."""
    path = Path(source).expanduser().resolve(strict=True)
    records: list[dict[str, str]] = []
    errors: list[str] = []
    ignored = 0

    def consume(data: bytes, name: str) -> None:
        nonlocal ignored
        try:
            record = _parse_sidecar(data, name)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            errors.append(f"{name}: {error}")
            return
        if record is None:
            ignored += 1
        else:
            records.append(record)

    if path.is_dir():
        for item in path.rglob("*.json"):
            if item.is_symlink() or not item.is_file():
                continue
            relative_name = item.relative_to(path).as_posix()
            if item.stat().st_size > MAX_SIDECAR_BYTES:
                errors.append(f"{relative_name}: sidecar exceeds 4 MiB and was skipped")
                continue
            consume(item.read_bytes(), relative_name)
    elif path.is_file() and zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for item in archive.infolist():
                if item.is_dir() or not item.filename.lower().endswith(".json"):
                    continue
                if item.file_size > MAX_SIDECAR_BYTES:
                    errors.append(f"{item.filename}: sidecar exceeds 4 MiB and was skipped")
                    continue
                with archive.open(item) as sidecar:
                    data = sidecar.read(MAX_SIDECAR_BYTES + 1)
                if len(data) > MAX_SIDECAR_BYTES:
                    errors.append(f"{item.filename}: sidecar exceeds 4 MiB and was skipped")
                    continue
                consume(data, item.filename)
    else:
        raise ValueError("Choose an extracted Takeout folder or a ZIP archive.")

    return {"records": records, "errors": errors, "ignored": ignored}