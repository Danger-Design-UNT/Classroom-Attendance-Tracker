from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Class
import qrcode                 
import io                      
import base64                 



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



# dashboard routes
@attendance_bp.route('/dashboard/student')
@role_required('student')
def student_dashboard():
    return render_template('dashboard_student.html')

@attendance_bp.route('/dashboard/teacher')
@role_required('teacher')
def teacher_dashboard():
    return render_template('dashboard_teacher.html')



# settings routes
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


# teacher dashboard routes

@attendance_bp.route('/quick_stats')
@role_required('teacher')
def quick_stats():
    return render_template('quick_stats.html')

@attendance_bp.route('/qr-generate', methods=['GET', 'POST'])
@login_required
def qr_generate():
    qr_image_url = None
    message = None

    if request.method == 'POST':
        
        data_to_encode = "https://example.com/attendance/demo?class=999"  

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

        import base64
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        qr_image_url = f"data:image/png;base64,{img_base64}"

        message = "QR code generated! (demo mode — links to example.com)"

    return render_template(
        'generate_qr.html',
        qr_image_url=qr_image_url,
        message=message
    )

@attendance_bp.route('/todays_sessions')
@role_required('teacher')
def todays_sessions():
    return render_template('todays_sessions.html')

@attendance_bp.route('/view_attendance>')
@role_required('teacher')
def view_attendance(classid):
    return render_template('view_attendance.html')

