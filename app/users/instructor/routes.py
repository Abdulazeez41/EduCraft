from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import User, Course, CompletedActivity, CourseResource, Enrollment, Quiz, Announcement, Assignment, Submission, StudentProgress
from app.users.instructor.forms import QuizForm, AssignmentForm
from datetime import datetime
from . import instructor
from app.courses.forms import CourseForm
import os
import mimetypes


@instructor.route('/dashboard')
@login_required
def instructor_dashboard():
    """
    Renders the instructor's dashboard, listing courses they have created.
    Access is restricted to users with the 'instructor' role.
    """
    if current_user.role != 'instructor':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    courses = Course.query.filter_by(instructor_id=current_user.id).all()
    if not courses:
        flash('No courses found.', 'info')
    chart_labels = [course.name for course in courses] if courses else []

    print("Chart Labels:", chart_labels, type(chart_labels))
    return render_template('instructor/dashboard.html', chart_labels=chart_labels, courses=courses, user=current_user)

@instructor.route('/create_course', methods=['GET', 'POST'])
@login_required
def create_course():
    """
    Allows instructors to create a new course. If the instructor has no permission,
    a flash message is displayed and they're redirected to the home page.
    """
    if current_user.role != 'instructor':
        flash('You do not have permission to create a course.', 'danger')
        return redirect(url_for('main.index'))

    form = CourseForm()

    if form.validate_on_submit():
        print("✅ Form validated!")
        print(f"📌 Title: {form.title.data}, Description: {form.description.data}, Instructor ID: {current_user.id}")

        media_filename = None
        if form.media.data:
            file = form.media.data
            media_filename = secure_filename(file.filename)
            
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            upload_path = os.path.join(upload_folder, media_filename)

            allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
            file_extension = os.path.splitext(file.filename)[1].lower()
            mime_type, _ = mimetypes.guess_type(file.filename)

            if file_extension not in allowed_extensions or mime_type is None:
                flash("Invalid file type. Allowed types: jpg, png, mp4, avi, pdf.", "danger")
                return redirect(request.url)

            try:
                file.save(upload_path)
                print("✅ Successfully saved")
            except Exception as e:
                flash(f"Error uploading file: Please try again.", "danger")
                return redirect(request.url)
        
        course = Course(
            title=form.title.data,
            description=form.description.data,
            instructor_id=current_user.id,
            date_created=form.date_created.data if form.date_created.data else datetime.utcnow(),
            media_url=f'static/uploads/{media_filename}' if media_filename else None,
            category=form.category.data,
            difficulty_level=form.difficulty_level.data
        )

        try:
            db.session.add(course)
            print("✅ Course added to session!")  # Debugging
            print("🔍 Pending to commit:", db.session.new)  # Show new objects
            print("🔄 Modified objects:", db.session.dirty)
            db.session.commit()
            print("✅ Course committed to database!")
            flash('Course created successfully!', 'success')
            return redirect(url_for('instructor.instructor_dashboard'))
        except Exception as e:
            db.session.rollback()
            print("❌Database Error:", e)
            flash(f'Error saving course: {e}', 'danger')

    return render_template('instructor/create_course.html', form=form, user=current_user)

@instructor.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    """
    Allows instructors to edit an existing course. If the course does not belong to
    the current instructor, they will be denied access and redirected.
    """
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('instructor.dashboard'))
    
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.date_created = form.date_created.data
        course.prerequisites = form.prerequisites.data
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('instructor.dashboard'))
    
    return render_template('instructor/edit_course.html', form=form, course=course)

@instructor.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    """
    Allows instructors to delete a course. Only the instructor who created the course
    can delete it.
    """
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('instructor.dashboard'))
    
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted successfully.', 'success')
    return redirect(url_for('instructor.dashboard'))

@instructor.route('/manage_courses', methods=['GET'])
@login_required
def manage_courses():
    """
    Displays a list of courses created by the instructor, including course details
    and an option to manage learners.
    """
    if current_user.role != 'instructor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    courses = Course.query.filter_by(instructor_id=current_user.id).all()

    course_data = []
    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).count()
        course_data.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'date_created': course.date_created,
            'enrollment_count': enrollments
        })

    return render_template('instructor/manage_courses.html', courses=course_data)

