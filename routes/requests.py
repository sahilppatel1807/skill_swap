from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from __init__ import db
from models import Skill, Request, users_have_accepted_connection

requests_bp = Blueprint('requests', __name__)


@requests_bp.route('/requests')
@login_required
def requests_page():
    incoming = Request.query.filter_by(
        to_user_id=current_user.id
    ).order_by(Request.created_at.desc()).all()
    outgoing = Request.query.filter_by(
        from_user_id=current_user.id
    ).order_by(Request.created_at.desc()).all()
    return render_template('requests.html', incoming=incoming, outgoing=outgoing)


@requests_bp.route('/requests/mark-sent-seen', methods=['POST'])
@login_required
def mark_sent_requests_seen():
    Request.query.filter(
        Request.from_user_id == current_user.id,
        Request.status != 'pending',
        Request.from_user_seen.is_(False),
    ).update({Request.from_user_seen: True}, synchronize_session=False)
    db.session.commit()
    return jsonify({'status': 'ok'})


@requests_bp.route('/request_skill', methods=['POST'])
@login_required
def request_skill():
    skill_id = request.form.get('skill_id')
    skill = Skill.query.get_or_404(skill_id)
    if skill.user_id == current_user.id:
        return jsonify({'status': 'error', 'message': 'Cannot request own skill'}), 400
    if users_have_accepted_connection(current_user.id, skill.user_id):
        return jsonify({'status': 'error', 'message': 'Already connected with this user'}), 400
    existing = Request.query.filter_by(
        skill_id=skill_id, from_user_id=current_user.id, status='pending'
    ).first()
    if existing:
        return jsonify({'status': 'error', 'message': 'Already requested'}), 400
    req = Request(skill_id=skill_id, from_user_id=current_user.id,
                  to_user_id=skill.user_id, status='pending')
    db.session.add(req)
    db.session.commit()
    return jsonify({'status': 'ok'})


@requests_bp.route('/requests/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_request(request_id):
    req = Request.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        if request.is_json:
            return jsonify({'status': 'error'}), 403
        return redirect(url_for('requests.requests_page'))
    req.status = 'accepted'
    req.to_user_seen = True
    req.from_user_seen = False

    Request.query.filter(
        Request.from_user_id == req.from_user_id,
        Request.to_user_id == req.to_user_id,
        Request.status == 'pending',
        Request.id != req.id,
    ).update(
        {Request.status: 'accepted', Request.from_user_seen: False},
        synchronize_session=False,
    )

    db.session.commit()
    if request.is_json:
        return jsonify({'status': 'ok'})
    return redirect(url_for('requests.requests_page'))


@requests_bp.route('/requests/decline/<int:request_id>', methods=['POST'])
@login_required
def decline_request(request_id):
    req = Request.query.get_or_404(request_id)
    if req.to_user_id != current_user.id:
        if request.is_json:
            return jsonify({'status': 'error'}), 403
        return redirect(url_for('requests.requests_page'))
    req.status = 'declined'
    req.to_user_seen = True
    req.from_user_seen = False
    db.session.commit()
    if request.is_json:
        return jsonify({'status': 'ok'})
    return redirect(url_for('requests.requests_page'))
