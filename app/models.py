from datetime import datetime
from flask_login import UserMixin
from app import db

# Constants
ROLE_CHOICES = ('user', 'instructor', 'learner')
QUESTION_TYPES = ('MCQ', 'Short Answer', 'Coding')
SUBMISSION_STATUSES = ('pending', 'graded')

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='learner')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    instructor_profile = db.relationship('InstructorProfile', uselist=False, backref='user', cascade="all, delete")
    enrollments = db.relationship('Enrollment', backref='user', lazy=True, cascade="all, delete-orphan")
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True, cascade="all, delete-orphan")
    completed_activities = db.relationship('CompletedActivity', backref='user', lazy=True, cascade="all, delete-orphan")
    forum_posts = db.relationship('ForumPost', backref='author', lazy=True, cascade="all, delete-orphan")
    forum_replies = db.relationship('ForumReply', backref='author', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"

class InstructorProfile(db.Model):
    __tablename__ = 'instructor_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    bio = db.Column(db.Text, nullable=False)
    expertise = db.Column(db.String(255), nullable=False)

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    instructor = db.relationship('User', backref='courses')
    activities = db.relationship('Activity', backref='course', lazy=True, cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade="all, delete-orphan")
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    prerequisites = db.Column(db.Text)
    media_url = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    difficulty_level = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"<Course {self.title} by {self.instructor_id}>"

class CourseResource(db.Model):
    __tablename__ = 'course_resources'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    enrollment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='active')

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(20), nullable=False, default="lesson")
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class CompletedActivity(db.Model):
    __tablename__ = 'completed_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Quiz(db.Model):
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False, default='MCQ')
    correct_answer = db.Column(db.Text, nullable=True)

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    replies = db.relationship('ForumReply', backref='post', lazy=True, cascade="all, delete-orphan")

class ForumReply(db.Model):
    __tablename__ = 'forum_replies'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    due_date = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text, nullable=False)

class Submission(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False, index=True)
    submitted_file = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    grade = db.Column(db.Integer, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')

class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False, index=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=True, index=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)

class StudentProgress(db.Model):
    __tablename__ = 'student_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    progress = db.Column(db.Float, default=0.0)
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def update_progress(self, completed, total):
        if total > 0:
            self.progress = (completed / total) * 100
            db.session.commit()
