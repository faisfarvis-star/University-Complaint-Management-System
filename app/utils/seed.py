"""Development seed data. All people and complaints are fictional."""
import random
from datetime import timedelta

from ..extensions import db
from ..models import Category, Complaint, ComplaintHistory, Notification, User
from ..utils import constants as C
from ..utils.helpers import utcnow

# Development-only credentials (documented in docs/DEV_CREDENTIALS.md). Not for production.
DEV_PASSWORDS = {"admin": "Admin@12345", "staff": "Staff@12345", "student": "Student@12345"}

CATEGORIES = [
    ("Academic", "Lectures, exams, grading and course content"),
    ("Facilities", "Classrooms, labs, library and buildings"),
    ("IT Services", "Wi-Fi, portals, computers and software"),
    ("Finance", "Fees, payments and scholarships"),
    ("Hostel & Transport", "Accommodation and campus transport"),
    ("Administration", "Records, registration and documents"),
]
STAFF = [("Nadeesha Perera", "Facilities"), ("Kasun Fernando", "IT Services"), ("Ishara Silva", "Academic Affairs")]
STUDENTS = [("Amal Jayasuriya", "HDIT"), ("Dilini Rathnayake", "HDBM"), ("Tharindu Weerasinghe", "HDIT"),
            ("Sanduni Gunawardena", "HDAE"), ("Ruwan Bandara", "HDBM")]
TITLES = [
    ("Wi-Fi is down in Block B", 2), ("Projector not working in Lab 3", 1), ("Exam result discrepancy", 0),
    ("Library AC not working", 1), ("Fee payment not reflected", 3), ("Hostel water supply issue", 4),
    ("Student portal login error", 2), ("Broken chairs in Lecture Hall 2", 1), ("Missing attendance records", 5),
    ("Shuttle bus delay every morning", 4), ("Lab computers running very slowly", 2), ("Scholarship letter delay", 3),
    ("Noise during exam hours", 1), ("Transcript request not processed", 5), ("Printer unavailable in library", 2),
    ("Lecture slides not uploaded", 0), ("Cafeteria hygiene concern", 1), ("Wrong course in timetable", 5),
    ("Receipt not issued for payment", 3), ("Leaking roof in Block C", 1),
]
STATUS_PLAN = ([C.PENDING] * 5 + [C.ASSIGNED] * 3 + [C.IN_PROGRESS] * 4 + [C.RESOLVED] * 3
               + [C.CLOSED] * 4 + [C.REOPENED])
PATHS = {
    C.PENDING: [], C.ASSIGNED: [C.ASSIGNED], C.IN_PROGRESS: [C.ASSIGNED, C.IN_PROGRESS],
    C.RESOLVED: [C.ASSIGNED, C.IN_PROGRESS, C.RESOLVED],
    C.CLOSED: [C.ASSIGNED, C.IN_PROGRESS, C.RESOLVED, C.CLOSED],
    C.REOPENED: [C.ASSIGNED, C.IN_PROGRESS, C.RESOLVED, C.REOPENED],
}


def _user(name, email, role, dept=None, reg=None):
    u = User(full_name=name, email=email, role=role, department=dept, registration_number=reg)
    u.set_password(DEV_PASSWORDS[role])
    db.session.add(u)
    return u


def seed_dev_data():
    if User.query.filter_by(email="admin@ucms-demo.edu").first():
        return "Seed data already present (use --reset to start over)."
    rng = random.Random(42)
    now = utcnow()

    admin = _user("Admin User", "admin@ucms-demo.edu", "admin", "Administration")
    staff = [_user(n, f"staff{i + 1}@ucms-demo.edu", "staff", d) for i, (n, d) in enumerate(STAFF)]
    students = [_user(n, f"student{i + 1}@ucms-demo.edu", "student", d, f"0324{1000 + i}")
                for i, (n, d) in enumerate(STUDENTS)]
    cats = [Category(name=n, description=d) for n, d in CATEGORIES]
    db.session.add_all(cats)
    db.session.flush()

    for i, ((title, cat_idx), status) in enumerate(zip(TITLES, STATUS_PLAN)):
        created = now - timedelta(days=rng.randint(1, 160), hours=rng.randint(0, 20))
        if status == C.PENDING and i % 2 == 0:
            created = now - timedelta(days=rng.randint(9, 20))      # overdue examples
        student = students[i % len(students)]
        worker = staff[i % len(staff)] if PATHS[status] else None
        c = Complaint(
            complaint_number=f"UCM-{now.year}-{i + 1:04d}", student_id=student.id,
            assigned_staff_id=worker.id if worker else None,
            category_id=cats[cat_idx % len(cats)].id, title=title,
            description=f"{title}. This has been affecting students for several days and needs attention.",
            priority=C.PRIORITIES[i % 4], status=status, created_at=created, updated_at=created)
        db.session.add(c)
        db.session.flush()
        db.session.add(ComplaintHistory(complaint_id=c.id, changed_by=student.id, old_status=None,
                                        new_status=C.PENDING, remarks="Complaint submitted", created_at=created))
        previous, stamp = C.PENDING, created
        for step in PATHS[status]:
            stamp += timedelta(hours=rng.randint(4, 30))
            actor = admin if step in (C.ASSIGNED, C.CLOSED) else (student if step == C.REOPENED else worker)
            remark = {C.ASSIGNED: f"Assigned to {worker.full_name}", C.RESOLVED: "Issue fixed and verified.",
                      C.REOPENED: "Problem occurred again.", C.IN_PROGRESS: "Work started.",
                      C.CLOSED: "Resolution verified."}[step]
            db.session.add(ComplaintHistory(complaint_id=c.id, changed_by=actor.id, old_status=previous,
                                            new_status=step, remarks=remark, created_at=stamp))
            previous = step
            if step == C.RESOLVED:
                c.resolved_at, c.resolution_notes = stamp, "Issue fixed and verified."
        if status == C.REOPENED:
            c.resolved_at = None
        c.updated_at = stamp
        db.session.add(Notification(user_id=student.id, complaint_id=c.id, title=f"Complaint {status.lower()}",
                                    message=f"{c.complaint_number} is now '{status}'.", is_read=i % 3 == 0,
                                    created_at=stamp))
        if worker:
            db.session.add(Notification(user_id=worker.id, complaint_id=c.id, title="New assignment",
                                        message=f"{c.complaint_number} was assigned to you.", is_read=i % 2 == 0,
                                        created_at=created + timedelta(hours=5)))
        if status == C.PENDING:
            db.session.add(Notification(user_id=admin.id, complaint_id=c.id, title="New complaint",
                                        message=f"{c.complaint_number}: {title}", created_at=created))
    db.session.commit()
    return "Seeded 1 admin, 3 staff, 5 students, 6 categories and 20 complaints."
