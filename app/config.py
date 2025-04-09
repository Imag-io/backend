import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "storage", "uploads")
    TILES_FOLDER  = os.path.join(BASE_DIR, "storage", "tiles")
    ALLOWED_EXT   = {"tif", "tiff", "jpg", "jpeg", "png"}
    TILE_SIZE     = 256
    MIN_ZOOM      = 0
    MAX_ZOOM      = 18

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False