@instructor.route('/manage_learners/<int:course_id>', methods=['GET'])
@login_required
def manage_learners(course_id):
    """
    Displays a list of learners enrolled in a specific course, including their
    progress and other details.
    """
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('instructor.dashboard'))
    
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    learner_data = []
    for enrollment in enrollments:
        learner = User.query.get(enrollment.user_id)
        completed_activities = CompletedActivity.query.filter_by(user_id=learner.id, course_id=course_id).count()
        learner_data.append({
            'id': learner.id,
            'username': learner.username,
            'email': learner.email,
            'enrollment_date': enrollment.enrollment_date,
            'status': enrollment.status,
            'completed_activities': completed_activities
        })
    
    return render_template('instructor/manage_learners.html', course=course, learners=learner_data)

@instructor.route('/send_feedback/<int:course_id>/<int:learner_id>', methods=['POST'])
@login_required
def send_feedback(course_id, learner_id):
    """
    Allows instructors to send feedback to a specific learner. The feedback is
    sent via flash messages and the learner’s details are fetched.
    """
    course = Course.query.get_or_404(course_id)
    if course.instructor_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('instructor.dashboard'))
    
    learner = User.query.get_or_404(learner_id)
    feedback_message = request.form.get('feedback_message')
    if feedback_message:
        flash(f'Feedback sent to {learner.username}: {feedback_message}', 'success')
    else:
        flash('Feedback cannot be empty.', 'danger')
    
    return redirect(url_for('instructor.manage_learners', course_id=course_id))

@instructor.route('/create_quiz/<int:course_id>', methods=['GET', 'POST'])
@login_required
def create_quiz(course_id):
    """
    Allows instructors to create a quiz for a specific course. Upon form submission,
    the quiz is saved to the database.
    """
    form = QuizForm()
    if form.validate_on_submit():
        quiz = Quiz(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            course_id=course_id
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('instructor.dashboard'))
    return render_template('instructor/create_quiz.html', form=form)

@instructor.route('/create_assignment/<int:course_id>', methods=['GET', 'POST'])
@login_required
def create_assignment(course_id):
    """
    Allows instructors to create an assignment for a specific course. The assignment
    can include a file upload. Once submitted, the assignment is saved to the database.
    """
    form = AssignmentForm()
    if form.validate_on_submit():
        file_path = None
        if form.file_upload.data:
            file = form.file_upload.data
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            file_path = f'static/uploads/{filename}'

        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            course_id=course_id
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Assignment created successfully!', 'success')
        return redirect(url_for('instructor.dashboard'))
    return render_template('instructor/create_assignment.html', form=form)

@instructor.route('/grade_submission/<int:submission_id>', methods=['POST'])
@login_required
def grade_submission(submission_id):
    """
    Allows instructors to grade student submissions for assignments or quizzes.
    Feedback and grade are saved to the submission.
    """
    submission = Submission.query.get_or_404(submission_id)
    if 'grade' in request.form:
        submission.grade = request.form['grade']
    if 'feedback' in request.form:
        submission.feedback = request.form['feedback']
    db.session.commit()
    flash('Submission graded successfully!', 'success')
    return redirect(url_for('instructor.dashboard'))

@instructor.route('/send_announcement/<int:course_id>', methods=['POST'])
@login_required
def send_announcement(course_id):
    """
    Allows instructors to send announcements to students enrolled in a course.
    The announcement is stored and displayed accordingly.
    """
    if current_user.role != 'instructor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    content = request.form.get('content')
    announcement = Announcement(course_id=course_id, instructor_id=current_user.id, content=content)
    db.session.add(announcement)
    db.session.commit()
    flash('Announcement sent successfully!', 'success')
    return redirect(url_for('instructor.dashboard'))

@instructor.route('/analytics')
@login_required
def view_analytics():
    """
    Provides analytics for instructors, such as course completion rates
    and student enrollment statistics.
    """
    if current_user.role != 'instructor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    course_statistics = db.session.query(
        Course.title, 
        db.func.avg(StudentProgress.progress).label("average_completion"),
        db.func.count(StudentProgress.id).label("total_students")
    ).join(StudentProgress).group_by(Course.id).all()

    return render_template('instructor/analytics.html', statistics=course_statistics)

@instructor.route('/upload_resource/<int:course_id>', methods=['POST'])
@login_required
def upload_resource(course_id):
    """
    Allows instructors to upload additional course resources (e.g., documents, videos).
    These resources are saved and linked to the course for student access.
    """
    if current_user.role != 'instructor':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.index'))

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    resource = CourseResource(course_id=course_id, file_name=filename, file_url=file_path)
    db.session.add(resource)
    db.session.commit()
    flash('Resource uploaded successfully!', 'success')
    return redirect(url_for('instructor.manage_course', course_id=course_id))
