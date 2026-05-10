from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User
from models import db, User, Request, Message

app = Flask(__name__)
app.config.from_object(Config)

# ── Extensions ────────────────────────────────────────────────────
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Blueprints ────────────────────────────────────────────────────
from auth import auth_bp
from routes.skills import skills_bp

app.register_blueprint(auth_bp)
app.register_blueprint(skills_bp)

# ── Home ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── Placeholder routes (until teammates complete their modules) ───
@app.route('/requests')
def requests():
    return render_template('requests.html')

@app.route('/chat')
@login_required
def chat():
    accepted = Request.query.filter(
        ((Request.from_user_id == current_user.id) |
         (Request.to_user_id   == current_user.id)),
        Request.status == 'accepted'
    ).all()

    connections = []
    seen = set()
    for req in accepted:
        other = req.from_user if req.to_user_id == current_user.id else req.to_user
        if other.id not in seen:
            seen.add(other.id)
            connections.append(other)

    return render_template('chat.html', connections=connections)

@app.route('/profile')
def profile():
    return render_template('profile.html')

# ── Create tables on first run ────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
