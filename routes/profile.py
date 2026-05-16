from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from __init__ import db
from datetime import datetime
from models import Skill, normalize_avatar_initials

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
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
    return render_template('profile.html', user=current_user,
                           skills=user_skills, categories=categories)


@profile_bp.route('/profile/edit', methods=['POST'])
@login_required
def edit_profile():
    current_user.nickname = request.form.get('nickname', current_user.nickname).strip()
    current_user.course = request.form.get('course', current_user.course or '').strip()
    current_user.bio = request.form.get('bio', current_user.bio or '').strip()
    current_user.avatar_initials = normalize_avatar_initials(
        request.form.get('avatar_initials', ''), current_user.nickname
    )
    db.session.commit()
    flash('Profile updated!', 'success')
    return redirect(url_for('profile.profile'))


@profile_bp.route('/profile/skills/add', methods=['POST'])
@login_required
def add_skill():
    data = request.get_json(silent=True) or request.form
    name = data.get('name', '').strip()
    category = data.get('category', '').strip()
    level = data.get('level', '').strip()
    description = data.get('description', data.get('desc', '')).strip()

    if not name or not category:
        message = 'Skill name and category are required.'
        if request.is_json:
            return jsonify({'status': 'error', 'message': message}), 400
        flash(message, 'error')
        return redirect(url_for('profile.profile'))

    existing = Skill.query.filter_by(
        user_id=current_user.id,
        name=name,
        level=level
    ).first()

    if existing:
        message = 'You already have a skill with this name and level.'
        if request.is_json:
            return jsonify({'status': 'error', 'message': message}), 400
        flash(message, 'error')
        return redirect(url_for('profile.profile'))
    # ─────────────────────────────────────────────────────────

    skill = Skill(name=name, category=category, level=level,
                  description=description, user_id=current_user.id)
    db.session.add(skill)
    db.session.commit()

@profile_bp.route('/profile/skills/edit/<int:skill_id>', methods=['POST'])
@login_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        return jsonify({'status': 'error'}), 403
    data = request.get_json(silent=True) or request.form
    skill.name = data.get('name', skill.name).strip()
    skill.category = data.get('category', skill.category).strip()
    skill.level = data.get('level', skill.level or '').strip()
    skill.description = data.get('description', data.get('desc', skill.description or '')).strip()
    skill.updated_at = datetime.utcnow()
    db.session.commit()
    if not request.is_json:
        flash('Skill updated!', 'success')
        return redirect(url_for('profile.profile'))
    return jsonify({'status': 'ok'})


@profile_bp.route('/profile/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def profile_delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        return jsonify({'status': 'error'}), 403
    db.session.delete(skill)
    db.session.commit()
    if not request.is_json:
        flash('Skill deleted.', 'success')
        return redirect(url_for('profile.profile'))
    return jsonify({'status': 'ok'})
