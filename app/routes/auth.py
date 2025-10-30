from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.forms import SignupForm, LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')



@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        role = form.role.data

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.signup'))
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)





@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('attendance.student_dashboard') if user.role == 'student' else url_for('attendance.teacher_dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
