# /app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import ALLOWED_ORIGINS


# Initialize SQLAlchemy with no settings
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object('config')

    CORS(app, origins=[ALLOWED_ORIGINS])

    # Initialize SQLAlchemy
    db.init_app(app)

    # Blueprint registration
    from app.routes.main_routes import main
    app.register_blueprint(main)

    from app.routes.api_routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app
