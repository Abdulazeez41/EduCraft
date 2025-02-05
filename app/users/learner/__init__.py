from flask import Blueprint

learner = Blueprint('learner', __name__, template_folder='templates')

from . import routes
