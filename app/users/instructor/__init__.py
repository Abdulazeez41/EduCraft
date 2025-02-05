from flask import Blueprint

instructor = Blueprint('instructor', __name__, template_folder='templates')

from . import routes
