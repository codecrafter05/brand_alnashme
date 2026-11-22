import json

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DeliveryZone
from app.security import require_admin, verify_csrf
from app.services.pricing import D

from .common import flash, redirect, render_admin

router = APIRouter(prefix="/delivery", dependencies=[Depends(require_admin)])


@router.get("")
def delivery_page(request: Request, db: Session = Depends(get_db)):
    zones = db.query(DeliveryZone).order_by(DeliveryZone.sort_order, DeliveryZone.id).all()
    zones_data = [{"id": z.id, "name_ar": z.name_ar, "name_en": z.name_en, "price": float(z.price), "is_active": z.is_active} for z in zones]
    return render_admin(request, db, "admin/delivery.html", zones_data=zones_data)


@router.post("", dependencies=[Depends(verify_csrf)])
def save_zones(request: Request, zones_json: str = Form("[]"), db: Session = Depends(get_db)):
    try:
        rows = json.loads(zones_json)
        assert isinstance(rows, list)
    except (ValueError, AssertionError):
        flash(request, "صيغة البيانات غير صحيحة", "err")
        return redirect("/admin/delivery")

    errors, clean = [], []
    for i, r in enumerate(rows, 1):
        name_ar, name_en = str(r.get("name_ar", "")).strip(), str(r.get("name_en", "")).strip()
        if not name_ar and not name_en:
            continue  # ignore blank rows
        price = D(r.get("price"))
        if price < 0:
            errors.append(i)
        clean.append({"id": r.get("id"), "name_ar": name_ar or name_en, "name_en": name_en or name_ar,
                      "price": price, "is_active": bool(r.get("is_active", True))})
    if errors:
        for n in errors:
            flash(request, "السطر {n}: السعر غير صحيح", "err", n=n)
        return redirect("/admin/delivery")

    existing = {z.id: z for z in db.query(DeliveryZone).all()}
    keep = set()
    for order, r in enumerate(clean):
        zone = existing.get(int(r["id"])) if str(r["id"] or "").isdigit() else None
        if zone is None:
            zone = DeliveryZone()
            db.add(zone)
        zone.name_ar, zone.name_en, zone.price = r["name_ar"], r["name_en"], r["price"]
        zone.is_active, zone.sort_order = r["is_active"], order
        db.flush()
        keep.add(zone.id)
    for zid, zone in existing.items():
        if zid not in keep:
            db.delete(zone)
    db.commit()
    flash(request, "تم حفظ مناطق التوصيل")
    return redirect("/admin/delivery")
