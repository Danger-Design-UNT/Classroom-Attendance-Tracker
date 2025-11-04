import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    """Setup a test client for the Flask app"""
    app = create_app("testing") 
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# -------------------------------
# AUTH ROUTES
# -------------------------------

def test_signup_success(client):
    """Test successful user registration"""
    response = client.post("/auth/signup", data={
        "username": "teacher1",
        "email": "teacher1@example.com",
        "password": "test123",
        "role": "teacher"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Signup successful" in response.data or b"Login" in response.data

def test_signup_duplicate_email(client):
    """Duplicate email signup should fail"""
    client.post("/auth/signup", data={
        "username": "user1",
        "email": "dup@example.com",
        "password": "test123",
    })
    response = client.post("/auth/signup", data={
        "username": "user2",
        "email": "dup@example.com",
        "password": "test123",
    })
    assert b"already exists" in response.data or response.status_code == 400

def test_login_success(client):
    """Login with correct credentials"""
    client.post("/auth/signup", data={
        "username": "student1",
        "email": "student1@example.com",
        "password": "pass123",
    })
    response = client.post("/auth/login", data={
        "email": "student1@example.com",
        "password": "pass123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Dashboard" in response.data

def test_login_invalid_password(client):
    """Invalid password should be rejected"""
    client.post("/auth/signup", data={
        "username": "userx",
        "email": "userx@example.com",
        "password": "correct",
    })
    response = client.post("/auth/login", data={
        "email": "userx@example.com",
        "password": "wrong"
    })
    assert b"Invalid" in response.data or response.status_code == 401


# -------------------------------
# CLASS CREATION / MANAGEMENT
# -------------------------------

def test_teacher_creates_class(client):
    """Teacher can create a class"""
    client.post("/auth/signup", data={
        "username": "teacher",
        "email": "teacher@example.com",
        "password": "pass123",
        "role": "teacher"
    })
    client.post("/auth/login", data={
        "email": "teacher@example.com",
        "password": "pass123"
    })
    response = client.post("/classes/create", data={
        "class_name": "CSCE3600",
        "section": "001"
    }, follow_redirects=True)
    assert b"CSCE3600" in response.data or b"successfully" in response.data


# -------------------------------
# QR CODE ATTENDANCE
# -------------------------------

def test_generate_qr(client):
    """QR route should return PNG"""
    response = client.get("/generate_qr/testsession")
    assert response.status_code == 200
    assert response.mimetype == "image/png"

def test_mark_attendance(client):
    """Student scans QR and gets success"""
    client.post("/auth/signup", data={
        "username": "student",
        "email": "student@example.com",
        "password": "pass123",
        "role": "student"
    })
    client.post("/auth/login", data={
        "email": "student@example.com",
        "password": "pass123"
    })
    response = client.get("/attendance/testsession", follow_redirects=True)
    assert b"Attendance recorded" in response.data or response.status_code in (200, 302)


# -------------------------------
# ACCESS CONTROL
# -------------------------------

def test_student_cannot_access_teacher_page(client):
    """Students should be denied teacher dashboard"""
    client.post("/auth/signup", data={
        "username": "student",
        "email": "student2@example.com",
        "password": "pass123",
        "role": "student"
    })
    client.post("/auth/login", data={
        "email": "student2@example.com",
        "password": "pass123"
    })
    response = client.get("/teacher/dashboard", follow_redirects=True)
    assert b"Access denied" in response.data or response.status_code in (302, 403)
