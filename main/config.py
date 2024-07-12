import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    CSRF_ENABLE = True
    CSRF_SESSION_KEY = os.environ.get("CSRF_SESSION_KEY")
    SECRET_KEY = os.environ.get("SECRET_KEY")


class ProdConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = ...


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(Config.BASE_DIR, "app.db")
    FLASK_DEBUG = True
    FLASK_ENV = "development"
    DEBUG = True
    ENV = "development"
