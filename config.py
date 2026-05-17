import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
default_database_path = "sqlite:///" + os.path.join(instance_dir, 'skillswap.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', default_database_path)
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig:
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret-key"
    TESTING = True
    WTF_CSRF_ENABLED = False

class SeleniumTestConfig:
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "selenium-test-secret-key"
    TESTING = True
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
