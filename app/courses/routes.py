from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course, Enrollment, CompletedActivity
from . import courses

@courses.route('/enroll_course/<int:course_id>')
@login_required
def enroll_course(course_id):
    course = Course.query.get_or_404(course_id)

    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if enrollment:
        flash('You are already enrolled in this course.', 'info')
    else:
        new_enrollment = Enrollment(user=current_user, course=course)
        db.session.add(new_enrollment)
        db.session.commit()
        flash('You have successfully enrolled in the course.', 'success')

    return redirect(url_for('courses.list_courses'))

@courses.route('/view_course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)

    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    user_is_enrolled = enrollment is not None

    course_progress = None
    if user_is_enrolled:
        completed_activities = CompletedActivity.query.filter_by(user_id=current_user.id, course_id=course_id).count()
        total_activities = course.activities.count()

        if total_activities > 0:
            course_progress = (completed_activities / total_activities) * 100

    return render_template('courses/view_course.html', course=course, user=current_user, user_is_enrolled=user_is_enrolled, course_progress=course_progress)


@courses.route('/list_courses')
@login_required
def list_courses():
    courses_list = Course.query.all()
    return render_template('courses/list_courses.html', courses=courses_list, user=current_user)

@courses.route('/course_details/<int:course_id>')
@login_required
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    is_enrolled = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    return render_template('courses/course_details.html', course=course, is_enrolled=is_enrolled, user=current_user)