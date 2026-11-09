import csv
import io

HEADERS = ["Complaint No", "Title", "Student", "Registration No", "Category", "Priority",
           "Status", "Assigned Staff", "Created", "Resolved"]


def _safe(value):
    """Neutralise spreadsheet formula injection."""
    text = "" if value is None else str(value)
    return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text


def complaints_csv(complaints):
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(HEADERS)
    for c in complaints:
        writer.writerow([_safe(v) for v in [
            c.complaint_number, c.title, c.student.full_name, c.student.registration_number,
            c.category.name, c.priority, c.status,
            c.assigned_staff.full_name if c.assigned_staff else "",
            c.created_at.strftime("%Y-%m-%d %H:%M"),
            c.resolved_at.strftime("%Y-%m-%d %H:%M") if c.resolved_at else ""]])
    return buf.getvalue()
