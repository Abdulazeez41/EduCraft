from flask import render_template
from flask_login import current_user
from app.models import Course
from app.main import main

@main.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses, user=current_user)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')
