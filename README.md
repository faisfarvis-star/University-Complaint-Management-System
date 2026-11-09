# University Complaint Management System (CA-05)

Flask · MVC architecture · Repository design pattern · SQLite · Bootstrap 5 grid · Lucide icons · Chart.js · pytest

**UI: CampusFlow design system (V2)** – see [CampusFlow UI](#campusflow-ui-v2) below.

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
Notes: "In progress" on dashboards counts Assigned + In Progress + Reopened. Charts, icons (Lucide), Bootstrap and the Plus Jakarta Sans font load from a CDN, so the
first page view needs internet access. Documentation, Mermaid diagrams, the CA-05 report draft and the presentation outline are in `docs/`.

## CampusFlow UI (V2)
The V2 release is a **view-layer-only** redesign. Controllers, services, repositories, models, routes, forms, CSRF handling and
permissions are unchanged, so the CA-05 MVC + Repository Pattern documentation in `docs/` still applies as written.

**Design system** (`app/static/css/style.css`, one token-driven file): CSS variables for the palette (primary `#6366F1`, secondary `#8B5CF6`,
accent `#06B6D4`, success/warning/danger), Plus Jakarta Sans typography, glassmorphism for chrome (sidebar, topbar, dropdowns, dialogs, login card)
and soft neumorphism for cards, stat tiles, buttons and inputs. Button and link text uses `#4F46E5` (a darker shade of the primary) to keep AA contrast.

**Themes:** light and dark. The saved choice lives in `localStorage` (`campusflow-theme`); first visit follows the OS setting. The theme is applied by a small
inline script in `<head>` to avoid a flash. Charts re-colour when the theme changes.

**Responsive behaviour:** desktop (>=1024px) fixed sidebar that can collapse (state remembered); tablet (768-1023px) compact icon rail;
mobile (<768px) off-canvas sidebar with overlay (Esc closes it, hidden from keyboard/AT while closed). Tables become stacked cards below 768px.

**Reusable Jinja components** (`app/templates/components/`): `_sidebar.html`, `_topbar.html`, `_flash.html` (toasts), and macros in `_macros.html`:
`stat`, `status_badge`, `priority_badge`, `active_badge`, `button`, `confirm_button`, `field`, `password_field`, `empty_state`, `notification_card`, `avatar`, `icon`.
Status colours: Pending amber, Assigned blue, In Progress purple, Resolved green, Closed slate, Reopened orange (text label always shown).

**Behaviour notes**
- Dashboards show only real database values; charts show an empty state when there is no data.
- The backend has no server-side pagination. Long tables use client-side paging (`data-paginate`); server-side filters are unchanged.
- The top-bar bell links to the notification page with the real unread count (no dropdown list, to avoid new backend queries).
- Confirmations use a native `<dialog>`; submit buttons show a spinner. `prefers-reduced-motion` is honoured.
- JavaScript: `static/js/app.js` (shell), `static/js/charts.js` (admin charts, data passed as JSON from the server).

**UI testing status:** see "Testing results" in the delivery notes. Templates were render-tested offline with stub data; the full pytest suite and
browser checks must be run in a normal environment (`pip install -r requirements.txt && python -m pytest -q`).
