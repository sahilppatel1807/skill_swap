import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_database_path = "sqlite:///" + os.path.join(basedir, 'skillswap.db')

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default_database_path)
    
    # Secret key for sessions and CSRF
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set.")

    SQLALCHEMY_TRACK_MODIFICATIONS = False