from app.extensions import db
import pytest

from app.models import Complaint, ComplaintHistory, Notification
from app.services import InvalidTransition, PermissionDenied, ValidationError
from app.services.factory import complaint_service

from .conftest import complaint_payload, pdf_file


def test_student_submits_complaint_via_route(make_client, data):
    c = make_client("stu@t.edu")
    r = c.post("/student/complaints/new", data=complaint_payload(data.cat.id))
    assert r.status_code == 302
    cm = Complaint.query.one()
    assert cm.status == "Pending" and cm.student_id == data.student.id
    assert cm.complaint_number.startswith("UCM-")
    assert Notification.query.filter_by(user_id=data.admin.id).count() == 1


@pytest.mark.parametrize("override", [{"title": "abc"}, {"description": "short"}, {"priority": "Bogus"},
                                      {"category_id": 999}])
def test_invalid_complaint_data_rejected(app, data, override):
    kw = complaint_payload(data.cat.id, **override)
    with pytest.raises(ValidationError):
        complaint_service().submit(data.student, kw["category_id"], kw["title"], kw["description"], kw["priority"])
    assert Complaint.query.count() == 0


def test_invalid_form_not_saved(make_client, data):
    c = make_client("stu@t.edu")
    r = c.post("/student/complaints/new", data=complaint_payload(data.cat.id, title="x"))
    assert r.status_code == 200 and Complaint.query.count() == 0


def test_full_workflow_and_history(app, data, complaint):
    svc = complaint_service()
    svc.assign(complaint.id, data.staff.id, data.admin)
    assert complaint.status == "Assigned" and complaint.assigned_staff_id == data.staff.id
    svc.change_status(complaint.id, "In Progress", data.staff)
    svc.change_status(complaint.id, "Resolved", data.staff, "Replaced the lamp")
    assert complaint.resolved_at is not None and complaint.resolution_notes == "Replaced the lamp"
    svc.change_status(complaint.id, "Closed", data.admin)
    steps = [h.new_status for h in ComplaintHistory.query.filter_by(complaint_id=complaint.id).order_by(ComplaintHistory.id)]
    assert steps == ["Pending", "Assigned", "In Progress", "Resolved", "Closed"]
    # student was notified of progress
    assert Notification.query.filter_by(user_id=data.student.id).count() >= 4


def test_invalid_transitions_blocked(app, data, complaint):
    svc = complaint_service()
    with pytest.raises(InvalidTransition):
        svc.change_status(complaint.id, "Resolved", data.admin)            # Pending -> Resolved
    svc.assign(complaint.id, data.staff.id, data.admin)
    with pytest.raises(InvalidTransition):
        svc.change_status(complaint.id, "Closed", data.admin)              # Assigned -> Closed
    with pytest.raises(InvalidTransition):
        svc.change_status(complaint.id, "In Progress", data.admin)         # only staff may start work
    with pytest.raises(PermissionDenied):
        svc.change_status(complaint.id, "In Progress", data.staff2)        # not the assigned staff


def test_resolution_note_required(app, data, complaint):
    svc = complaint_service()
    svc.assign(complaint.id, data.staff.id, data.admin)
    svc.change_status(complaint.id, "In Progress", data.staff)
    with pytest.raises(ValidationError):
        svc.change_status(complaint.id, "Resolved", data.staff, "  ")


def test_close_and_reopen(app, data, complaint):
    svc = complaint_service()
    svc.assign(complaint.id, data.staff.id, data.admin)
    svc.change_status(complaint.id, "In Progress", data.staff)
    svc.change_status(complaint.id, "Resolved", data.staff, "Fixed")
    with pytest.raises(ValidationError):                                    # reason required
        svc.change_status(complaint.id, "Reopened", data.student, "")
    svc.change_status(complaint.id, "Reopened", data.student, "Still broken")
    assert complaint.status == "Reopened" and complaint.resolved_at is None
    svc.change_status(complaint.id, "In Progress", data.staff)
    svc.change_status(complaint.id, "Resolved", data.staff, "Really fixed")
    svc.change_status(complaint.id, "Closed", data.admin)
    svc.change_status(complaint.id, "Reopened", data.admin, "Audit found issue")
    assert complaint.status == "Reopened"


def test_assign_requires_admin_and_active_staff(app, data, complaint):
    svc = complaint_service()
    with pytest.raises(PermissionDenied):
        svc.assign(complaint.id, data.staff.id, data.student)
    with pytest.raises(ValidationError):
        svc.assign(complaint.id, data.student.id, data.admin)               # not a staff member


def test_assignment_via_route(make_client, data, complaint):
    c = make_client("admin@t.edu")
    r = c.post(f"/complaints/{complaint.id}/assign", data={"staff_id": data.staff.id})
    assert r.status_code == 302
    assert db.session.get(Complaint, complaint.id).status == "Assigned"
    assert Notification.query.filter_by(user_id=data.staff.id).count() == 1


def test_student_edit_only_while_pending_unassigned(app, data, complaint):
    svc = complaint_service()
    svc.update_pending(complaint.id, data.student, data.cat2.id, "Updated title", "Updated description text", "Low")
    assert complaint.title == "Updated title"
    svc.assign(complaint.id, data.staff.id, data.admin)
    with pytest.raises(InvalidTransition):
        svc.update_pending(complaint.id, data.student, data.cat.id, "Another title", "Another description", "Low")


def test_comments_and_notifications(app, data, complaint):
    svc = complaint_service()
    svc.assign(complaint.id, data.staff.id, data.admin)
    svc.add_comment(complaint.id, data.staff, "We are on it")
    assert Notification.query.filter_by(user_id=data.student.id, title="New response").count() == 1
    svc.add_comment(complaint.id, data.student, "Thank you")
    assert Notification.query.filter_by(user_id=data.staff.id, title="New student comment").count() == 1
    with pytest.raises(PermissionDenied):
        svc.add_comment(complaint.id, data.staff2, "intruder")


def test_attachment_upload_and_download(make_client, data, tmp_path):
    c = make_client("stu@t.edu")
    payload = complaint_payload(data.cat.id)
    payload["attachments"] = [pdf_file()]
    r = c.post("/student/complaints/new", data=payload, content_type="multipart/form-data")
    assert r.status_code == 302
    cm = Complaint.query.one()
    assert len(cm.attachments) == 1
    assert c.get(f"/attachments/{cm.attachments[0].id}").status_code == 200
    # another student must not download it
    other = make_client("stu2@t.edu")
    assert other.get(f"/attachments/{cm.attachments[0].id}").status_code == 403
