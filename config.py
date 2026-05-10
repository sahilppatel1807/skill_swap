import os

basedir = os.path.abspath(os.path.dirname(__file__))
default_database_path = "sqlite:///" + os.path.join(basedir, 'skillswap.db')

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default_database_path)
    
    # Secret key for sessions and CSRF
    SECRET_KEY = "skillswap-dev-secret-key"

    SQLALCHEMY_TRACK_MODIFICATIONS = False