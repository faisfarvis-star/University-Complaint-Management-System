from datetime import datetime

from flask import current_app

from ..utils.constants import PRIORITIES, STATUSES


def _date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except (TypeError, ValueError):
        return None


def read_filters(args):
    """Parse and sanitise list filters from a query string."""
    f = {}
    q = (args.get("q") or "").strip()
    if q:
        f["q"] = q[:100]
    if args.get("category_id", "").isdigit():
        f["category_id"] = int(args["category_id"])
    if args.get("priority") in PRIORITIES:
        f["priority"] = args["priority"]
    if args.get("status") in STATUSES:
        f["status"] = args["status"]
    if _date(args.get("date_from")):
        f["date_from"] = _date(args["date_from"])
    if _date(args.get("date_to")):
        f["date_to"] = _date(args["date_to"])
    if args.get("overdue") == "1":
        f["overdue"] = True
        f["overdue_days"] = current_app.config["OVERDUE_DAYS"]
    return f
