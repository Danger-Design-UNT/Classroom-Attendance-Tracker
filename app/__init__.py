from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# Import blueprints
# from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.attendance import attendance_bp

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    # app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)

    return app
