from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course
from app.admin import admin
from app.courses.forms import CourseForm

@admin.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.', 'danger')
        return redirect(url_for('main.index'))
    
    courses = Course.query.all()

    return render_template('admin/admin_dashboard.html', courses=courses, user=current_user)

@admin.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    if current_user.role != 'admin':
        flash('You do not have permission to create a course.', 'danger')
        return redirect(url_for('main.index'))

    form = CourseForm()

    if form.validate_on_submit():
        course = Course(title=form.title.data, description=form.description.data, instructor=current_user)
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/create_course.html', form=form, user=current_user)
