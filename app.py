import os
from flask import request
from sqlalchemy import inspect, text
from __init__ import create_app, db
from models import User, Request

app = create_app()


@app.before_request
def debug():
    print("➡️", request.method, request.path)


with app.app_context():
    db.create_all()
    inspector = inspect(db.engine)
    user_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'avatar_initials' not in user_columns:
        db.session.execute(text('ALTER TABLE users ADD COLUMN avatar_initials VARCHAR(2)'))
        db.session.commit()
    if 'nickname' not in user_columns:
        db.session.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(80)"))
        db.session.commit()
    if 'last_login' not in user_columns:
        db.session.execute(text('ALTER TABLE users ADD COLUMN last_login DATETIME'))
        db.session.commit()
    request_columns = [col['name'] for col in inspector.get_columns('requests')]
    skills_columns = [col['name'] for col in inspector.get_columns('skills')]
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
