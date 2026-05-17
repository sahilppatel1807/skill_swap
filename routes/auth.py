from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db
from models import User, normalize_avatar_initials
from forms import (
    LoginForm, SignupForm, ChangePasswordForm,
    ChangeNicknameForm,ChangeNameForm, ChangeEmailForm, DeleteAccountForm
)
from __init__ import limiter
from flask_limiter.errors import RateLimitExceeded

auth_bp = Blueprint('auth', __name__)


@auth_bp.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    form = LoginForm()
    return render_template('login.html', form=form,
                           error='Too many login attempts. Please wait 1 minute and try again.'), 429


@auth_bp.route('/signup', methods=['GET', 'POST'])
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
            return render_template('signup.html', form=form,
                                   error='An account with that email already exists.')
        if User.query.filter_by(nickname=nickname).first():
            return render_template('signup.html', form=form,
                                   error='Nickname is already taken.')

        user = User(
            name=name, nickname=nickname, email=email, course=course, bio=bio,
            avatar_initials=normalize_avatar_initials(nickname, name)
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    
    error = None
    if request.method == 'POST' and form.errors:
        error = next(iter(form.errors.values()))[0]
    return render_template('signup.html', form=form, error=error)

    


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data.strip()
        password = form.password.data
        user = User.query.filter(
            db.func.lower(User.email) == identifier.lower()
        ).first()

        if not user:
            user = User.query.filter_by(nickname=identifier).first()

        if user and user.check_password(password):
            session.pop('_flashes', None)
            login_user(user)
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('skills.skills'))

        return render_template('login.html', form=form,
                               error='Invalid email/nickname or password.')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/settings/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    error = None
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            error = 'Current password is incorrect.'
        elif current_user.check_password(form.new_password.data):  
            error = 'New password must be different from your current password.'
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Password updated successfully.', 'success')
            return redirect(url_for('auth.change_password'))
    elif request.method == 'POST':
        error = next(iter(form.errors.values()))[0]
    return render_template('settings/change_password.html', form=form, error=error)


@auth_bp.route('/settings/change-name', methods=['GET', 'POST'])
@login_required
def change_name():
    form = ChangeNameForm()
    error = None
    success = None
    if form.validate_on_submit():
        new_name = form.name.data.strip()
        if new_name == current_user.name:
            error = 'New name is the same as your current name.'
        else:
            current_user.name = new_name
            db.session.commit()
            flash('Full name updated successfully.', 'success')  
            return redirect(url_for('auth.change_name')) 
    elif request.method == 'POST':
        error = next(iter(form.errors.values()))[0]
    return render_template('settings/change_name.html', form=form, error=error, success=success)

@auth_bp.route('/settings/change-nickname', methods=['GET', 'POST'])
@login_required
def change_nickname():
    form = ChangeNicknameForm()
    error = None
    if form.validate_on_submit():
        new_nickname = form.nickname.data.strip()
        if new_nickname == current_user.nickname:
            error = 'New nickname is the same as your current nickname.'
        elif User.query.filter_by(nickname=new_nickname).first():
            error = 'Nickname is already taken.'
        else:
            current_user.nickname = new_nickname
            db.session.commit()
            flash('Nickname updated successfully.', 'success')
            return redirect(url_for('auth.change_nickname'))
    elif request.method == 'POST':
        error = next(iter(form.errors.values()))[0]
    return render_template('settings/change_nickname.html', form=form, error=error)

@auth_bp.route('/settings/change-email', methods=['GET', 'POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    error = None
    if form.validate_on_submit():
        new_email = form.email.data
        password = form.password.data
        if not current_user.check_password(password):
            error = 'Incorrect password.'
        elif new_email == current_user.email:
            error = 'New email is the same as your current email.'
        elif User.query.filter_by(email=new_email).first():
            error = 'Email already exists.'
        else:
            current_user.email = new_email
            db.session.commit()
            flash('Email updated successfully.', 'success')
            return redirect(url_for('auth.change_email'))
    elif request.method == 'POST':
        error = next(iter(form.errors.values()))[0]
    return render_template('settings/change_email.html', form=form, error=error)

@auth_bp.route('/settings/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()
    error = None
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            error = 'Incorrect password.'
        else:
            user_id = current_user.id
            logout_user()
            user = User.query.get(user_id)
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for('main.index'))
    return render_template('settings/delete_account.html', form=form, error=error)
