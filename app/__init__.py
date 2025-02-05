from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from flask_socketio import SocketIO
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
mail = Mail()
socketio = SocketIO()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

    from .auth.routes import auth
    from .main.routes import main
    from .courses.routes import courses
    from .users.instructor.routes import instructor
    from .users.learner.routes import learner

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(courses, url_prefix='/courses')
    app.register_blueprint(instructor, url_prefix='/instructor')
    app.register_blueprint(learner, url_prefix='/learner')

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    socketio.init_app(app, cors_allowed_origins="*")

    return app
