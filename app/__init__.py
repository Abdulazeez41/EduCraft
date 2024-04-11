from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(Config)

    from .main.routes import main
    from .users.routes import users
    from .courses.routes import courses
    from .admin.routes import admin

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(users, url_prefix='/')
    app.register_blueprint(courses, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/')

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
