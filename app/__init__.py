from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
limiter = Limiter(key_func=get_remote_address)

def create_app():
    load_dotenv()

    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, '..', 'instance', 'attendance.db')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback_key')

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"


    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        REMEMBER_COOKIE_HTTPONLY=True,
        SESSION_PROTECTION='strong'
    )

    db.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    from .models import User

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import auth_bp
    from .routes.attendance import attendance_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)

    from .routes.r4 import r4_bp
    app.register_blueprint(r4_bp)


    @app.before_request
    def enforce_https():
        if not app.debug and not request.is_secure:
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    return app
