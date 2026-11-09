# CA-05 Report Draft – University Complaint Management System

> Adjust headings to match the university's official CA-05 template if it differs.

**Student:** ________  **Reg. No.:** ________  **Batch:** ________  **Date:** ________

## 1. Introduction
(Summarise the system – see `01_project_overview.md`.)

## 2. Problem statement and objectives
(Copy from `01_project_overview.md`.)

## 3. Selected architecture: MVC
Justification: clear separation of data (models), presentation (templates) and request handling
(controllers) suits a form-driven web app and maps directly to Flask. Diagram: `diagrams/mvc_architecture.mmd`.
Evidence in the project: `app/models`, `app/templates`, `app/controllers`.

## 4. Selected design pattern: Repository
Justification: isolates persistence so business rules are testable and storage can change.
UML: `diagrams/repository_uml.mmd`. Evidence: `app/repositories/*`, unit test with a mock repository.

## 5. System design
5.1 Use cases and roles · 5.2 ER diagram (`er_diagram.mmd`) · 5.3 Workflow (`workflow.mmd`).
Render the `.mmd` files at https://mermaid.live and paste the images here.

## 6. Implementation
Technology stack, folder structure, security measures, key screens (see `05_implementation_testing.md`).

## 7. Testing
Test strategy and the recorded result: 48 tests passed (pytest). Add your own re-run output.

## 8. Screenshots
- [SCREENSHOT PLACEHOLDER – Login page]
- [SCREENSHOT PLACEHOLDER – Student dashboard]
- [SCREENSHOT PLACEHOLDER – Submit complaint form]
- [SCREENSHOT PLACEHOLDER – Admin dashboard with charts]
- [SCREENSHOT PLACEHOLDER – Assign complaint]
- [SCREENSHOT PLACEHOLDER – Staff update/resolve]
- [SCREENSHOT PLACEHOLDER – Complaint history timeline]
- [SCREENSHOT PLACEHOLDER – Mobile view with sidebar]
- [SCREENSHOT PLACEHOLDER – pytest output]

## 9. Conclusion and future improvements
(See `01_project_overview.md` §6.)

## 10. References
Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Bootstrap 5, Chart.js documentation; Fowler, *Patterns of Enterprise Application Architecture* (Repository).
