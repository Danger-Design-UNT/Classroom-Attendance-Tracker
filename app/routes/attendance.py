from flask import Blueprint, render_template, redirect, url_for, session

attendance_bp = Blueprint('attendance', __name__)  # <- match the import in __init__.py

@attendance_bp.route('/dashboard/student')
def student_dashboard():
    return render_template('dashboard_student.html')

@attendance_bp.route('/dashboard/teacher')
def teacher_dashboard():
    return render_template('dashboard_teacher.html')
