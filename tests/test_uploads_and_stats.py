import io

from werkzeug.datastructures import FileStorage

from app.services.factory import complaint_service, stats_service
from app.utils.files import UploadPolicy, validate_upload

POLICY = UploadPolicy(max_size=1024)


def fs(content, name):
    return FileStorage(stream=io.BytesIO(content), filename=name)


def test_valid_files_accepted():
    assert validate_upload(fs(b"%PDF-1.7 hello", "a.pdf"), POLICY) is None
    assert validate_upload(fs(b"\x89PNG\r\n\x1a\n....", "a.png"), POLICY) is None
    assert validate_upload(fs(b"plain text", "notes.txt"), POLICY) is None


def test_disallowed_extension_rejected():
    assert "not allowed" in validate_upload(fs(b"MZ....", "virus.exe"), POLICY)
    assert "not allowed" in validate_upload(fs(b"<?php", "shell.php"), POLICY)


def test_fake_extension_rejected():
    assert "valid .pdf" in validate_upload(fs(b"this is not a pdf", "fake.pdf"), POLICY)


def test_oversize_and_empty_rejected():
    assert "limit" in validate_upload(fs(b"%PDF" + b"x" * 2000, "big.pdf"), POLICY)
    assert "empty" in validate_upload(fs(b"", "empty.txt"), POLICY)


def test_traversal_filename_is_sanitised(app, data):
    import pytest
    from app.services import ValidationError
    with pytest.raises(ValidationError):
        complaint_service().submit(data.student, data.cat.id, "Upload test", "Description is long enough",
                                   "Low", [fs(b"x", "../../etc/passwd")])


def test_dashboard_statistics_are_real(app, data):
    svc = complaint_service()
    a = svc.submit(data.student, data.cat.id, "First complaint", "First description text", "High")
    b = svc.submit(data.student, data.cat2.id, "Second complaint", "Second description text", "Low")
    svc.submit(data.student2, data.cat.id, "Third complaint", "Third description text", "Low")
    svc.assign(a.id, data.staff.id, data.admin)
    svc.change_status(a.id, "In Progress", data.staff)
    stats = stats_service()
    admin = stats.admin_dashboard()
    assert admin["total"] == 3 and admin["pending"] == 2 and admin["in_progress"] == 1
    assert admin["priority"]["High"] == 1 and admin["priority"]["Low"] == 2
    assert admin["category"]["IT"] == 2 and admin["category"]["Facilities"] == 1
    assert sum(m["count"] for m in admin["trend"]) == 3
    s1 = stats.student_dashboard(data.student.id)
    assert s1["total"] == 2 and s1["pending"] == 1 and s1["in_progress"] == 1
    assert stats.student_dashboard(data.student2.id)["total"] == 1
    st = stats.staff_dashboard(data.staff.id)
    assert st["assigned"] == 1 and st["active"] == 1 and st["resolved_total"] == 0
    assert stats.staff_dashboard(data.staff2.id)["assigned"] == 0


def test_overdue_detection(app, data):
    from datetime import timedelta
    from app.extensions import db
    from app.utils.helpers import utcnow
    c = complaint_service().submit(data.student, data.cat.id, "Old complaint", "Old description text", "Low")
    assert stats_service().admin_dashboard()["overdue"] == 0
    c.created_at = utcnow() - timedelta(days=10)
    db.session.commit()
    assert stats_service().admin_dashboard()["overdue"] == 1
    assert c.is_overdue(7)


def test_dashboard_pages_render_real_numbers(make_client, data, complaint):
    r = make_client("admin@t.edu").get("/admin/dashboard")
    assert r.status_code == 200 and b"Total complaints" in r.data
    assert make_client("stu@t.edu").get("/student/dashboard").status_code == 200
    assert make_client("staff@t.edu").get("/staff/dashboard").status_code == 200


def test_seed_command(app):
    from app.models import Complaint, User
    from app.utils.seed import seed_dev_data
    seed_dev_data()
    assert User.query.filter_by(role="admin").count() == 1
    assert User.query.filter_by(role="staff").count() == 3
    assert User.query.filter_by(role="student").count() == 5
    assert Complaint.query.count() == 20
