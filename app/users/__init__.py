from flask import Blueprint

users = Blueprint('users', __name__)

from .instructor.routes import instructor
from .learner.routes import learner

users.register_blueprint(instructor, url_prefix='/instructor')
users.register_blueprint(learner, url_prefix='/learner')
