from flask_cors import CORS
import logging

cors   = CORS()
logger = logging.getLogger("app")
logging.basicConfig(level=logging.INFO)
