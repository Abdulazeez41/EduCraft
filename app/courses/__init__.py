from flask import Blueprint

courses = Blueprint('courses', __name__, template_folder='templates')

from . import routes
