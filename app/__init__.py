from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')
    app.config.from_pyfile('config.py', silent=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)


    from .routes.auth import auth_bp
    from .routes.attendance import attendance_bp
 
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)

    return app

