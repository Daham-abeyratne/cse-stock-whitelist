from datetime import datetime, date, timedelta, timezone

# Sri Lanka is UTC +05:30 (no DST)
SL_TZ = timezone(timedelta(hours=5, minutes=30), name="Asia/Colombo")

def today_colombo() -> date:
    """Return today's date in Sri Lanka (UTC+05:30)."""
    return datetime.now(SL_TZ).date()

def iso(d: date) -> str:
    """Convert a date to ISO-8601 string."""
    return d.isoformat()

def parse_iso_date(s: str) -> date:
    """Parse an ISO-8601 date string (YYYY-MM-DD)."""
    return date.fromisoformat(s)
