from flask import Blueprint, render_template

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/')
def dashboard():
    return render_template('dashboard.html')