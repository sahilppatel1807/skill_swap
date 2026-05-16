from flask import request
from flask_login import LoginManager, current_user
from sqlalchemy import inspect, text
from __init__ import create_app, db
from models import User, Request

app = create_app()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@app.before_request
def debug():
    print("➡️", request.method, request.path)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_nav_pending_requests():
    if current_user.is_authenticated:
        incoming_pending_unseen = Request.query.filter(
            Request.to_user_id == current_user.id,
            Request.status == 'pending',
            Request.to_user_seen.is_(False),
        ).count()
        outgoing_response_unseen = Request.query.filter(
            Request.from_user_id == current_user.id,
            Request.status != 'pending',
            Request.from_user_seen.is_(False),
        ).count()
        return {'nav_requests_unseen_count': incoming_pending_unseen + outgoing_response_unseen}
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


with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    user_columns = [column['name'] for column in inspector.get_columns('users')]
    if 'avatar_initials' not in user_columns:
        db.session.execute(text('ALTER TABLE users ADD COLUMN avatar_initials VARCHAR(2)'))
        db.session.commit()
    if 'nickname' not in user_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(80)"))
        db.session.commit()
    request_columns = [column['name'] for column in inspector.get_columns('requests')]
    if 'last_login' not in user_columns:
        db.session.execute(text('ALTER TABLE users ADD COLUMN last_login DATETIME'))
        db.session.commit()
    skills_columns = [column['name'] for column in inspector.get_columns('skills')]
    if 'updated_at' not in skills_columns:
        db.session.execute(text('ALTER TABLE skills ADD COLUMN updated_at DATETIME'))
        db.session.commit()
    if 'to_user_seen' not in request_columns:
        db.session.execute(text('ALTER TABLE requests ADD COLUMN to_user_seen INTEGER NOT NULL DEFAULT 0'))
        db.session.commit()
    if 'from_user_seen' not in request_columns:
        db.session.execute(text('ALTER TABLE requests ADD COLUMN from_user_seen INTEGER NOT NULL DEFAULT 1'))
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
