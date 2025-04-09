from flask import Blueprint, jsonify
from ..services import files

bp = Blueprint("status", __name__, url_prefix="/api")

@bp.get("/status/<image_id>")
def status(image_id):
    meta = files.image_metadata.get(image_id)
    if not meta:
        return jsonify(status="not_found"), 404

    return jsonify(
        status="complete" if meta.get("tiling_complete") else "processing",
        width = meta.get("width"),
        height= meta.get("height"),
        timestamp = meta.get("timestamp"),
    )
