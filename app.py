from flask import render_template, redirect, url_for, request, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import inspect, text
from __init__ import create_app, db
from models import User, Skill, Request, Message, normalize_avatar_initials
from forms import LoginForm, SignupForm, ChangePasswordForm, ChangeNicknameForm, ChangeEmailForm, DeleteAccountForm
app = create_app()

# ── Flask-Login setup ─────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_nav_pending_requests():
    """Compute navbar Requests red-dot count (unseen request activity)."""
    if current_user.is_authenticated:
        # Recipient side: show dot for pending incoming requests not yet handled.
        incoming_pending_unseen = Request.query.filter(
            Request.to_user_id == current_user.id,
            Request.status == 'pending',
            Request.to_user_seen.is_(False),
        ).count()

        # Sender side: show dot when the recipient has responded (accepted/declined)
        # and the sender hasn't seen that response yet.
        outgoing_response_unseen = Request.query.filter(
            Request.from_user_id == current_user.id,
            Request.status != 'pending',
            Request.from_user_seen.is_(False),
        ).count()

        return {'nav_requests_unseen_count': incoming_pending_unseen + outgoing_response_unseen}

    return {'nav_requests_unseen_count': 0}


# ── Create tables on startup ──────────────────────────────────────
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

    # Ensure notification columns exist in the `requests` table (no migrations here).
    request_columns = [column['name'] for column in inspector.get_columns('requests')]
    if 'to_user_seen' not in request_columns:
        db.session.execute(text('ALTER TABLE requests ADD COLUMN to_user_seen INTEGER NOT NULL DEFAULT 0'))
        db.session.commit()
    if 'from_user_seen' not in request_columns:
        db.session.execute(text('ALTER TABLE requests ADD COLUMN from_user_seen INTEGER NOT NULL DEFAULT 1'))
        db.session.commit()
# ── Home ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

# ── Signup ────────────────────────────────────────────────────────
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        name = form.name.data
        nickname = form.nickname.data
        email = form.email.data
        password = form.password.data
        course = form.course.data
        bio = form.bio.data

        if User.query.filter_by(email=email).first():
            return render_template(
                'signup.html',
                form=form,
                error='An account with that email already exists.'
            )

        if User.query.filter_by(nickname=nickname).first():
            return render_template(
                'signup.html',
                form=form,
                error='Nickname is already taken.'
            )

        user = User(
            name=name,
            nickname=nickname,
            email=email,
            course=course,
            bio=bio,
            avatar_initials=normalize_avatar_initials('', name)
        )

        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html', form=form)
# ── Login ─────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        identifier = form.identifier.data
        password = form.password.data

        user = User.query.filter_by(email=identifier).first()

        if not user:
            user = User.query.filter_by(nickname=identifier).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('skills'))

        return render_template(
            'login.html',
            form=form,
            error='Invalid email/nickname or password.'
        )

    return render_template('login.html', form=form)

# ── Logout ────────────────────────────────────────────────────────
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/settings/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    error = None

    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data

        if not current_user.check_password(current_password):
            error = 'Current password is incorrect.'
        else:
            current_user.set_password(new_password)
            db.session.commit()
            logout_user()
            return redirect(url_for('login'))

    elif request.method == 'POST':
        error = next(iter(form.errors.values()))[0]

    return render_template(
        'settings/change_password.html',
        form=form,
        error=error
    )

@app.route('/settings/change-nickname', methods=['GET', 'POST'])
@login_required
def change_nickname():
    form = ChangeNicknameForm()
    error = None

    if form.validate_on_submit():
        new_nickname = form.nickname.data

        existing_user = User.query.filter_by(nickname=new_nickname).first()

        if existing_user and existing_user.id != current_user.id:
            error = 'This nickname is already taken.'
        else:
            current_user.nickname = new_nickname
            db.session.commit()
            return redirect(url_for('profile'))

    elif request.method == 'POST':
        error = next(iter(form.errors.values()))[0]

    return render_template(
        'settings/change_nickname.html',
        form=form,
        error=error
    )

@app.route('/settings/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    error = None

    if form.validate_on_submit():
        new_email = form.email.data
        password = form.password.data

        if not current_user.check_password(password):
            error = 'Incorrect password.'
        elif User.query.filter_by(email=new_email).first():
            error = 'Email already exists.'
        else:
            current_user.email = new_email
            db.session.commit()
            return redirect(url_for('profile'))

    elif request.method == 'POST':
        error = next(iter(form.errors.values()))[0]

    return render_template(
        'settings/change_email.html',
        form=form,
        error=error
    )

@app.route('/settings/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    error = None

    if form.validate_on_submit():
        password = form.password.data

        if not current_user.check_password(password):
            error = 'Incorrect password.'
        else:
            user_id = current_user.id
            logout_user()

            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()

            return redirect(url_for('index'))

    return render_template(
        'settings/delete_account.html',
        form=form,
        error=error
    )

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


@app.route('/requests/mark-sent-seen', methods=['POST'])
@login_required
def mark_sent_requests_seen():
    # Sender clears the "new response" dot only after viewing Sent Requests.
    Request.query.filter(
        Request.from_user_id == current_user.id,
        Request.status != 'pending',
        Request.from_user_seen.is_(False),
    ).update(
        {Request.from_user_seen: True},
        synchronize_session=False,
    )
    db.session.commit()
    return jsonify({'status': 'ok'})

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
        to_user_id   = skill.user_id,
        # Recipient hasn't handled it yet; sender hasn't seen a response yet.
        to_user_seen   = False,
        from_user_seen = True,
    )
    db.session.add(req)
    db.session.commit()
    return jsonify({ 'status': 'ok' })

@app.route('/requests/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    req = Request.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        if request.is_json:
            return jsonify({ 'status': 'error' }), 403
        return redirect(url_for('requests_page'))

    req.status = 'accepted'
    # Recipient has handled it; sender should get a "new response" dot.
    req.to_user_seen = True
    req.from_user_seen = False
    db.session.commit()

    if request.is_json:
        return jsonify({ 'status': 'ok' })
    return redirect(url_for('requests_page'))

@app.route('/requests/decline/<int:request_id>', methods=['POST'])
@login_required
def decline_request(request_id):
    req = Request.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        if request.is_json:
            return jsonify({ 'status': 'error' }), 403
        return redirect(url_for('requests_page'))

    req.status = 'declined'
    # Recipient has handled it; sender should get a "new response" dot.
    req.to_user_seen = True
    req.from_user_seen = False
    db.session.commit()

    if request.is_json:
        return jsonify({ 'status': 'ok' })
    return redirect(url_for('requests_page'))

# ── Chat ──────────────────────────────────────────────────────────
def has_accepted_connection(user_id):
    return Request.query.filter(
        Request.status == 'accepted',
        (
            ((Request.from_user_id == current_user.id) &
             (Request.to_user_id == user_id)) |
            ((Request.from_user_id == user_id) &
             (Request.to_user_id == current_user.id))
        )
    ).first() is not None

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

    requested_user_id = request.args.get('user_id', type=int)
    active_user_id = None
    if requested_user_id in seen:
        active_user_id = requested_user_id
    elif connections:
        active_user_id = connections[0].id

    return render_template(
        'chat.html',
        connections=connections,
        active_user_id=active_user_id
    )

@app.route('/chat/messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    if not has_accepted_connection(user_id):
        return jsonify({ 'status': 'error', 'message': 'Not an accepted connection' }), 403

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

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({ 'status': 'error' }), 400

    if not has_accepted_connection(user_id):
        return jsonify({ 'status': 'error', 'message': 'Not an accepted connection' }), 403

    msg = Message(
        sender_id   = current_user.id,
        receiver_id = user_id,
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
    default_categories = ['Programming', 'Design', 'Music', 'Communication']
    existing_categories = [
        category for (category,) in db.session.query(Skill.category).distinct().all()
        if category
    ]
    categories = list(dict.fromkeys(default_categories + existing_categories))

    return render_template('profile.html',
                           user=current_user,
                           skills=user_skills,
                           categories=categories)

@app.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    current_user.name = request.form.get('name', current_user.name).strip()
    current_user.course = request.form.get('course', current_user.course or '').strip()
    current_user.bio = request.form.get('bio', current_user.bio or '').strip()
    current_user.avatar_initials = normalize_avatar_initials(
        request.form.get('avatar_initials', ''),
        current_user.name
    )

    db.session.commit()
    flash('Profile updated!', 'success')
    return redirect(url_for('profile'))

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
