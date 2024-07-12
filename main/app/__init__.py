from flask import Flask

from app.users.routes import blueprint as user_blueprint
from app.posts.routes import blueprint as post_blueprint
from app.extentions import db, migrate, login_manager
import app.exceptions as app_exception
from app.users.models import User, Code, Follow
from config import DevConfig


def register_blueprint(app):
    app.register_blueprint(user_blueprint)
    app.register_blueprint(post_blueprint)


def register_error_handlers(app):
    app.register_error_handler(404, app_exception.page_not_found)
    app.register_error_handler(500, app_exception.server_error)


def register_shell_context(app):  # for automatic import in flask shell
    def shell_context():
        return {"db": db, "User": User, "Code": Code, "Follow": Follow}

    app.shell_context_processor(shell_context)


app = Flask(__name__)
register_blueprint(app)
register_error_handlers(app)
register_shell_context(app)
app.config.from_object(DevConfig)


db.init_app(app)

from app.users.models import User

migrate.init_app(app, db)
login_manager.init_app(app)


@app.after_request
def after_req(response):
    print("after any request")
    return response


@app.before_request
def before_req():
    print("before any request")
