from flask import Flask, redirect, request, url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()

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
    migrate.init_app(app, db)
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

    @app.route('/')
    def landing():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role == 'student':
            return redirect(url_for('attendance.student_dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('attendance.teacher_dashboard'))
        else:
            return redirect(url_for('auth.login'))

    @app.before_request
    def enforce_https():
        if not app.debug and not request.is_secure:
            url = request.url.replace("http://", "https://", 1)
            return redirect(url, code=301)

    return app
