import flask
from flask_login import login_required, current_user
from app import db
from models import Skill, Request

skills_bp = flask.Blueprint('skills', __name__)
DEFAULT_SKILL_CATEGORIES = ['Programming', 'Design', 'Music', 'Communication']


# ── Skills Feed (Browse all skills) ─────────────────────────────
@skills_bp.route('/skills')
@skills_bp.route('/skills', methods=['GET', 'POST'])
def skills():
    if flask.request.method == 'POST':
        if not current_user.is_authenticated:
            flask.flash('You must be logged in to post a skill.', 'error')
            return flask.redirect(flask.url_for('skills.skills'))

        name        = flask.request.form.get('name', '').strip()
        category    = flask.request.form.get('category', '').strip()
        level       = flask.request.form.get('level', '').strip()
        description = flask.request.form.get('description', '').strip()

        errors = []
        if not name:
            errors.append('Skill name is required.')
        if len(name) > 100:
            errors.append('Name must be under 100 characters.')
        if not category:
            errors.append('Category is required.')
        if len(description) > 500:
            errors.append('Description must be under 500 characters.')

        if errors:
            for e in errors:
                flask.flash(e, 'error')
            # Re-render the feed with current data and errors
            # (fall through to GET logic below)
        else:
            skill = Skill(user_id=current_user.id, name=name,
                        category=category, level=level, description=description)
            db.session.add(skill)
            db.session.commit()
            flask.flash('Skill added!', 'success')
            return flask.redirect(flask.url_for('skills.skills'))

    query    = Skill.query
    category = flask.request.args.get('category', '').strip()
    search   = flask.request.args.get('search', '').strip()

    if category:
        query = query.filter_by(category=category)
    if search:
        like  = f'%{search}%'
        query = query.filter(
            db.or_(Skill.name.ilike(like), Skill.description.ilike(like))
        )

    skills_list = query.order_by(Skill.created_at.desc()).limit(50).all()
    categories  = [c[0] for c in db.session.query(Skill.category).distinct().all() if c[0]]

    return flask.render_template('skills.html',
        skills           = skills_list,
        categories       = categories,
        current_category = category,
        current_search   = search
    )


# ── Request a Skill ──────────────────────────────────────────────
@skills_bp.route('/skills/request/<int:skill_id>', methods=['POST'])
@login_required
def request_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)

    # Can't request your own skill
    if skill.user_id == current_user.id:
        flask.flash('You cannot request your own skill.', 'error')
        return flask.redirect(flask.url_for('skills.skills'))

    # Prevent duplicate pending requests
    existing = Request.query.filter_by(
        skill_id     = skill_id,
        from_user_id = current_user.id,
        status       = 'pending'
    ).first()

    if existing:
        flask.flash('You already have a pending request for this skill.', 'error')
        return flask.redirect(flask.url_for('skills.skills'))

    req = Request(
        skill_id     = skill_id,
        from_user_id = current_user.id,
        to_user_id   = skill.user_id,
        message      = flask.request.form.get('message', '').strip()
    )
    db.session.add(req)
    db.session.commit()
    flask.flash(f'Request sent to {skill.owner.name}!', 'success')
    return flask.redirect(flask.url_for('skills.skills'))


# ── Profile: view own skills ─────────────────────────────────────
@skills_bp.route('/profile')
@login_required
def profile():
    my_skills = Skill.query.filter_by(user_id=current_user.id)\
                           .order_by(Skill.created_at.desc()).all()
    existing_categories = [
        category for (category,) in db.session.query(Skill.category).distinct().all()
        if category
    ]
    categories = list(dict.fromkeys(DEFAULT_SKILL_CATEGORIES + existing_categories))

    return flask.render_template(
        'profile.html',
        user=current_user,
        skills=my_skills,
        categories=categories
    )


# ── Profile: add skill ───────────────────────────────────────────
@skills_bp.route('/profile/skills/add', methods=['POST'])
@login_required
def add_skill():  # (Optional) You may keep or remove the add_skill route below if you want to allow skill posting from the profile page as well.
    name        = flask.request.form.get('name', '').strip()
    category    = flask.request.form.get('category', '').strip()
    level       = flask.request.form.get('level', '').strip()
    description = flask.request.form.get('description', '').strip()

    errors = []
    if not name:             errors.append('Skill name is required.')
    if len(name) > 100:      errors.append('Name must be under 100 characters.')
    if not category:         errors.append('Category is required.')
    if len(description) > 500: errors.append('Description must be under 500 characters.')

    if errors:
        for e in errors: flask.flash(e, 'error')
        return flask.redirect(flask.url_for('skills.profile'))

    skill = Skill(user_id=current_user.id, name=name,
                  category=category, level=level, description=description)
    db.session.add(skill)
    db.session.commit()
    flask.flash('Skill added!', 'success')
    return flask.redirect(flask.url_for('skills.profile'))


# ── Profile: edit skill ──────────────────────────────────────────
@skills_bp.route('/profile/skills/edit/<int:skill_id>', methods=['POST'])
@login_required
def edit_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        flask.flash('Not authorised.', 'error')
        return flask.redirect(flask.url_for('skills.profile'))

    skill.name        = flask.request.form.get('name',        skill.name).strip()
    skill.category    = flask.request.form.get('category',    skill.category).strip()
    skill.level       = flask.request.form.get('level',       skill.level).strip()
    skill.description = flask.request.form.get('description', skill.description).strip()
    db.session.commit()
    flask.flash('Skill updated!', 'success')
    return flask.redirect(flask.url_for('skills.profile'))


# ── Profile: delete skill ────────────────────────────────────────
@skills_bp.route('/profile/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id != current_user.id:
        flask.flash('Not authorised.', 'error')
        return flask.redirect(flask.url_for('skills.profile'))

    db.session.delete(skill)
    db.session.commit()
    flask.flash('Skill deleted.', 'success')
    return flask.redirect(flask.url_for('skills.profile'))
