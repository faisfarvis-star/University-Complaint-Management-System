# University Complaint Management System (CA-05)

## 1. Project overview
A web application where students submit complaints, administrators triage and assign them, and staff
resolve them. Every action is stored in SQLite, recorded in a status history and surfaced as in-app
notifications. Selected architecture: **MVC**. Selected design pattern: **Repository**.

## 2. Problem statement
Complaints at universities are often raised by email, phone or paper. They get lost, nobody knows who
owns them, students cannot see progress and management has no statistics. A single system with a
clear workflow, ownership and history removes these problems.

## 3. Objectives
1. Let students submit and track complaints with evidence attachments.
2. Give administrators one place to filter, assign, verify, report and audit.
3. Give staff a focused view of only their assigned complaints.
4. Enforce the workflow and access rules on the server.
5. Provide dashboards built from live database data.
6. Demonstrate one architecture (MVC) and one design pattern (Repository) in real code.

## 4. Functional requirements
| Role | Capabilities |
|------|--------------|
| Student | Register, log in/out, dashboard, submit complaint (category, title, description, priority, attachments), list/track, history, read responses, follow-up comments, edit while Pending and unassigned, notifications, profile |
| Admin | Dashboard with charts, all complaints with filters/search, assign/reassign, update status (close/reopen), manage students/staff/categories, overdue view, CSV report, audit logs, send updates to students |
| Staff | Dashboard, assigned complaints only, start work, resolve with note, completed list, respond to students, notifications, personal performance |

## 5. Non-functional requirements
- **Security:** password hashing, CSRF, role-based access, server-side validation, upload restrictions, secure cookies, safe error pages.
- **Usability:** responsive dashboard, accessible contrast, keyboard focus styles, skip link, ARIA labels.
- **Maintainability:** MVC folders, thin controllers, repositories behind interfaces.
- **Testability:** services accept repositories, so they run without a database (see unit test with a mock repository).
- **Portability:** Python + SQLite only; runs from a ZIP with `pip install -r requirements.txt`.

## 6. Future improvements
Email/SMS notifications, SLA timers per priority, pagination for very large lists, Flask-Migrate
versioned migrations, PDF reports, multi-language UI, department-based auto-assignment.
