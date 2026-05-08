import os

class Config:
    # Secret key for sessions and CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'skillswap-dev-secret-key'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///skillswap.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False