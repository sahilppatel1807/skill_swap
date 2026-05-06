from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from config import Config
from models import db, User

app = Flask(__name__)
app.config.from_object(Config)

# ── Extensions ───────────────────────────────────────────────────
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'          # redirect here if @login_required fails
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Create tables on first run ────────────────────────────────────
with app.app_context():
    db.create_all()


# ── Home ─────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


# ── Auth ─────────────────────────────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('skills'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        course   = request.form.get('course', '').strip()
        bio      = request.form.get('bio', '').strip()

        # Validation
        if not name or not email or not password:
            return render_template('signup.html', error='Name, email and password are required.')

        if len(password) < 6:
            return render_template('signup.html', error='Password must be at least 6 characters.')

        if User.query.filter_by(email=email).first():
            return render_template('signup.html', error='An account with that email already exists.')

        user = User(name=name, email=email, course=course, bio=bio)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('skills'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('skills'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('skills'))

        return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ── Skills ───────────────────────────────────────────────────────
@app.route('/skills')
@login_required
def skills():
    return render_template('skills.html')


# ── Requests ─────────────────────────────────────────────────────
@app.route('/requests')
@login_required
def requests():
    return render_template('requests.html')


# ── Chat ─────────────────────────────────────────────────────────
# Dummy data — replace with DB queries when chat is built out
_connections = [
    {'id': 1, 'name': 'Sara Ali',  'avatar': 'SA'},
    {'id': 2, 'name': 'Jake Lee',  'avatar': 'JL'},
]
_messages_store = {
    1: [
        {'sender': 'Sara Ali', 'text': 'Hey! Thanks for accepting my request.'},
        {'sender': 'Sahil',    'text': 'No problem! When do you want to start learning Python?'},
        {'sender': 'Sara Ali', 'text': 'How about tomorrow at 3 PM?'},
        {'sender': 'Sahil',    'text': 'Sounds good! I\'ll send you some resources beforehand.'},
        {'sender': 'Sara Ali', 'text': 'Hey! Ready to start?'},
    ],
    2: [
        {'sender': 'Jake Lee', 'text': 'Thanks for accepting!'},
        {'sender': 'Sahil',    'text': 'Of course! What skill did you want to learn?'},
    ]
}

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', connections=_connections)

@app.route('/chat/messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    msgs = _messages_store.get(user_id, [])
    formatted = [
        {
            'type': 'sent' if m['sender'] == current_user.name else 'received',
            'text': m['text']
        }
        for m in msgs
    ]
    return jsonify({'messages': formatted})

@app.route('/chat/send', methods=['POST'])
@login_required
def send_message():
    data    = request.get_json()
    user_id = data.get('user_id')
    text    = data.get('message', '').strip()

    if not text or not user_id:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    _messages_store.setdefault(user_id, []).append({
        'sender': current_user.name,
        'text':   text
    })
    return jsonify({'status': 'ok'})


# ── Profile ───────────────────────────────────────────────────────
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/profile/skills/add', methods=['POST'])
@login_required
def add_skill():
    return jsonify({'status': 'ok'})

@app.route('/profile/skills/edit/<int:skill_id>', methods=['POST'])
@login_required
def edit_skill(skill_id):
    return jsonify({'status': 'ok'})

@app.route('/profile/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True)
