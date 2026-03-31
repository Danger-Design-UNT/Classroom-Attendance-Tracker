from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Class, Attendance, Student
import qrcode
import io
import base64
from datetime import datetime

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

# ==================== Dashboard Routes ====================
@attendance_bp.route('/dashboard/student')
@role_required('student')
def student_dashboard():
    return render_template('dashboard_student.html')

@attendance_bp.route('/dashboard/teacher')
@role_required('teacher')
def teacher_dashboard():
    return render_template('dashboard_teacher.html')



# ==================== Settings Routes ====================
@attendance_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@attendance_bp.route('/settings/teacher')
@role_required('teacher')
def teacher_settings():
    return render_template('settings_teacher.html')

@attendance_bp.route('/scan_qr')
@login_required
def scan_qr():
    return render_template('qr.html')

@attendance_bp.route('/StudentAttendanceHistory')
@role_required('student')
def student_attendance_history():
    return render_template('student_attendance_history.html')

@attendance_bp.route('/create_class', methods=['GET', 'POST'])
@login_required
def create_class():
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        class_section = request.form.get('class_section')

        new_class = Class(class_name=class_name, class_section=class_section, user_id=current_user.id)
        db.session.add(new_class)
        db.session.commit()

        flash("Class created successfully!", "success")
        return redirect(url_for('attendance.teacher_dashboard'))
    return render_template('create_class.html')

@attendance_bp.route('/view_classes')
@login_required
def view_classes():
    classes = Class.query.filter_by(user_id=current_user.id).all()
    return render_template('view_classes.html', classes=classes)


@attendance_bp.route('/update_name', methods=['POST'])
@login_required
def update_name():
    new_name = request.form.get('name')

    current_user.name = new_name
    db.session.commit()

    flash("Name updated successfully!", "success")
    return redirect(url_for('attendance.settings'))


# ==================== Teacher Dashboard Routes ====================

@attendance_bp.route('/quick_stats')
@role_required('teacher')
def quick_stats():
    return render_template('quick_stats.html')

@attendance_bp.route('/todays_sessions')
@role_required('teacher')
def todays_sessions():
    return render_template('todays_sessions.html')

@attendance_bp.route('/view_attendance>')
@role_required('teacher')
def view_attendance(classid):
    return render_template('view_attendance.html')


# ==================== Generate qr code routes logic ====================


@attendance_bp.route('/qr-generate', methods=['GET', 'POST'])
@role_required('teacher')
def qr_generate():
    qr_image_url = None
    message = None
    classes = Class.query.filter_by(user_id=current_user.id).all()   # show teacher's classes

    if request.method == 'POST':
        # Get the link the teacher wants in the QR (from the form)
        data_to_encode = request.form.get('data')

        if not data_to_encode or data_to_encode.strip() == "":
            flash("Please enter a valid attendance link", "danger")
            return render_template('generate_qr.html', qr_image_url=None, message=None, classes=classes)

        # Generate QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data_to_encode)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        qr_image_url = f"data:image/png;base64,{img_base64}"

        message = "✅ QR Code generated successfully! Share or display it."

    return render_template(
        'generate_qr.html',
        qr_image_url=qr_image_url,
        message=message,
        classes=classes
    )


@attendance_bp.route('/mark_attendance/<int:class_id>')
@role_required('student')
def mark_attendance(class_id):
    # Find or create student record for the logged-in user
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        student = Student(name=current_user.name or "Student", email=current_user.email)
        db.session.add(student)
        db.session.commit()

    # Check if already marked today for this class
    today = datetime.utcnow().date()
    existing = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.class_id == class_id,
        db.func.date(Attendance.timestamp) == today
    ).first()

    if existing:
        flash("✅ You are already marked present for this class today!", "info")
    else:
        new_attendance = Attendance(
            student_id=student.id,
            class_id=class_id,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_attendance)
        db.session.commit()
        flash("🎉 Attendance marked successfully!", "success")

    return redirect(url_for('attendance.student_dashboard'))