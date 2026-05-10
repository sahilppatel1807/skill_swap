from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from _init_ import create_app, db
from models import User, Skill, Request, Message

app = create_app()



# ── Skills ────────────────────────────────────────────────────────
@app.route('/skills')
@login_required
def skills():
    all_skills = Skill.query.order_by(Skill.created_at.desc()).all()
    return render_template('skills.html', skills=all_skills)

@app.route('/skills/create', methods=['POST'])
@login_required
def create_skill():
    data  = request.get_json()
    skill = Skill(
        title       = data.get('title'),
        category    = data.get('category'),
        description = data.get('description'),
        user_id     = current_user.id
    )
    db.session.add(skill)
    db.session.commit()
    return jsonify({ 'status': 'ok', 'id': skill.id })

@app.route('/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        return jsonify({ 'status': 'error', 'message': 'Unauthorized' }), 403
    db.session.delete(skill)
    db.session.commit()
    return jsonify({ 'status': 'ok' })

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