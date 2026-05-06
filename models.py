from datetime import datetime
from app import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    category    = db.Column(db.String(50),  nullable=False)
    level       = db.Column(db.String(20))   # Beginner / Intermediate / Expert
    description = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # lets you write skill.owner.username in templates
    owner    = db.relationship('User', backref='skills', lazy=True)
    requests = db.relationship('Request', backref='skill', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name,
            'category': self.category, 'level': self.level,
            'description': self.description
        }


class Request(db.Model):
    __tablename__ = 'requests'

    id          = db.Column(db.Integer, primary_key=True)
    skill_id    = db.Column(db.Integer, db.ForeignKey('skills.id'),  nullable=False)
    from_user_id= db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    to_user_id  = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    message     = db.Column(db.Text)
    status      = db.Column(db.String(20), default='pending')  # pending/accepted/rejected
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    from_user = db.relationship('User', foreign_keys=[from_user_id], backref='sent_requests')
    to_user   = db.relationship('User', foreign_keys=[to_user_id],   backref='received_requests')