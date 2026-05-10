from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User

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
def chat():
    return render_template('chat.html', connections=[])

@app.route('/profile')
def profile():
    return render_template('profile.html')

# ── Create tables on first run ────────────────────────────────────
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
