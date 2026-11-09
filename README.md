# University Complaint Management System (CA-05)

Flask · MVC architecture · Repository design pattern · SQLite · Bootstrap 5 · Chart.js · pytest

Roles: **student** (submit/track), **admin** (triage, assign, manage, report, audit), **staff** (resolve assigned complaints).

## Install (Python 3.11+)
```bash
unzip University_Complaint_Management_System_CA05.zip && cd university-complaint-management
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env  (then set SECRET_KEY)
```

## Initialise and run
```bash
flask --app run init-db            # create tables
flask --app run seed               # fictional demo data (1 admin, 3 staff, 5 students, 20 complaints)
flask --app run run                # http://127.0.0.1:5000
```
Reset demo data: `flask --app run seed --reset`. Create a real admin: `flask --app run create-admin`.
Demo logins: see `docs/DEV_CREDENTIALS.md` (e.g. `admin@ucms-demo.edu` / `Admin@12345`).

## Tests
```bash
python -m pytest -q
```
Tests use a temporary database; the development database is never modified.

## Structure
```
app/models/        MODEL        entities and relationships
app/templates/     VIEW         Jinja2 templates (+ app/static, app/views helpers)
app/controllers/   CONTROLLER   thin HTTP handlers (auth, main, student, admin, staff)
app/services/      business rules (workflow, permissions, notifications, stats)
app/repositories/  REPOSITORY   interfaces/ + implementations/ (SQLAlchemy)
app/forms/         Flask-WTF forms
tests/  docs/  migrations/  config.py  run.py
```
Notes: "In progress" on dashboards counts Assigned + In Progress + Reopened. Charts and icons load from a CDN, so the
first page view needs internet access. Documentation, Mermaid diagrams, the CA-05 report draft and the presentation outline are in `docs/`.
