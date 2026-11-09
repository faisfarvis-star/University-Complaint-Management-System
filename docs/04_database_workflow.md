# Database design and workflow

ER diagram: `diagrams/er_diagram.mmd`. Workflow diagram: `diagrams/workflow.mmd`.

Tables: `users`, `complaints`, `categories`, `complaint_history`, `complaint_comments`,
`notifications`, `attachments`, `audit_logs`. Added beyond the brief: `complaints.resolution_notes`
and `notifications.complaint_id` (to link a notification to its complaint).
Constraints: unique `users.email`, `users.registration_number`, `complaints.complaint_number`,
`categories.name`, `attachments.stored_filename`; foreign keys on all relations; indexes on
complaint student, staff, status and created date, history complaint id, and notification user/read.

## Workflow rules (single source: `TRANSITIONS` in `app/utils/constants.py`)
| From | To | Allowed role |
|------|----|--------------|
| Pending, Reopened | Assigned | Admin (assignment action; Assigned can also be reassigned) |
| Assigned, Reopened | In Progress | Assigned staff |
| In Progress | Resolved | Assigned staff (note required) |
| Resolved | Closed | Admin |
| Resolved | Reopened | Admin or owning student (reason required) |
| Closed | Reopened | Admin (reason required) |
Every change writes a `complaint_history` row and an `audit_logs` row.
