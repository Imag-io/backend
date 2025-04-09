from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os, uuid, threading
from ..services import files, tiler

bp = Blueprint("upload", __name__, url_prefix="/api")

@bp.post("/upload")
def upload():
    """Handle file upload and kick off tiling in a background thread."""
    if "file" not in request.files:
        return jsonify(error="No file part"), 400

    f = request.files["file"]
    if f.filename == "" or not files.allowed_file(f.filename):
        return jsonify(error="Invalid or empty file"), 400

    image_id = str(uuid.uuid4())
    image_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], image_id)
    os.makedirs(image_dir, exist_ok=True)

    filename  = secure_filename(f.filename)
    file_path = os.path.join(image_dir, filename)
    f.save(file_path)

    # async/await in Express. To change later (i think is Celery)
    threading.Thread(target=tiler.process_image,
                     args=(image_id, file_path)).start()

    return jsonify(status="success",
                   image_id=image_id,
                   filename=filename)
