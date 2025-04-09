from flask import Flask
from .config import DevConfig
from .extensions import cors, logger
from .api import register_blueprints

def create_app(config_class=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

   
    cors.init_app(app)        
    logger.info("Flask app created with %s", config_class.__name__)

    # Routes
    register_blueprints(app)

    # ── error handlers (?) ───────────────────────────────────
    # from .errors import register_error_handlers
    # register_error_handlers(app)

    return app
