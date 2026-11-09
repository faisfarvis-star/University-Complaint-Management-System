import io

import pytest
from flask import g
from flask.testing import FlaskClient

from app import create_app
from app.extensions import db
from app.models import Category, User
from config import TestConfig


class IsolatedClient(FlaskClient):
    """The fixtures keep one app context open, so clear Flask-Login's cached user per request;
    otherwise two logged-in clients in one test would leak identity through flask.g."""

    def open(self, *args, **kwargs):
        g.pop("_login_user", None)
        return super().open(*args, **kwargs)


@pytest.fixture()
def app(tmp_path):
    """Fresh app on a throw-away SQLite file; the development DB is never touched."""
    class Cfg(TestConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{tmp_path / 'test.db'}"
        UPLOAD_FOLDER = str(tmp_path / "uploads")

    app = create_app(Cfg)
    app.test_client_class = IsolatedClient
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def make_user(role, email, name=None, reg=None, password="Passw0rd!"):
    u = User(full_name=name or email.split("@")[0].title(), email=email, role=role,
             registration_number=reg, department="Test Dept")
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture()
def data(app):
    """Admin, two staff, two students and two categories."""
    d = type("Data", (), {})()
    d.admin = make_user("admin", "admin@t.edu")
    d.staff = make_user("staff", "staff@t.edu")
    d.staff2 = make_user("staff", "staff2@t.edu")
    d.student = make_user("student", "stu@t.edu", reg="R1")
    d.student2 = make_user("student", "stu2@t.edu", reg="R2")
    d.cat = Category(name="IT", description="IT issues")
    d.cat2 = Category(name="Facilities")
    db.session.add_all([d.cat, d.cat2])
    db.session.commit()
    return d


def login(client, email, password="Passw0rd!"):
    return client.post("/login", data={"email": email, "password": password}, follow_redirects=False)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_client(app):
    def factory(email):
        c = app.test_client()
        assert login(c, email).status_code == 302
        return c
    return factory


def complaint_payload(cat_id, **over):
    p = {"category_id": cat_id, "title": "Wi-Fi not working", "priority": "High",
         "description": "The Wi-Fi in block B has been down all week."}
    p.update(over)
    return p


@pytest.fixture()
def complaint(app, data):
    from app.services.factory import complaint_service
    return complaint_service().submit(data.student, data.cat.id, "Projector broken",
                                      "The projector in lab 3 does not turn on.", "Medium")


def pdf_file(name="evidence.pdf", content=b"%PDF-1.4 test"):
    return (io.BytesIO(content), name)
