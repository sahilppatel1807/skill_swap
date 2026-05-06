from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db            = SQLAlchemy()
login_manager = LoginManager()
bcrypt        = Bcrypt()
migrate       = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']                     = 'skillswap-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///skillswap.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    # ── Dummy Data ───────────────────────────────────────────────
    CURRENT_USER = 'Sahil'

    connections = [
        { 'id': 1, 'name': 'Sara Ali', 'avatar': 'SA' },
        { 'id': 2, 'name': 'Jake Lee', 'avatar': 'JL' },
    ]

    messages_store = {
        1: [
            { 'sender': 'Sara Ali', 'text': 'Hey! Thanks for accepting my request.' },
            { 'sender': 'Sahil',    'text': 'No problem! When do you want to start learning Python?' },
            { 'sender': 'Sara Ali', 'text': 'How about tomorrow at 3 PM?' },
            { 'sender': 'Sahil',    'text': 'Sounds good! I\'ll send you some resources beforehand.' },
            { 'sender': 'Sara Ali', 'text': 'Hey! Ready to start?' },
        ],
        2: [
            { 'sender': 'Jake Lee', 'text': 'Thanks for accepting!' },
            { 'sender': 'Sahil',    'text': 'Of course! What skill did you want to learn?' },
        ]
    }

    users = []

    # ── Register your skills blueprint ──────────────────────────
    from routes.skills import skills_bp
    app.register_blueprint(skills_bp)

    # ── Existing Routes ──────────────────────────────────────────
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/requests')
    def requests():
        return render_template('requests.html')

    # ── Chat Routes ──────────────────────────────────────────────
    @app.route('/chat')
    def chat():
        return render_template('chat.html', connections=connections)

    @app.route('/chat/messages/<int:user_id>', methods=['GET'])
    def get_messages(user_id):
        msgs = messages_store.get(user_id, [])
        formatted = []
        for m in msgs:
            formatted.append({
                'type': 'sent' if m['sender'] == CURRENT_USER else 'received',
                'text': m['text']
            })
        return jsonify({ 'messages': formatted })

    @app.route('/chat/send', methods=['POST'])
    def send_message():
        data    = request.get_json()
        user_id = data.get('user_id')
        text    = data.get('message', '').strip()

        if not text or not user_id:
            return jsonify({ 'status': 'error', 'message': 'Missing data' }), 400

        if user_id not in messages_store:
            messages_store[user_id] = []
        messages_store[user_id].append({ 'sender': CURRENT_USER, 'text': text })
        return jsonify({ 'status': 'ok' })

    # ── Profile Routes ───────────────────────────────────────────
    @app.route('/profile')
    def profile():
        return render_template('profile.html')

    @app.route('/profile/skills/add', methods=['POST'])
    def add_skill():
        data = request.get_json()
        return jsonify({ 'status': 'ok' })

    @app.route('/profile/skills/edit/<int:skill_id>', methods=['POST'])
    def edit_skill(skill_id):
        data = request.get_json()
        return jsonify({ 'status': 'ok' })

    @app.route('/profile/skills/delete/<int:skill_id>', methods=['POST'])
    def delete_skill(skill_id):
        return jsonify({ 'status': 'ok' })

    # ── Login / Signup Routes ────────────────────────────────────
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name     = request.form.get('name')
            email    = request.form.get('email')
            password = request.form.get('password')
            course   = request.form.get('course')
            bio      = request.form.get('bio')

            existing = next((u for u in users if u['email'] == email), None)
            if existing:
                return render_template('signup.html',
                                       error='An account with that email already exists.')

            users.append({ 'name': name, 'email': email,
                           'password': password, 'course': course, 'bio': bio })
            return redirect(url_for('login'))

        return render_template('signup.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email    = request.form.get('email')
            password = request.form.get('password')
            user     = next((u for u in users
                             if u['email'] == email and u['password'] == password), None)
            if user:
                session['user']  = user['name']
                session['email'] = user['email']
                return redirect(url_for('skills.skills'))
            else:
                return render_template('login.html', error='Invalid email or password.')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    # ── Create tables ────────────────────────────────────────────
    with app.app_context():
        import models
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)