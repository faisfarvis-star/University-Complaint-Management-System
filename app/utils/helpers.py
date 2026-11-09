from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin

from flask import request


def utcnow():
    """Naive UTC timestamp (keeps SQLite handling simple)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_safe_url(target):
    """Only allow redirects to the same host (prevents open redirects)."""
    if not target:
        return False
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc
