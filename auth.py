from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('skills.skills'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        course   = request.form.get('course', '').strip()
        bio      = request.form.get('bio', '').strip()

        if not name or not email or not password:
            return render_template('signup.html',
                                   error='Name, email and password are required.')
        if len(password) < 6:
            return render_template('signup.html',
                                   error='Password must be at least 6 characters.')
        if User.query.filter_by(email=email).first():
            return render_template('signup.html',
                                   error='An account with that email already exists.')

        user = User(name=name, email=email, course=course, bio=bio)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('skills.skills'))

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('skills.skills'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('skills.skills'))

        return render_template('login.html', error='Invalid email or password.')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
