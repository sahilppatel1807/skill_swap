from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from __init__ import db
from models import Skill, Request

skills_bp = Blueprint('skills', __name__)


@skills_bp.route('/skills')
@login_required
def skills():
    query    = Skill.query
    category = request.args.get('category', '').strip()
    search   = request.args.get('search', '').strip()

    if category:
        query = query.filter_by(category=category)
    if search:
        like  = f'%{search}%'
        query = query.filter(
            db.or_(Skill.name.ilike(like), Skill.description.ilike(like))
        )

    skills_list = query.order_by(Skill.created_at.desc()).all()

    my_requests = Request.query.filter_by(
        from_user_id=current_user.id
    ).all()

    request_map = {r.skill_id: r.status for r in my_requests}

    categories = [c[0] for c in db.session.query(Skill.category).distinct().all() if c[0]]
    if not categories:
        categories = ["Programming", "Design", "Music", "Communication"]

    return render_template('skills.html',
        skills            = skills_list,
        categories        = categories,
        current_category  = category,
        current_search    = search,
        request_map       = request_map
    )


@skills_bp.route('/skills/new', methods=['POST'])
@login_required
def post_skill():
    name = request.form.get('name', '').strip()
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()

    errors = []
    if not name:               errors.append('Skill name is required.')
    if len(name) > 100:        errors.append('Name must be under 100 characters.')
    if not category:           errors.append('Category is required.')
    if len(description) > 500: errors.append('Description must be under 500 characters.')

    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('skills.skills'))

    skill = Skill(name=name, category=category, description=description,
                  user_id=current_user.id)
    db.session.add(skill)
    db.session.commit()
    flash('Skill posted!', 'success')
    return redirect(url_for('skills.skills'))
