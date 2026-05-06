from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db            = SQLAlchemy()
login_manager = LoginManager()
bcrypt        = Bcrypt()
migrate       = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY']                     = 'skillswap-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI']        = 'sqlite:///skillswap.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'

    # Register blueprints
    # from auth           import auth_bp
    # from routes.chat    import chat_bp
    # from routes.profile import profile_bp
    from routes.skills  import skills_bp

    # app.register_blueprint(auth_bp)
    # app.register_blueprint(chat_bp)
    # app.register_blueprint(profile_bp)
    app.register_blueprint(skills_bp)

    # Index route — inside create_app so 'app' exists
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('skills.skills'))
        return render_template('index.html')

    # Create tables
    with app.app_context():
        import models
        db.create_all()

    return app          


app = create_app()      # ← this is what flask shell needs

if __name__ == '__main__':
    app.run(debug=True)