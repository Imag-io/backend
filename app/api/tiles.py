from flask import Blueprint, send_file, jsonify, current_app
import os, io
from PIL import Image
from ..services import tiler, files

bp = Blueprint("tiles", __name__, url_prefix="/api")

@bp.get("/tiles/<image_id>/<int:z>/<int:x>/<int:y>.png")
def tile(image_id, z, x, y):
    tile_path = os.path.join(
        current_app.config["TILES_FOLDER"], image_id, str(z), str(x), f"{y}.png"
    )
    if os.path.exists(tile_path):
        return send_file(tile_path, mimetype="image/png")

    # Is it still processing? (Don't know :p )
    meta = files.image_metadata.get(image_id, {})
    if not meta.get("tiling_complete", True):
        return jsonify(status="processing"), 202

    # EMPTY TILE
    tile = Image.new("RGBA",
                     (current_app.config["TILE_SIZE"],)*2,
                     (0,0,0,0))
    buf = io.BytesIO(); tile.save(buf, "PNG"); buf.seek(0)
    return send_file(buf, mimetype="image/png")
