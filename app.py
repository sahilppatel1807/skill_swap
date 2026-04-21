from flask import Flask, render_template, redirect, url_for, request, jsonify, session

app = Flask(__name__)
app.secret_key = 'skillswap-secret-key'

# ── Dummy Data (replace with database queries later) ────────────
CURRENT_USER = 'Sahil'

connections = [
    { 'id': 1, 'name': 'Sara Ali',  'avatar': 'SA' },
    { 'id': 2, 'name': 'Jake Lee',  'avatar': 'JL' },
]

messages_store = {
    1: [
        { 'sender': 'Sara Ali', 'text': 'Hey! Thanks for accepting my request.' },
        { 'sender': 'Sahil',    'text': 'No problem! When do you want to start learning Python?' },
        { 'sender': 'Sara Ali', 'text': 'How about tomorrow at 3 PM?' },
        { 'sender': 'Sahil',    'text': 'Sounds good! I\'ll send you some resources beforehand.' },
        { 'sender': 'Sara Ali', 'text': 'Hey! Ready to start?' },
    ],
    2: [
        { 'sender': 'Jake Lee', 'text': 'Thanks for accepting!' },
        { 'sender': 'Sahil',    'text': 'Of course! What skill did you want to learn?' },
    ]
}

# ── Existing Routes ──────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/skills')
def skills():
    return render_template('skills.html')

@app.route('/requests')
def requests():
    return render_template('requests.html')

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    return render_template('profile.html')

# ── Chat Routes ──────────────────────────────────────────────────
@app.route('/chat')
def chat():
    return render_template('chat.html', connections=connections)

@app.route('/chat/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    msgs = messages_store.get(user_id, [])

    # Format for frontend — mark each as sent or received
    formatted = []
    for m in msgs:
        formatted.append({
            'type': 'sent' if m['sender'] == CURRENT_USER else 'received',
            'text': m['text']
        })

    return jsonify({ 'messages': formatted })

@app.route('/chat/send', methods=['POST'])
def send_message():
    data = request.get_json()

    user_id  = data.get('user_id')
    text     = data.get('message', '').strip()

    if not text or not user_id:
        return jsonify({ 'status': 'error', 'message': 'Missing data' }), 400

    # Save to in-memory store
    if user_id not in messages_store:
        messages_store[user_id] = []

    messages_store[user_id].append({
        'sender': CURRENT_USER,
        'text':   text
    })

    return jsonify({ 'status': 'ok' })

if __name__ == '__main__':
    app.run(debug=True)
