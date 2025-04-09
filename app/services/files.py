from __future__ import annotations
import os, time
from typing import Dict, List, Any
from ..config import BaseConfig

# Runtime store
image_metadata: Dict[str, Dict[str, Any]] = {}


# upload and tiles folder REQUIRED
def ensure_folders() -> None:
    os.makedirs(BaseConfig.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(BaseConfig.TILES_FOLDER,  exist_ok=True)


# File extension validation
def allowed_file(filename: str) -> bool:
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in BaseConfig.ALLOWED_EXT


# History builders (used in /history routes)
def build_history(root_id: str | None = None) -> List[Dict[str, Any]]:
    if root_id is None:
        items = [_slim(m, i) for i, m in image_metadata.items()
                 if "error" not in m]
        return sorted(items, key=lambda x: x["timestamp"], reverse=True)

    if root_id not in image_metadata:
        raise KeyError("Image not found")

    lineage = [_slim(image_metadata[root_id], root_id) | {"operation": "original"}]
    for i, m in image_metadata.items():
        if m.get("parent_id") == root_id:
            lineage.append(_slim(m, i))
    return sorted(lineage, key=lambda x: x["timestamp"])


def _slim(meta: Dict[str, Any], image_id: str) -> Dict[str, Any]:
    return {
        "image_id": image_id,
        "timestamp": meta.get("timestamp"),
        "width": meta.get("width"),
        "height": meta.get("height"),
        "operation": meta.get("operation"),
        "parent_id": meta.get("parent_id"),
        "tiling_complete": meta.get("tiling_complete", False),
        "params": meta.get("params"),
    }