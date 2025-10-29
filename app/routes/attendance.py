from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps

attendance_bp = Blueprint('attendance', __name__)  

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for('auth.login'))
            if role and session.get('role') != role:
                flash("Access denied.", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@attendance_bp.route('/dashboard/student')
def student_dashboard():
    # later: check if user is logged in and role == 'student' 
    return render_template('dashboard_student.html')

@attendance_bp.route('/dashboard/teacher')
def teacher_dashboard():
    # later: check if user is logged in and role == 'teacher' 
    return render_template('dashboard_teacher.html')
