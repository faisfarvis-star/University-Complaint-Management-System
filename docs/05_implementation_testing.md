# Implementation and testing

## Implementation notes
- **Security:** `werkzeug` password hashes; `CSRFProtect` on every POST (logout is POST-only);
  `roles_required` decorator plus ownership checks in `ComplaintService.get_for_user`; Jinja
  auto-escaping; SQLAlchemy parameterised queries; session cookies are HttpOnly + SameSite=Lax
  (Secure via `SESSION_COOKIE_SECURE=1` behind HTTPS); `SECRET_KEY` from the environment.
- **Uploads:** extension allow-list, 5 MB limit, file-signature check, random stored names,
  stored outside `static/`, downloads only through `/attachments/<id>` after a complaint permission check.
- **CSV export:** cells starting with `= + - @` are prefixed to block spreadsheet formula injection.
- **Open redirects** on `?next=` are rejected.

## Testing
Run: `python -m pytest -q`. Tests use a temporary SQLite file per test and never touch `instance/ucms.db`.

| File | Covers |
|------|--------|
| `test_auth.py` | registration, role cannot be chosen, duplicate email, login/logout, invalid login, deactivated account, guest redirect, open-redirect block |
| `test_complaints.py` | submission, invalid data, assignment, status updates, history, close/reopen, invalid transitions, comments + notifications, attachment upload/download |
| `test_permissions.py` | student/staff/admin restrictions, account and category management, CSV, error pages |
| `test_repositories.py` | repository CRUD, interface conformance, mock repository replacing the real one |
| `test_uploads_and_stats.py` | upload validation, dashboard statistics, overdue detection, seed command |

**Recorded result (this build, Python 3.12.3, Flask 3.1.3):** `48 passed` in about 21 s.
The same environment also confirmed a live server start, `init-db`, `seed`, CSRF rejection (HTTP 400 without a token) and a successful admin login.
Screenshots have **not** been captured in this environment – see the placeholders in the report.
