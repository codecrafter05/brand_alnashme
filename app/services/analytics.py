from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from markupsafe import Markup, escape
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Order, Visit
from app.services.pricing import D
from app.services.timeutil import now_local, today_local

COUNTED = ("confirmed", "delivered")


def dashboard_stats(db: Session, days: int | None):
    today = today_local()
    start = today - timedelta(days=days - 1) if days else None
    chart_days = min(days or 30, 30)
    chart_start = today - timedelta(days=chart_days - 1)

    oq = db.query(Order)
    vq = db.query(Visit)
    if start:
        oq = oq.filter(Order.created_at >= start)
        vq = vq.filter(Visit.day >= start)
    orders = oq.all()

    live = [o for o in orders if o.status != "cancelled"]
    counted = [o for o in orders if o.status in COUNTED]
    revenue = sum((D(o.total) for o in counted), Decimal("0"))
    fees = sum((D(o.delivery_fee) for o in counted), Decimal("0"))
    pending = [o for o in orders if o.status == "new"]
    pending_value = sum((D(o.total) for o in pending), Decimal("0"))

    visitors = vq.with_entities(func.count(func.distinct(Visit.visitor_id))).scalar() or 0
    views = vq.with_entities(func.count(Visit.id)).scalar() or 0
    today_visitors = (
        db.query(func.count(func.distinct(Visit.visitor_id))).filter(Visit.day == today).scalar() or 0
    )

    status_counts = defaultdict(int)
    for o in orders:
        status_counts[o.status] += 1

    # per day series for charts
    day_list = [chart_start + timedelta(days=i) for i in range(chart_days)]
    orders_by_day = defaultdict(int)
    revenue_by_day = defaultdict(Decimal)
    for o in db.query(Order).filter(Order.created_at >= chart_start).all():
        d = o.created_at.date()
        if o.status != "cancelled":
            orders_by_day[d] += 1
        if o.status in COUNTED:
            revenue_by_day[d] += D(o.total)
    visitors_by_day = dict(
        db.query(Visit.day, func.count(func.distinct(Visit.visitor_id)))
        .filter(Visit.day >= chart_start).group_by(Visit.day).all()
    )

    # top products & zones (non-cancelled)
    prod = defaultdict(lambda: {"qty": 0, "revenue": Decimal("0")})
    for o in live:
        for it in o.items or []:
            key = (it.get("name_ar"), it.get("name_en"))
            prod[key]["qty"] += int(it.get("qty", 0))
            prod[key]["revenue"] += D(it.get("price", 0)) * int(it.get("qty", 0))
    top_products = sorted(
        ({"name_ar": k[0], "name_en": k[1], **v} for k, v in prod.items()),
        key=lambda x: (-x["qty"], -x["revenue"]),
    )[:6]
    zones = defaultdict(lambda: {"orders": 0, "fees": Decimal("0")})
    for o in live:
        zones[o.zone_name]["orders"] += 1
        zones[o.zone_name]["fees"] += D(o.delivery_fee)
    top_zones = sorted(({"name": k, **v} for k, v in zones.items()), key=lambda x: -x["orders"])[:6]

    return {
        "orders_count": len(live),
        "revenue": revenue,
        "fees": fees,
        "pending_count": len(pending),
        "pending_value": pending_value,
        "customers": len({o.phone for o in live}),
        "aov": (revenue / len(counted)) if counted else Decimal("0"),
        "visitors": visitors,
        "views": views,
        "today_visitors": today_visitors,
        "conversion": (len(live) / visitors * 100) if visitors else 0,
        "status_counts": dict(status_counts),
        "labels": [d.strftime("%d/%m") for d in day_list],
        "orders_series": [orders_by_day.get(d, 0) for d in day_list],
        "revenue_series": [float(revenue_by_day.get(d, 0)) for d in day_list],
        "visitors_series": [int(visitors_by_day.get(d, 0)) for d in day_list],
        "top_products": top_products,
        "top_zones": top_zones,
    }


def bar_chart(values, labels, height=170, decimals=0) -> Markup:
    """Minimal inline-SVG bar chart (no JS, no libraries)."""
    n = len(values)
    if n == 0:
        return Markup("")
    w, pad_l, pad_b, pad_t = 640, 34, 24, 14
    h = height
    plot_w, plot_h = w - pad_l - 6, h - pad_b - pad_t
    vmax = max(values) or 1
    step = plot_w / n
    bw = max(3, step * 0.62)
    out = [f'<svg viewBox="0 0 {w} {h}" class="chart" role="img" preserveAspectRatio="none">']
    for i in range(3):
        y = pad_t + plot_h * i / 2
        val = vmax * (1 - i / 2)
        out.append(f'<line x1="{pad_l}" x2="{w-6}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>')
        out.append(f'<text x="{pad_l-6}" y="{y+3:.1f}" text-anchor="end" class="axis">{val:.{decimals}f}</text>')
    every = max(1, n // 8)
    for i, v in enumerate(values):
        bh = (v / vmax) * plot_h if vmax else 0
        x = pad_l + i * step + (step - bw) / 2
        y = pad_t + plot_h - bh
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(bh, 0.5):.1f}" class="bar">'
            f'<title>{escape(labels[i])}: {v:.{decimals}f}</title></rect>'
        )
        if i % every == 0:
            out.append(f'<text x="{x+bw/2:.1f}" y="{h-6}" text-anchor="middle" class="axis">{escape(labels[i])}</text>')
    out.append("</svg>")
    return Markup("".join(out))
