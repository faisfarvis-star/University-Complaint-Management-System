ROLE_STUDENT, ROLE_ADMIN, ROLE_STAFF = "student", "admin", "staff"

PENDING, ASSIGNED, IN_PROGRESS = "Pending", "Assigned", "In Progress"
RESOLVED, CLOSED, REOPENED = "Resolved", "Closed", "Reopened"
STATUSES = [PENDING, ASSIGNED, IN_PROGRESS, RESOLVED, CLOSED, REOPENED]
ACTIVE_STATUSES = (ASSIGNED, IN_PROGRESS, REOPENED)   # "in progress" bucket on dashboards
FINAL_STATUSES = (RESOLVED, CLOSED)

PRIORITIES = ["Low", "Medium", "High", "Urgent"]

# (old status, new status) -> roles allowed to perform the transition.
# Server-side single source of truth for the complaint workflow.
TRANSITIONS = {
    (PENDING, ASSIGNED): {ROLE_ADMIN},
    (REOPENED, ASSIGNED): {ROLE_ADMIN},
    (ASSIGNED, IN_PROGRESS): {ROLE_STAFF},
    (REOPENED, IN_PROGRESS): {ROLE_STAFF},
    (IN_PROGRESS, RESOLVED): {ROLE_STAFF},
    (RESOLVED, CLOSED): {ROLE_ADMIN},
    (RESOLVED, REOPENED): {ROLE_ADMIN, ROLE_STUDENT},
    (CLOSED, REOPENED): {ROLE_ADMIN},
}
