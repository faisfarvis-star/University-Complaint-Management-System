from app.extensions import db
from app.models import Complaint


def test_student_cannot_view_other_students_complaint(make_client, data, complaint):
    assert make_client("stu2@t.edu").get(f"/complaints/{complaint.id}").status_code == 403
    assert make_client("stu@t.edu").get(f"/complaints/{complaint.id}").status_code == 200


def test_student_cannot_change_status_or_assign(make_client, data, complaint):
    c = make_client("stu@t.edu")
    c.post(f"/complaints/{complaint.id}/status", data={"new_status": "Closed"})
    c.post(f"/complaints/{complaint.id}/assign", data={"staff_id": data.staff.id})
    assert db.session.get(Complaint, complaint.id).status == "Pending"
    assert c.get("/admin/dashboard").status_code == 403
    assert c.get("/staff/dashboard").status_code == 403


def test_student_cannot_comment_on_others(make_client, data, complaint):
    r = make_client("stu2@t.edu").post(f"/complaints/{complaint.id}/comment", data={"message": "hello there"})
    assert r.status_code == 403


def test_staff_sees_only_assigned(make_client, data, complaint):
    from app.services.factory import complaint_service
    complaint_service().assign(complaint.id, data.staff.id, data.admin)
    assert make_client("staff@t.edu").get(f"/complaints/{complaint.id}").status_code == 200
    other = make_client("staff2@t.edu")
    assert other.get(f"/complaints/{complaint.id}").status_code == 403
    assert complaint.title.encode() not in other.get("/staff/complaints").data


def test_staff_cannot_use_admin_or_student_areas(make_client, data):
    c = make_client("staff@t.edu")
    for url in ("/admin/dashboard", "/admin/complaints", "/admin/audit", "/student/dashboard",
                "/student/complaints/new"):
        assert c.get(url).status_code == 403


def test_staff_cannot_assign(make_client, data, complaint):
    r = make_client("staff@t.edu").post(f"/complaints/{complaint.id}/assign", data={"staff_id": data.staff.id})
    assert r.status_code == 403


def test_admin_permissions(make_client, data, complaint):
    c = make_client("admin@t.edu")
    for url in ("/admin/dashboard", "/admin/complaints", "/admin/students", "/admin/staff",
                "/admin/categories", "/admin/audit", "/admin/assignments", f"/complaints/{complaint.id}"):
        assert c.get(url).status_code == 200, url
    assert c.get("/student/dashboard").status_code == 403


def test_admin_creates_staff_and_toggles_accounts(make_client, data):
    from app.models import User
    c = make_client("admin@t.edu")
    r = c.post("/admin/staff/new", data={"full_name": "New Staff", "email": "ns@t.edu", "password": "Secret123"})
    assert r.status_code == 302 and User.query.filter_by(email="ns@t.edu").one().role == "staff"
    c.post(f"/admin/users/{data.student.id}/toggle")
    assert db.session.get(User, data.student.id).is_active is False
    c.post(f"/admin/users/{data.admin.id}/toggle")                       # admins cannot be deactivated
    assert db.session.get(User, data.admin.id).is_active is True


def test_category_management(make_client, data):
    from app.models import Category
    c = make_client("admin@t.edu")
    c.post("/admin/categories", data={"name": "Library", "description": "Books"})
    assert Category.query.filter_by(name="Library").count() == 1
    c.post(f"/admin/categories/{data.cat.id}/delete")                    # fine: unused
    assert db.session.get(Category, data.cat.id) is None


def test_category_in_use_cannot_be_deleted(make_client, data, complaint):
    from app.models import Category
    make_client("admin@t.edu").post(f"/admin/categories/{complaint.category_id}/delete")
    assert db.session.get(Category, complaint.category_id) is not None


def test_csv_report_and_formula_injection(make_client, data, complaint):
    from app.extensions import db
    complaint.title = "=HYPERLINK(\"http://x\")"
    db.session.commit()
    r = make_client("admin@t.edu").get("/admin/reports/complaints.csv")
    assert r.mimetype == "text/csv" and b"Complaint No" in r.data
    assert b"'=HYPERLINK" in r.data


def test_error_pages_are_safe(make_client, data):
    c = make_client("admin@t.edu")
    r = c.get("/complaints/9999")
    assert r.status_code == 404 and b"Traceback" not in r.data
