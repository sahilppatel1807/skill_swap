from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# db is initialised here and bound to the app in app.py via db.init_app(app)
# DO NOT do "from app import db" — that causes a circular import
db = SQLAlchemy()


# ── User ─────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.String(256), nullable=False)
    course     = db.Column(db.String(150))
    bio        = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f'<User {self.email}>'


# ── Skill ─────────────────────────────────────────────────────────
class Skill(db.Model):
    __tablename__ = 'skills'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    category    = db.Column(db.String(50),  nullable=False)
    level       = db.Column(db.String(20))
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    owner    = db.relationship('User', backref='skills', lazy=True)
    requests = db.relationship('Request', backref='skill', lazy=True,
                               cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id':          self.id,
            'name':        self.name,
            'category':    self.category,
            'level':       self.level,
            'description': self.description
        }


# ── Swap Request ──────────────────────────────────────────────────
class Request(db.Model):
    __tablename__ = 'requests'

    id           = db.Column(db.Integer, primary_key=True)
    skill_id     = db.Column(db.Integer, db.ForeignKey('skills.id'),  nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    to_user_id   = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    message      = db.Column(db.Text)
    status       = db.Column(db.String(20), default='pending')  # pending/accepted/rejected
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    from_user = db.relationship('User', foreign_keys=[from_user_id],
                                backref='sent_requests')
    to_user   = db.relationship('User', foreign_keys=[to_user_id],
                                backref='received_requests')

# ── Message ───────────────────────────────────────────────────────
class Message(db.Model):
    __tablename__ = 'messages'

    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body        = db.Column(db.Text, nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)

    sender   = db.relationship('User', foreign_keys=[sender_id],   backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
