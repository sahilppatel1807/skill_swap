# Dummy users store (replace with database later)
users = []

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name     = request.form.get('name')
        email    = request.form.get('email')
        password = request.form.get('password')
        course   = request.form.get('course')
        bio      = request.form.get('bio')

        # Check if email already exists
        existing = next((u for u in users if u['email'] == email), None)
        if existing:
            return render_template('signup.html',
                                   error='An account with that email already exists.')

        # Save user
        users.append({
            'name':     name,
            'email':    email,
            'password': password,
            'course':   course,
            'bio':      bio
        })

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        # Check credentials
        user = next((u for u in users
                     if u['email'] == email and u['password'] == password), None)

        if user:
            session['user'] = user['name']
            session['email'] = user['email']
            return redirect(url_for('skills'))
        else:
            return render_template('login.html',
                                   error='Invalid email or password.')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))