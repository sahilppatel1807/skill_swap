from flask import Flask, render_template
app = Flask(__name__)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/chat')
def chat():
    return "Chat page"

@app.route('/skills')
def skills():
    return "Skills page"

@app.route('/requests')
def requests():
    return "Requests page"

@app.route('/profile')
def profile():
    return "Profile page"

@app.route('/logout')
def logout():
    return "Logout"

if __name__ == '__main__':
    app.run(debug=True)