from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=[])
login_manager = LoginManager()


def create_app(config_class=None):
    if config_class is None:
        from config import Config
        config_class = Config

    app = Flask(__name__)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.from_object(config_class)

    if not app.config.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable is not set.")

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = None

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_nav_pending_requests():
        from flask_login import current_user
        from models import Request
        if current_user.is_authenticated:
            incoming = Request.query.filter(
                Request.to_user_id == current_user.id,
                Request.status == 'pending',
                Request.to_user_seen.is_(False),
            ).count()
            outgoing = Request.query.filter(
                Request.from_user_id == current_user.id,
                Request.status != 'pending',
                Request.from_user_seen.is_(False),
            ).count()
            return {'nav_requests_unseen_count': incoming + outgoing}
        return {'nav_requests_unseen_count': 0}

    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.skills import skills_bp
    from routes.requests import requests_bp
    from routes.profile import profile_bp
    from routes.chat import chat_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(chat_bp)

    return app
