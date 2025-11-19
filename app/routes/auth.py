from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.forms import SignupForm, LoginForm
from app import limiter
from flask_limiter.util import get_remote_address




auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.signup'))
        
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)




@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("100 per minute", key_func=get_remote_address)
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')

            next_page = request.args.get('next')

            if user.role == 'teacher':
                dashboard = 'attendance.teacher_dashboard'
            else:
                dashboard = 'attendance.student_dashboard'

            return redirect(next_page or url_for(dashboard))

        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'teacher':
        return redirect(url_for('attendance.teacher_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('attendance.student_dashboard'))
    else:
        flash('Unknown role.', 'danger')
        return redirect(url_for('auth.login'))
