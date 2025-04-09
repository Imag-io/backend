from __future__ import annotations
import os, time, math, numpy as np, cv2
from osgeo import gdal
from ..config import BaseConfig
from ..extensions import logger
from . import files


# API
def process_image(image_id: str, file_path: str) -> None:
    # Create the tile pyramid for the file_path and update metadata
    # Run in background ( ASYNC???? CELERY????)
    try:
        logger.info("Processing image %s", file_path)
        tiles_dir = os.path.join(BaseConfig.TILES_FOLDER, image_id)
        os.makedirs(tiles_dir, exist_ok=True)

        # GDAL first (GeoTIFFs, huge rasters, TODO: is it necessary for the images i wil get????)
        try:
            ds = gdal.Open(file_path)
            w, h = ds.RasterXSize, ds.RasterYSize
            _store_meta(image_id, file_path, w, h)
            _create_tiles_gdal(ds, tiles_dir, w, h)
        except Exception as gdal_err:
            logger.warning("GDAL failed → OpenCV: %s", gdal_err)
            img = cv2.imread(file_path)
            h, w = img.shape[:2]
            _store_meta(image_id, file_path, w, h)
            _create_tiles_cv2(img, tiles_dir, w, h)

        files.image_metadata[image_id]["tiling_complete"] = True
        logger.info("Tiling complete for %s", image_id)

    except Exception as exc:
        logger.error("Tiling error: %s", exc, exc_info=True)
        files.image_metadata[image_id] = {"error": str(exc),
                                          "timestamp": time.time()}


# Helper (inside GDAL and openCV try/catch)
def _store_meta(img_id, path, w, h):
    files.image_metadata[img_id] = {
        "width": w, "height": h, "file_path": path,
        "tiling_complete": False, "timestamp": time.time()
    }


def _native_zoom(w, h) -> int:
    return math.ceil(math.log2(max(w, h) / BaseConfig.TILE_SIZE))


# Create tiles
def _create_tiles_gdal(ds, out_dir, w, h):
    max_native = _native_zoom(w, h)

    for z in range(BaseConfig.MIN_ZOOM,
                   min(max_native, BaseConfig.MAX_ZOOM) + 1):
        z_dir = os.path.join(out_dir, str(z))
        os.makedirs(z_dir, exist_ok=True)

        scale = 2 ** (max_native - z)
        tx = math.ceil(w / (BaseConfig.TILE_SIZE * scale))
        ty = math.ceil(h / (BaseConfig.TILE_SIZE * scale))
        logger.info("GDAL tiles zoom %d → %dx%d", z, tx, ty)

        for x in range(tx):
            x_dir = os.path.join(z_dir, str(x))
            os.makedirs(x_dir, exist_ok=True)
            for y in range(ty):
                dst = os.path.join(x_dir, f"{y}.png")

                sx = x * BaseConfig.TILE_SIZE * scale
                sy = y * BaseConfig.TILE_SIZE * scale
                sw = min(BaseConfig.TILE_SIZE * scale, w - sx)
                sh = min(BaseConfig.TILE_SIZE * scale, h - sy)
                if sw <= 0 or sh <= 0:
                    continue

                gdal.Translate(dst, ds,
                               srcWin=[sx, sy, sw, sh],
                               width=BaseConfig.TILE_SIZE,
                               height=BaseConfig.TILE_SIZE,
                               format="PNG",
                               options=["-of", "PNG"])


# Fallback (gdal)
def _create_tiles_cv2(img, out_dir, w, h):
    max_native = _native_zoom(w, h)

    for z in range(BaseConfig.MIN_ZOOM,
                   min(max_native, BaseConfig.MAX_ZOOM) + 1):
        z_dir = os.path.join(out_dir, str(z))
        os.makedirs(z_dir, exist_ok=True)

        scale = 2 ** (max_native - z)
        scaled = cv2.resize(img,
                            (int(w / scale), int(h / scale)),
                            interpolation=cv2.INTER_AREA) if scale > 1 else img
        sh, sw = scaled.shape[:2]
        tx = math.ceil(sw / BaseConfig.TILE_SIZE)
        ty = math.ceil(sh / BaseConfig.TILE_SIZE)
        logger.info("OpenCV tiles zoom %d → %dx%d", z, tx, ty)

        for x in range(tx):
            x_dir = os.path.join(z_dir, str(x))
            os.makedirs(x_dir, exist_ok=True)
            for y in range(ty):
                x0, y0 = x * BaseConfig.TILE_SIZE, y * BaseConfig.TILE_SIZE
                x1, y1 = min(x0 + BaseConfig.TILE_SIZE, sw), \
                         min(y0 + BaseConfig.TILE_SIZE, sh)
                tile = scaled[y0:y1, x0:x1]

                if tile.shape[:2] != (BaseConfig.TILE_SIZE, BaseConfig.TILE_SIZE):
                    pad = np.zeros((BaseConfig.TILE_SIZE,
                                    BaseConfig.TILE_SIZE, 3), np.uint8)
                    pad[:tile.shape[0], :tile.shape[1]] = tile
                    tile = pad

                cv2.imwrite(os.path.join(x_dir, f"{y}.png"), tile)