from datetime import datetime, date, timedelta, timezone

# Sri Lanka is UTC +05:30 (no DST)
SL_TZ = timezone(timedelta(hours=5, minutes=30))

def today_colombo() -> date:
    return datetime.now(SL_TZ).date()

def iso(d: date) -> str:
    return d.isoformat()

def parse_iso_date(s: str) -> date:
    return date.fromisoformat(s)
