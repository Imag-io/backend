from .upload import bp as upload_bp
from .tiles  import bp as tiles_bp
from .status import bp as status_bp
from .processing import bp as proc_bp
from .history import bp as hist_bp

def register_blueprints(app):
    app.register_blueprint(upload_bp)
    app.register_blueprint(tiles_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(proc_bp)
    app.register_blueprint(hist_bp)
