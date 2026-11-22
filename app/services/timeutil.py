from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.config import TIMEZONE

_tz = ZoneInfo(TIMEZONE)


def now_local() -> datetime:
    """Naive datetime in Bahrain time (what we store in the DB)."""
    return datetime.now(_tz).replace(tzinfo=None)


def today_local() -> date:
    return now_local().date()
