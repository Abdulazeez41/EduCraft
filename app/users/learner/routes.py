from flask import render_template, redirect, flash, url_for, send_from_directory, request
from . import learner
from app.models import User, Course, Enrollment, CompletedActivity, Quiz, Assignment, StudentProgress, Submission, Bookmark, Notification
from app import db
from flask_login import login_required, current_user
from app.certificates.generator import CertificateGenerator
import os
import zipfile
from io import BytesIO

@learner.route('/dashboard')
@login_required
def learner_dashboard():
    """
    Renders the learner's dashboard view. 
    It checks the learner's enrolled courses, bookmarked lessons, and progress.
    If the user is not a learner, they are redirected with an 'access denied' flash message.
    """
    if current_user.role != 'learner':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    enrolled_courses = Enrollment.query.filter_by(user_id=current_user.id).all()
    bookmarked_lessons = Bookmark.query.filter_by(user_id=current_user.id).all()
    progress_data = StudentProgress.query.filter_by(user_id=current_user.id).all()

    progress_labels = [p.course.title for p in progress_data]
    progress_values = [p.progress for p in progress_data]
    
    return render_template('learner/dashboard.html', enrolled_courses=enrolled_courses, bookmarked_lessons=bookmarked_lessons, user=current_user, progress_labels=progress_labels, progress_values=progress_values)

@learner.route('/browse_courses')
@login_required
def browse_courses():
    """
    Allows the learner to browse courses by filtering by category and difficulty level.
    Fetches courses based on the provided filters or returns all courses if no filters are applied.
    """
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    
    query = Course.query
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    
    courses = query.all()
    return render_template('learner/browse_courses.html', courses=courses)

@learner.route('/enroll/<int:course_id>')
@login_required
def enroll_course(course_id):
    """
    Enrolls a learner in a course if they are not already enrolled.
    Once enrolled, sends a success flash message and redirects to the learner's dashboard.
    """
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()

    if not enrollment:
        new_enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        flash('Enrolled successfully!', 'success')

    return redirect(url_for('learner.dashboard'))

@learner.route('/bookmark/<int:lesson_id>')
@login_required
def bookmark_lesson(lesson_id):
    """
    Allows a learner to bookmark a lesson. If the lesson is not already bookmarked, it is added to the learner's bookmarks.
    A flash message is shown to notify the user that the lesson was successfully bookmarked.
    """
    bookmark = Bookmark.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if not bookmark:
        new_bookmark = Bookmark(user_id=current_user.id, lesson_id=lesson_id)
        db.session.add(new_bookmark)
        db.session.commit()
        flash('Lesson bookmarked!', 'success')
    
    return redirect(url_for('learner.dashboard'))

@learner.route('/submit_assignment/<int:assignment_id>', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    """
    Handles the submission of an assignment.
    Learner uploads a file, which is then saved and associated with the specific assignment.
    After successful submission, the learner is notified with a flash message.
    """
    assignment = Assignment.query.get_or_404(assignment_id)
    submitted_file = request.files['submitted_file']

    if submitted_file:
        file_path = f"uploads/{submitted_file.filename}"
        submitted_file.save(file_path)

        new_submission = Submission(
            user_id=current_user.id,
            assignment_id=assignment_id,
            submitted_file=file_path
        )
        db.session.add(new_submission)
        db.session.commit()
        flash('Assignment submitted successfully!', 'success')

    return redirect(url_for('learner.dashboard'))

@learner.route('/download-certificate/<int:learner_id>')
@login_required
def download_certificate(learner_id):
    """
    Generates and allows the learner to download a zip file containing all certificates 
    for completed courses.
    If no courses have been completed, it returns a message indicating no certificates.
    """
    learner = User.query.get_or_404(learner_id)
    
    completed_courses = db.session.query(Course).join(CompletedActivity).filter(CompletedActivity.user_id == learner_id).all()
    
    if not completed_courses:
        return {"message": "No completed courses found for this learner."}

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for course in completed_courses:
            cert_generator = CertificateGenerator(course.title, learner.username, course.instructor.username)
            certificate_path = cert_generator.generate_certificate()

            if certificate_path:
                cert_filename = os.path.basename(certificate_path)
                zip_file.write(certificate_path, cert_filename)

    zip_buffer.seek(0)

    return send_from_directory('app/static/certificates', zip_buffer, as_attachment=True, attachment_filename="certificates.zip")

@learner.route('/notifications')
@login_required
def view_notifications():
    """
    Displays a list of unread notifications for the learner.
    Notifications are filtered by the learner's user ID and 'read' status.
    """
    notifications = Notification.query.filter_by(user_id=current_user.id, read=False).all()
    return render_template('learner/notifications.html', notifications=notifications)

@learner.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """
    Marks a specific notification as read.
    The notification must belong to the currently logged-in learner.
    After marking as read, the user is redirected back to the notifications page.
    """
    notification = Notification.query.get(notification_id)
    if notification and notification.user_id == current_user.id:
        notification.read = True
        db.session.commit()
    return redirect(url_for('learner.view_notifications'))

@learner.route('/take_quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    """
    Renders a page for the learner to take a quiz.
    It fetches the quiz associated with the provided quiz ID and presents it to the learner.
    """
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('learner/quiz.html', quiz=quiz)
