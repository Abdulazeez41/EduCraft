from flask import render_template, flash, redirect, url_for
from . import auth
from app.models import User, InstructorProfile
from app.users.forms import LoginForm, LearnerRegistrationForm, InstructorRegistrationForm
from app.utils.emails import send_email
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Checks if the user is already logged in. If so, redirects them to the appropriate dashboard based on their role.
    If the user is not authenticated, the login form is displayed. On successful login, the user is redirected 
    to their respective dashboard (instructor or learner).
    """
    if current_user.is_authenticated:
        return redirect_user_based_on_role(current_user)

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.password:
            if not user.password.startswith("pbkdf2:sha256:"): 
                flash("Your password needs to be reset. Please contact support.", "danger")
                return redirect(url_for("auth.login"))

            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash("Login successful!", "success")
                return redirect_user_based_on_role(user)

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html", form=form, user=current_user)


def redirect_user_based_on_role(user):
    """
    Redirect users based on their role.
    """
    if user.role == "learner":
        return redirect(url_for("learner.learner_dashboard"))
    elif user.role == "instructor":
        return redirect(url_for("instructor.instructor_dashboard"))
    else:
        flash("Invalid role assigned to user.", "danger")
        return redirect(url_for("auth.login"))


@auth.route('/logout')
@login_required
def logout():
    """
    Logs out the user and redirects them to the login page with a confirmation message.
    """
    logout_user() 
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/register/learner', methods=['GET', 'POST'])
def register_learner():
    form = LearnerRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='learner')
        
        try:
            db.session.add(user)
            db.session.commit()
            send_email(
                "Welcome to EduCraft!",
                form.email.data,
                f"Hi {form.username.data},\n\nThank you for registering as a Student at EduCraft!"
            )
            flash('Account created successfully as a Student. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email or username already exists. Please use a different one.', 'danger')
    
    return render_template('auth/register_learner.html', form=form)


@auth.route('/register/instructor', methods=['GET', 'POST'])
def register_instructor():
    form = InstructorRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='instructor')
        
        try:
            db.session.add(user)
            db.session.commit()
            
            instructor_profile = InstructorProfile(user_id=user.id, bio=form.bio.data, expertise=form.expertise.data)
            db.session.add(instructor_profile)
            db.session.commit()
            
            send_email(
                "Welcome to EduCraft!",
                form.email.data,
                f"Hi {form.username.data},\n\nThank you for registering as an Instructor at EduCraft!"
            )
            flash('Instructor account created successfully. You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError:
            db.session.rollback()
            flash('Email or username already exists. Please use a different one.', 'danger')
    
    return render_template('auth/register_instructor.html', form=form)
