# MVC architecture

The one selected architecture is **Model–View–Controller**. Diagram: `diagrams/mvc_architecture.mmd`.

| Part | Responsibility | Where in the code |
|------|----------------|-------------------|
| **Model** | Entities, relationships, constraints | `app/models/` (User, Complaint, Category, ComplaintHistory, ComplaintComment, Notification, Attachment, AuditLog) |
| **View** | What the user sees | `app/templates/` (Jinja2), `app/static/` (CSS/JS), `app/views/` (template filters and context helpers) |
| **Controller** | HTTP handling, validation of the request, permission gate, choosing the response | `app/controllers/` – `auth`, `main`, `student`, `admin`, `staff` blueprints |

Controllers stay thin. They parse the request (Flask-WTF forms in `app/forms/`), call an application
service, and render a template or redirect. Business rules (allowed transitions, who may assign,
notifications) live in `app/services/`. These services are plumbing *inside* the controller/model
side of MVC – they are not a second architecture. The only data-access abstraction is the Repository
pattern (next document).

Example request: *admin assigns a complaint*
1. `POST /complaints/7/assign` → `main.assign` (controller) checks role and validates the form.
2. Calls `ComplaintService.assign()` which applies the rules.
3. The service uses `ComplaintRepository`, `UserRepository`, `NotificationRepository`, `ComplaintHistoryRepository`.
4. Controller redirects; the complaint page is rendered by `shared/complaint_detail.html`.
