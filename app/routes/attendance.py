from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Class, Attendance, Student
import qrcode
import io
import base64
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

attendance_bp = Blueprint('attendance', __name__)


# ==================== Role Required Decorator ====================
def role_required(role):
    def decorator(f):
        @wraps(f)
        @login_required
        def wrapped(*args, **kwargs):
            if getattr(current_user, 'role', None) != role:
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


# ==================== Class Management ====================
@attendance_bp.route('/create_class', methods=['GET', 'POST'])
@role_required('teacher')
def create_class():
    if request.method == 'POST':
        class_name = request.form.get('class_name', '').strip()
        class_section = request.form.get('class_section', '').strip()

        if not class_name:
            flash("Class name is required.", "danger")
            return render_template('create_class.html')

        # Check for duplicate class for this teacher
        existing = Class.query.filter_by(
            user_id=current_user.id,
            class_name=class_name,
            class_section=class_section
        ).first()

        if existing:
            flash("You already have a class with this name and section.", "warning")
        else:
            try:
                new_class = Class(
                    class_name=class_name,
                    class_section=class_section,
                    user_id=current_user.id
                )
                db.session.add(new_class)
                db.session.commit()
                flash(f"Class '{class_name}' created successfully!", "success")
                return redirect(url_for('attendance.teacher_dashboard'))
            except Exception as e:
                db.session.rollback()
                flash("An error occurred while creating the class. Please try again.", "danger")

    return render_template('create_class.html')


@attendance_bp.route('/view_classes')
@role_required('teacher')
def view_classes():
    classes = Class.query.filter_by(user_id=current_user.id).all()
    return render_template('view_classes.html', classes=classes)


# ==================== Placeholder Routes (to stop BuildError) ====================
@attendance_bp.route('/quick_stats')
@role_required('teacher')
def quick_stats():
    return render_template('quick_stats.html')


@attendance_bp.route('/todays_sessions')
@role_required('teacher')
def todays_sessions():
    return render_template('todays_sessions.html')

@attendance_bp.route('/view_attendance/<int:class_id>')
@role_required('teacher')
def view_attendance(class_id):
    records = Attendance.query.filter_by(class_id=class_id).all()
    return render_template('view_attendance_table.html', records=records, class_id=class_id)


# ==================== Generate QR Code - Main Feature ====================
@attendance_bp.route('/qr-generate', methods=['GET', 'POST'])
@role_required('teacher')
def qr_generate():
    classes = Class.query.filter_by(user_id=current_user.id).all()
    qr_image_url = None
    message = None

    if request.method == 'POST':
        class_id = request.form.get('class_id')
        
        if class_id and class_id.strip():
            data_to_encode = url_for('attendance.mark_attendance', class_id=class_id, _external=True)
        else:
            data_to_encode = request.form.get('data')

        if not data_to_encode or not data_to_encode.strip():
            flash("Please select a class or enter a valid attendance link", "danger")
        else:
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
            message = "✅ QR Code generated successfully! Show this to your students."

    return render_template(
        'generate_qr.html',
        qr_image_url=qr_image_url,
        message=message,
        classes=classes
    )


# ==================== Mark Attendance (QR Redirect Target) ====================
@attendance_bp.route('/mark_attendance/<int:class_id>')
@role_required('student')
def mark_attendance(class_id):
    class_obj = Class.query.get_or_404(class_id)   # Better error handling

    # Get or create student
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        student = Student(
            name=current_user.name or current_user.email.split('@')[0],
            email=current_user.email
        )
        db.session.add(student)
        db.session.commit()

    today = datetime.utcnow().date()

    # Check if already marked today
    existing = Attendance.query.filter(
        Attendance.student_id == student.id,
        Attendance.class_id == class_id,
        db.func.date(Attendance.timestamp) == today
    ).first()

    if existing:
        return render_template('attendance_success.html', 
                               class_name=class_obj.class_name, 
                               already_marked=True)

    # Mark attendance
    new_attendance = Attendance(
        student_id=student.id,
        class_id=class_id,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_attendance)
    db.session.commit()

    return render_template('attendance_success.html', 
                           class_name=class_obj.class_name, 
                           already_marked=False)
    
    
# ==================== Student QR Scanner ====================
@attendance_bp.route('/scan_qr')
@role_required('student')
def scan_qr():
    return render_template('qr.html')
# ==================== Student Attendance History ====================
@attendance_bp.route('/StudentAttendanceHistory')
@role_required('student')
def student_attendance_history():
    student = Student.query.filter_by(email=current_user.email).first()
    records = Attendance.query.filter_by(student_id=student.id).all() if student else []
    return render_template('student_attendance_history.html', records=records)

