from flask import render_template, flash, redirect, url_for
from . import users
from app.models import User, Course, Enrollment 
from app.users.forms import LoginForm, RegistrationForm, EnrollmentForm
from app import db, bcrypt
from flask_login import login_user, login_required, logout_user, current_user

@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash('Login successful!', 'success')

            if user.role == 'admin':
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("main.index"))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template("users/login.html", form=form, user=current_user)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('users.login'))


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email address already in use. Please choose a different one.', 'danger')
            return redirect(url_for('users.register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role='user')

        if User.query.count() == 0:
            user.role = 'admin'

        db.session.add(user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        login_user(user)
        return redirect(url_for('main.index'))

    return render_template('users/register.html', form=form, user=current_user)
