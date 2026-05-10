from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from __init__ import create_app, db
from models import User, Skill, Request, Message

app = create_app()

# ── Flask-Login setup ─────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Create tables on startup ──────────────────────────────────────
with app.app_context():
    db.create_all()

# ── Home ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── Signup ────────────────────────────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('name')
        email    = request.form.get('email')
        password = request.form.get('password')
        course   = request.form.get('course')
        bio      = request.form.get('bio')

        if User.query.filter_by(email=email).first():
            return render_template('signup.html',
                                   error='An account with that email already exists.')

        user = User(name=name, email=email, course=course, bio=bio)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

# ── Login ─────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('skills'))

        return render_template('login.html',
                               error='Invalid email or password.')

    return render_template('login.html')

# ── Logout ────────────────────────────────────────────────────────
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

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

# ── Requests ──────────────────────────────────────────────────────
@app.route('/requests')
@login_required
def requests_page():
    incoming = Request.query.filter_by(
        to_user_id=current_user.id
    ).order_by(Request.created_at.desc()).all()

    outgoing = Request.query.filter_by(
        from_user_id=current_user.id
    ).order_by(Request.created_at.desc()).all()

    return render_template('requests.html', incoming=incoming, outgoing=outgoing)

@app.route('/requests/send/<int:skill_id>', methods=['POST'])
@login_required
def send_request(skill_id):
    skill = Skill.query.get_or_404(skill_id)

    if skill.user_id == current_user.id:
        return jsonify({ 'status': 'error',
                         'message': 'Cannot request your own skill' }), 400

    existing = Request.query.filter_by(
        skill_id     = skill_id,
        from_user_id = current_user.id
    ).first()
    if existing:
        return jsonify({ 'status': 'error',
                         'message': 'Already requested' }), 400

    req = Request(
        skill_id     = skill_id,
        from_user_id = current_user.id,
        to_user_id   = skill.user_id
    )
    db.session.add(req)
    db.session.commit()
    return jsonify({ 'status': 'ok' })

@app.route('/requests/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    req = Request.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        return jsonify({ 'status': 'error' }), 403
    req.status = 'accepted'
    db.session.commit()
    return jsonify({ 'status': 'ok' })

@app.route('/requests/decline/<int:request_id>', methods=['POST'])
@login_required
def decline_request(request_id):
    req = Request.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        return jsonify({ 'status': 'error' }), 403
    req.status = 'declined'
    db.session.commit()
    return jsonify({ 'status': 'ok' })

# ── Chat ──────────────────────────────────────────────────────────
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
        other = req.sender if req.to_user_id == current_user.id else req.receiver
        if other.id not in seen:
            seen.add(other.id)
            connections.append(other)

    return render_template('chat.html', connections=connections)

@app.route('/chat/messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    msgs = Message.query.filter(
        ((Message.sender_id   == current_user.id) &
         (Message.receiver_id == user_id)) |
        ((Message.sender_id   == user_id) &
         (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    formatted = [{
        'type': 'sent' if m.sender_id == current_user.id else 'received',
        'text': m.body
    } for m in msgs]

    return jsonify({ 'messages': formatted })

@app.route('/chat/send', methods=['POST'])
@login_required
def send_message():
    data    = request.get_json()
    user_id = data.get('user_id')
    text    = data.get('message', '').strip()

    if not text or not user_id:
        return jsonify({ 'status': 'error' }), 400

    msg = Message(
        sender_id   = current_user.id,
        receiver_id = int(user_id),
        body        = text
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({ 'status': 'ok' })

# ── Profile ───────────────────────────────────────────────────────
@app.route('/profile')
@login_required
def profile():
    user_skills = Skill.query.filter_by(
        user_id=current_user.id
    ).order_by(Skill.created_at.desc()).all()
    return render_template('profile.html',
                           user=current_user,
                           skills=user_skills)

@app.route('/profile/skills/add', methods=['POST'])
@login_required
def add_skill():
    data = request.get_json(silent=True) or request.form

    name        = data.get('name', '').strip()
    category    = data.get('category', '').strip()
    level       = data.get('level', '').strip()
    description = data.get('description', data.get('desc', '')).strip()

    if not name or not category:
        message = 'Skill name and category are required.'
        if request.is_json:
            return jsonify({ 'status': 'error', 'message': message }), 400
        flash(message, 'error')
        return redirect(url_for('profile'))

    skill = Skill(
        name        = name,
        category    = category,
        level       = level,
        description = description,
        user_id     = current_user.id
    )
    db.session.add(skill)
    db.session.commit()

    if not request.is_json:
        flash('Skill added!', 'success')
        return redirect(url_for('profile'))

    return jsonify({ 'status': 'ok', 'id': skill.id })

@app.route('/profile/skills/edit/<int:skill_id>', methods=['POST'])
@login_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        return jsonify({ 'status': 'error' }), 403
    data              = request.get_json(silent=True) or request.form
    skill.name        = data.get('name', skill.name).strip()
    skill.category    = data.get('category', skill.category).strip()
    skill.level       = data.get('level', skill.level or '').strip()
    skill.description = data.get('description', data.get('desc', skill.description or '')).strip()
    db.session.commit()

    if not request.is_json:
        flash('Skill updated!', 'success')
        return redirect(url_for('profile'))

    return jsonify({ 'status': 'ok' })

@app.route('/profile/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def profile_delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        return jsonify({ 'status': 'error' }), 403
    db.session.delete(skill)
    db.session.commit()

    if not request.is_json:
        flash('Skill deleted.', 'success')
        return redirect(url_for('profile'))

    return jsonify({ 'status': 'ok' })

if __name__ == '__main__':
    app.run(debug=True)
