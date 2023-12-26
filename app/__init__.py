# /app/__init__.py 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .config import ALLOWED_ORIGINS, FLASK_SECRET_KEY
from flask_migrate import Migrate
# Initialize SQLAlchemy with no settings
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object('app.config')
    app.secret_key = FLASK_SECRET_KEY
    CORS(app, origins=[ALLOWED_ORIGINS])

    # Initialize SQLAlchemy
    db.init_app(app)

    migrate = Migrate(app, db)
    # Blueprint registration
    from app.routes.main_routes import main
    app.register_blueprint(main)

    from app.routes.api_routes import api
    app.register_blueprint(api, url_prefix='/api')
    """
    app.register_blueprint(linkedin_blueprint, url_prefix="/login")
    """
    #print(app.url_map)

    return app
