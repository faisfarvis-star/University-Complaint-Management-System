"""View-layer helpers: template filters, globals and context processors."""
from flask import current_app
from flask_login import current_user

from ..repositories.implementations import SqlAlchemyNotificationRepository
from ..utils import constants as C

STATUS_CLASS = {C.PENDING: "warning", C.ASSIGNED: "info", C.IN_PROGRESS: "primary",
                C.RESOLVED: "success", C.CLOSED: "secondary", C.REOPENED: "danger"}
PRIORITY_CLASS = {"Low": "secondary", "Medium": "info", "High": "warning", "Urgent": "danger"}


def register_view_helpers(app):
    @app.template_filter("dt")
    def fmt_dt(value, fmt="%d %b %Y, %H:%M"):
        return value.strftime(fmt) if value else "—"

    @app.template_filter("status_class")
    def status_class(status):
        return STATUS_CLASS.get(status, "secondary")

    @app.template_filter("priority_class")
    def priority_class(priority):
        return PRIORITY_CLASS.get(priority, "secondary")

    @app.context_processor
    def inject_globals():
        unread = 0
        if current_user.is_authenticated:
            unread = SqlAlchemyNotificationRepository().unread_count(current_user.id)
        return {"unread_count": unread, "STATUSES": C.STATUSES, "PRIORITIES": C.PRIORITIES,
                "overdue_days": current_app.config["OVERDUE_DAYS"]}
