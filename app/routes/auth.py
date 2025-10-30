# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student') 

        if User.query.filter_by(email=email).first():
            flash('Email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)  
            flash('Login successful!', 'success')

            if user.role == 'student':
                return redirect(url_for('attendance.student_dashboard'))
            else:
                return redirect(url_for('attendance.teacher_dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()  
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
