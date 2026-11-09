from app.models import User
from .conftest import login


def test_student_registration(client, app, data):
    r = client.post("/register", data={"full_name": "New Student", "email": "new@t.edu",
                    "registration_number": "R99", "password": "Secret123", "confirm": "Secret123"})
    assert r.status_code == 302
    u = User.query.filter_by(email="new@t.edu").one()
    assert u.role == "student"
    assert u.password_hash != "Secret123"          # hashed, never plaintext


def test_registration_cannot_choose_role(client, app, data):
    client.post("/register", data={"full_name": "Evil", "email": "evil@t.edu", "registration_number": "R77",
                "password": "Secret123", "confirm": "Secret123", "role": "admin"})
    assert User.query.filter_by(email="evil@t.edu").one().role == "student"


def test_duplicate_email_rejected(client, data):
    r = client.post("/register", data={"full_name": "Dup", "email": "stu@t.edu", "registration_number": "R55",
                    "password": "Secret123", "confirm": "Secret123"})
    assert r.status_code == 200 and b"already exists" in r.data


def test_login_and_logout(client, data):
    assert login(client, "stu@t.edu").status_code == 302
    assert client.get("/student/dashboard").status_code == 200
    assert client.post("/logout").status_code == 302
    assert client.get("/student/dashboard").status_code == 302   # back to login


def test_invalid_login(client, data):
    r = client.post("/login", data={"email": "stu@t.edu", "password": "wrong"})
    assert r.status_code == 200 and b"Invalid email or password" in r.data


def test_deactivated_user_cannot_login(client, data, app):
    from app.extensions import db
    data.student.is_active = False
    db.session.commit()
    r = client.post("/login", data={"email": "stu@t.edu", "password": "Passw0rd!"})
    assert b"deactivated" in r.data


def test_guest_redirected_to_login(client):
    assert client.get("/admin/dashboard").status_code == 302


def test_open_redirect_blocked(client, data):
    r = client.post("/login?next=https://evil.example/", data={"email": "stu@t.edu", "password": "Passw0rd!"})
    assert "evil.example" not in r.headers["Location"]
