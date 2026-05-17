from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from __init__ import db
from models import Request, Message, users_have_accepted_connection

chat_bp = Blueprint('chat', __name__)


def has_accepted_connection(user_id):
    return users_have_accepted_connection(current_user.id, user_id)


@chat_bp.route('/chat')
@login_required
def chat():
    accepted = Request.query.filter(
        ((Request.from_user_id == current_user.id) |
         (Request.to_user_id == current_user.id)),
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

    return render_template('chat.html', connections=connections, active_user_id=active_user_id)


@chat_bp.route('/chat/messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    if not has_accepted_connection(user_id):
        return jsonify({'status': 'error', 'message': 'Not an accepted connection'}), 403

    msgs = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    formatted = [
        {'type': 'sent' if m.sender_id == current_user.id else 'received', 'text': m.body}
        for m in msgs
    ]
    return jsonify({'messages': formatted})


@chat_bp.route('/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    user_id = data.get('user_id')
    text = data.get('message', '').strip()

    if not text or not user_id:
        return jsonify({'status': 'error'}), 400

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({'status': 'error'}), 400

    if not has_accepted_connection(user_id):
        return jsonify({'status': 'error', 'message': 'Not an accepted connection'}), 403

    msg = Message(sender_id=current_user.id, receiver_id=user_id, body=text)
    db.session.add(msg)
    db.session.commit()
    return jsonify({'status': 'ok'})
