from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import require_admin
from app.services.analytics import bar_chart, dashboard_stats

from .common import render_admin

router = APIRouter(prefix="/admin", dependencies=[Depends(require_admin)])


@router.get("")
def dashboard(request: Request, days: str = "30", db: Session = Depends(get_db)):
    period = {"7": 7, "30": 30, "90": 90, "all": None}.get(days, 30)
    stats = dashboard_stats(db, period)
    charts = {
        "orders": bar_chart(stats["orders_series"], stats["labels"]),
        "revenue": bar_chart(stats["revenue_series"], stats["labels"], decimals=0),
        "visitors": bar_chart(stats["visitors_series"], stats["labels"]),
    }
    return render_admin(request, db, "admin/dashboard.html", st=stats, charts=charts,
                        days=days if days in ("7", "30", "90", "all") else "30")
