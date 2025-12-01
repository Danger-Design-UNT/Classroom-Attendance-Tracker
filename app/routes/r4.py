from flask import Blueprint, render_template
from app import db
from app.models import Student, Class, Attendance

r4_bp = Blueprint("r4", __name__)

@r4_bp.route("/classes/<int:class_id>/students")
def list_students(class_id):
    # Get the class
    clazz = Class.query.get(class_id)
    if not clazz:
        return "Class not found", 404

    # Get students who have attendance records for this class
    students = (
        db.session.query(Student)
        .join(Attendance, Attendance.student_id == Student.id)
        .filter(Attendance.class_id == class_id)
        .order_by(Student.name.asc())
        .all()
    )

    return render_template(
        "r4_students.html",
        clazz=clazz,
        students=students,
    )

