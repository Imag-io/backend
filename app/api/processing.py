from flask import Blueprint, request, jsonify
from ..services import operations, sandbox, files
import threading

bp = Blueprint("processing", __name__, url_prefix="/api")

# Image Processing (IMPORTANT !REMEMBER ME 09/05/2025)
@bp.post("/process")
def process_image():
    data = request.get_json(silent=True) or {}
    image_id  = data.get("image_id")
    operation = data.get("operation")
    params    = data.get("params", {})

    if not image_id or not operation:
        return jsonify(error="Missing required fields"), 400
    if image_id not in files.image_metadata:
        return jsonify(error="Image not found"), 404

    src_path = files.image_metadata[image_id]["file_path"]
    try:
        result_id, result_path = operations.run(image_id, src_path,
                                                operation, params)
        # Fill in background
        threading.Thread(target=operations.finish,
                         args=(result_id, result_path)).start()
        return jsonify(status="success", result_id=result_id)
    except Exception as e:
        return jsonify(error=str(e)), 500

# Route
@bp.post("/execute")
def execute_python():
    data = request.get_json(silent=True) or {}
    image_id = data.get("image_id"); code = data.get("code")
    if not image_id or not code:
        return jsonify(error="Missing required fields"), 400
    if image_id not in files.image_metadata:
        return jsonify(error="Image not found"), 404

    src_path = files.image_metadata[image_id]["file_path"]
    try:
        result_id, result_path = sandbox.run(image_id, src_path, code)
        threading.Thread(target=operations.finish,
                         args=(result_id, result_path)).start()
        return jsonify(status="success", result_id=result_id)
    except Exception as e:
        return jsonify(error=str(e)), 500
