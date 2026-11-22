import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DeliveryZone, Order
from app.security import client_ip, rate_limited
from app.services.cart import delivery_fee, resolve_cart
from app.services.i18n import LANGS, make_translator
from app.services.pricing import fmt
from app.services.settings import get_settings
from app.services.whatsapp import build_order_message, wa_link
from app.templating import get_lang

router = APIRouter(prefix="/api")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _lines_json(lines):
    return [{
        "p": l["p"], "v": l["v"], "qty": l["qty"], "stock": l["stock"], "name": l["name"],
        "label": l["label"], "image": l["image"], "price": fmt(l["price"]),
        "orig": fmt(l["orig"]) if l["orig"] else None, "line_total": fmt(l["line_total"]),
    } for l in lines]


@router.post("/cart/resolve")
async def cart_resolve(request: Request, db: Session = Depends(get_db)):
    try:
        data = await request.json()
    except ValueError:
        data = {}
    lang = get_lang(request)
    lines, subtotal = resolve_cart(db, data.get("items", []), lang)
    return {"items": _lines_json(lines), "subtotal": fmt(subtotal)}


@router.post("/order")
async def create_order(request: Request, db: Session = Depends(get_db)):
    if rate_limited(f"order:{client_ip(request)}", limit=8, window=600):
        return JSONResponse({"ok": False, "error": "Too many requests"}, status_code=429)
    try:
        data = await request.json()
        assert isinstance(data, dict)
    except (ValueError, AssertionError):
        return JSONResponse({"ok": False, "error": "Bad request"}, status_code=400)

    lang = data.get("lang") if data.get("lang") in LANGS else get_lang(request)
    t = make_translator(lang)
    s = get_settings(db)

    def clean(key, limit):
        return str(data.get(key, "") or "").strip()[:limit]

    name, email, phone = clean("name", 150), clean("email", 190), clean("phone", 40)
    house, road, block, note = clean("house", 80), clean("road", 80), clean("block", 80), clean("note", 1000)
    errors = {}
    for key, val in (("name", name), ("email", email), ("phone", phone), ("house", house),
                     ("road", road), ("block", block)):
        if not val:
            errors[key] = t("err_required")
    if email and not EMAIL_RE.match(email):
        errors["email"] = t("err_email")
    digits = re.sub(r"\D", "", phone)
    if phone and not 8 <= len(digits) <= 15:
        errors["phone"] = t("err_phone")
    zone = None
    try:
        zone = db.get(DeliveryZone, int(data.get("zone_id")))
    except (TypeError, ValueError):
        pass
    if not zone or not zone.is_active:
        errors["zone_id"] = t("err_required")
    if errors:
        return JSONResponse({"ok": False, "errors": errors}, status_code=422)

    raw_items = data.get("items", [])
    lines, subtotal = resolve_cart(db, raw_items, lang)
    if not lines:
        return JSONResponse({"ok": False, "error": t("err_empty_cart")}, status_code=400)

    fee = delivery_fee(zone.price, subtotal, s)
    order = Order(
        status="new", customer_name=name, email=email, phone=phone,
        zone_name=zone.name_ar, zone_name_en=zone.name_en,
        house=house, road=road, block=block, note=note or None,
        items=[{
            "product_id": l["p"], "variant_id": l["v"], "name_ar": l["name_ar"], "name_en": l["name_en"],
            "label_ar": l["label_ar"], "label_en": l["label_en"], "price": float(l["price"]), "qty": l["qty"],
        } for l in lines],
        subtotal=subtotal, delivery_fee=fee, total=subtotal + fee, lang=lang,
    )
    db.add(order)
    db.flush()
    order.order_number = f"BA{1000 + order.id}"
    db.commit()

    url = wa_link(s["whatsapp_number"], build_order_message(order, lang))
    return {"ok": True, "order_number": order.order_number, "whatsapp_url": url}
