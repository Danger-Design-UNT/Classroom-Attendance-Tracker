from flask import Blueprint, render_template, request, redirect, url_for
from PyPDF2 import PdfReader
from app import db
from app.models import Student, Class, Attendance

r4_bp = Blueprint("r4", __name__)

@r4_bp.route("/classes/<int:class_id>/students")
def list_students(class_id):
    clazz = Class.query.get(class_id)
    if not clazz:
        return "Class not found", 404

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
        students=students
    )


@r4_bp.route("/classes/<int:class_id>/upload-roster", methods=["POST"])
def upload_roster(class_id):
    clazz = Class.query.get(class_id)
    if not clazz:
        return "Class not found", 404

    file = request.files.get("roster_pdf")
    if not file:
        return "No file uploaded", 400

    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    buffer = []

    for line in lines:
        buffer.append(line)

        # treat any line with @ as an email
        if "@" in line:
            email = line
            name = " ".join(buffer[:-1])
            buffer = []

            student = Student.query.filter_by(email=email).first()
            if not student:
                student = Student(name=name, email=email)
                db.session.add(student)
                db.session.flush()

            existing = Attendance.query.filter_by(
                student_id=student.id,
                class_id=clazz.id
            ).first()

            if not existing:
                attendance = Attendance(
                    student_id=student.id,
                    class_id=clazz.id
                )
                db.session.add(attendance)

    db.session.commit()

    return redirect(url_for("r4.list_students", class_id=class_id))
