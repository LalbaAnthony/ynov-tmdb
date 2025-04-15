# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Load configuration (from a config file or environment variables)
    app.config.from_pyfile('../config.py', silent=True)  # optional, or configure directly

    # Register Blueprints (we’ll create a blueprint in routes.py)
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Optionally add any global jinja2 functions
    app.jinja_env.globals.update({'max': max, 'min': min})
    
    return app
