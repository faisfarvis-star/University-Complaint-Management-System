from ..utils.constants import (ACTIVE_STATUSES, ASSIGNED, CLOSED, FINAL_STATUSES, IN_PROGRESS,
                               PENDING, REOPENED, RESOLVED, ROLE_STAFF, ROLE_STUDENT)


def _buckets(by_status):
    return {
        "total": sum(by_status.values()),
        "pending": by_status[PENDING],
        "in_progress": sum(by_status[s] for s in ACTIVE_STATUSES),
        "resolved": by_status[RESOLVED],
        "closed": by_status[CLOSED],
    }


class StatsService:
    def __init__(self, complaints, users, overdue_days=7):
        self.complaints = complaints
        self.users = users
        self.overdue_days = overdue_days

    def admin_dashboard(self):
        data = _buckets(self.complaints.count_by_status())
        data.update({
            "overdue": len(self.complaints.list_overdue(self.overdue_days)),
            "priority": self.complaints.count_by_priority(),
            "category": self.complaints.count_by_category(),
            "trend": self.complaints.monthly_trend(6),
            "recent": self.complaints.recent(6),
            "staff_performance": self.complaints.staff_performance(),
            "students": self.users.count_by_role(ROLE_STUDENT),
            "staff": self.users.count_by_role(ROLE_STAFF),
        })
        return data

    def student_dashboard(self, student_id):
        data = _buckets(self.complaints.count_by_status(student_id=student_id))
        data["recent"] = self.complaints.recent(5, student_id=student_id)
        return data

    def staff_dashboard(self, staff_id):
        by_status = self.complaints.count_by_status(staff_id=staff_id)
        data = _buckets(by_status)
        mine = next((p for p in self.complaints.staff_performance() if p["staff_id"] == staff_id), None)
        data.update({
            "assigned": data["total"],
            "active": data["in_progress"],
            "resolved_total": by_status[RESOLVED] + by_status[CLOSED],
            "to_start": by_status[ASSIGNED] + by_status[REOPENED],
            "recent": self.complaints.recent(5, staff_id=staff_id),
            "rate": mine["rate"] if mine else 0,
            "avg_hours": mine["avg_hours"] if mine else None,
        })
        return data
