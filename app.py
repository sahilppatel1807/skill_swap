from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/skills')
def skills():
    return render_template('skills.html')

@app.route('/requests')
def requests():
    return render_template('requests.html')

@app.route('/logout')
def logout():
    # Placeholder logout logic, just redirect to home
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
