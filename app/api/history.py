from flask import Blueprint, jsonify
from ..services import files

bp = Blueprint("history", __name__, url_prefix="/api")

@bp.get("/history")
def history():
    return jsonify(files.build_history())

@bp.get("/history/<image_id>")
def history_single(image_id):
    if image_id not in files.image_metadata:
        return jsonify(error="Image not found"), 404
    return jsonify(files.build_history(image_id))
