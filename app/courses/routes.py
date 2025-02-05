from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Course, StudentProgress, Enrollment, CompletedActivity, ForumPost, ForumReply
from app.utils.emails import send_email
from . import courses

@courses.route('/enroll_course/<int:course_id>')
@login_required
def enroll_course(course_id):
    """
    Handles course enrollment for the user. It ensures the user is not already enrolled
    and sends an email notification upon successful enrollment.
    """
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if not enrollment:
        new_enrollment = Enrollment(user=current_user, course=course)
        db.session.add(new_enrollment)
        db.session.commit()

        send_email(
            "Course Enrollment Confirmation",
            current_user.email,
            f"You have successfully enrolled in {course.title}. Start learning now!"
        )
        flash('Enrolled successfully! Check your email.', 'success')

    return redirect(url_for('courses.list_courses'))

@courses.route('/complete_course/<int:course_id>')
@login_required
def complete_course(course_id):
    """
    Marks the course as completed for the user. If the user has progress in the course,
    it updates their progress to 100% and sends an email notification about the completion.
    """
    progress = StudentProgress.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if progress:
        progress.progress = 100.0
        db.session.commit()

        send_email(
            "Course Completion",
            current_user.email,
            f"Congratulations! You have completed {progress.course.title}. Your certificate is now available."
        )

        flash('Course marked as complete! Check your email for the certificate.', 'success')

    return redirect(url_for('learner.dashboard'))

@courses.route('/view_course/<int:course_id>')
@login_required
def view_course(course_id):
    """
    Displays course details and calculates the user's progress if they are enrolled in the course.
    Shows the number of completed activities compared to the total activities.
    """
    course = Course.query.get_or_404(course_id)

    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    user_is_enrolled = enrollment is not None

    course_progress = None
    if user_is_enrolled:
        completed_activities = CompletedActivity.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        total_activities = db.session.query(CompletedActivity).filter_by(course_id=course_id).count()

        if total_activities > 0:
            course_progress = (completed_activities / total_activities) * 100

    return render_template('courses/view_course.html', course=course, user=current_user, user_is_enrolled=user_is_enrolled, course_progress=course_progress)

@courses.route('/list_courses')
@login_required
def list_courses():
    """
    Retrieves and displays the list of all available courses.
    """
    courses_list = Course.query.all()
    return render_template('courses/list_courses.html', courses=courses_list, user=current_user)

@courses.route('/course_details/<int:course_id>')
@login_required
def course_details(course_id):
    """
    Displays detailed information about a specific course, including whether the user is enrolled.
    """
    course = Course.query.get_or_404(course_id)
    is_enrolled = Enrollment.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    return render_template('courses/course_details.html', course=course, is_enrolled=is_enrolled, user=current_user)

@courses.route('/forum/<int:course_id>')
@login_required
def course_forum(course_id):
    """
    Displays the forum posts related to the course, ordered by the most recent post.
    """
    course = Course.query.get_or_404(course_id)
    posts = ForumPost.query.filter_by(course_id=course_id).order_by(ForumPost.timestamp.desc()).all()
    return render_template('courses/forum.html', course=course, posts=posts)

@courses.route('/forum/create/<int:course_id>', methods=['POST'])
@login_required
def create_forum_post(course_id):
    """
    Allows users to create new forum posts for a specific course.
    The post requires both a title and content to be valid.
    """
    title = request.form.get('title')
    content = request.form.get('content')
    if title and content:
        new_post = ForumPost(user_id=current_user.id, course_id=course_id, title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully!', 'success')
    return redirect(url_for('courses.course_forum', course_id=course_id))

@courses.route('/forum/reply/<int:post_id>', methods=['POST'])
@login_required
def reply_to_forum(post_id):
    """
    Allows users to reply to a forum post. The reply requires content and is linked to the original post.
    """
    content = request.form.get('content')
    if content:
        reply = ForumReply(post_id=post_id, user_id=current_user.id, content=content)
        db.session.add(reply)
        db.session.commit()
        flash('Reply posted!', 'success')
    return redirect(request.referrer)
