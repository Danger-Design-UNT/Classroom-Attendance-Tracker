from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db



attendance_bp = Blueprint('attendance', __name__)


def role_required(role):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if current_user.role != role:
                flash("Access denied.", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@attendance_bp.route('/dashboard/student')
@role_required('student')
def student_dashboard():
    return render_template('dashboard_student.html')


@attendance_bp.route('/dashboard/teacher')
@role_required('teacher')
def teacher_dashboard():
    return render_template('dashboard_teacher.html')


@attendance_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


@attendance_bp.route('/scan_qr')
@login_required
def scan_qr():
    return render_template('qr.html')


@attendance_bp.route('/create_class', methods=['GET', 'POST'])
@login_required
def create_class():
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        flash("Class created successfully!", "success")
        return redirect(url_for('attendance.teacher_dashboard'))
    return render_template('create_class.html')


@attendance_bp.route('/qr_generate/<int:classid>', methods=['POST', 'GET'])
@login_required
def qr_generate():
    return render_template('qr_generate.html', classid=1) # Placeholder for class ID until class management is implemented fully


@attendance_bp.route('/update_name', methods=['POST'])
@login_required
def update_name():
    new_name = request.form.get('name')

    current_user.name = new_name
    db.session.commit()

    flash("Name updated successfully!", "success")
    return redirect(url_for('attendance.settings'))
