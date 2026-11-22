"""Resolve a raw cart (product/variant/qty) against the DB. The server is the source of truth for prices."""
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Product
from app.services.pricing import D, eff_price, find_variant, on_sale


def resolve_cart(db: Session, raw_items: list, lang: str = "ar"):
    """Returns (lines, subtotal). Lines whose product/variant vanished are dropped; qty is clamped to stock."""
    ids = []
    for it in raw_items or []:
        try:
            ids.append(int(it.get("p")))
        except (TypeError, ValueError, AttributeError):
            continue
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(set(ids)), Product.is_active.is_(True)).all()} if ids else {}

    lines, subtotal = [], Decimal("0.000")
    merged = {}
    for it in raw_items or []:
        if not isinstance(it, dict):
            continue
        try:
            pid, vid, qty = int(it.get("p")), str(it.get("v")), int(it.get("q"))
        except (TypeError, ValueError):
            continue
        if qty < 1:
            continue
        merged[(pid, vid)] = merged.get((pid, vid), 0) + qty

    for (pid, vid), qty in merged.items():
        product = products.get(pid)
        if not product or not product.category or not product.category.is_active:
            continue
        v = find_variant(product, vid)
        if not v:
            continue
        stock = int(v.get("stock", 0))
        if stock <= 0:
            continue
        qty = min(qty, stock, 99)
        price = eff_price(v)
        line_total = price * qty
        subtotal += line_total
        lines.append({
            "p": pid, "v": vid, "qty": qty, "stock": stock,
            "name_ar": product.name_ar, "name_en": product.name_en,
            "label_ar": v["label_ar"], "label_en": v["label_en"],
            "name": product.name_ar if lang == "ar" else product.name_en,
            "label": v["label_ar"] if lang == "ar" else v["label_en"],
            "image": product.image, "price": price,
            "orig": D(v["price"]) if on_sale(v) else None,
            "line_total": line_total,
        })
    return lines, subtotal


def delivery_fee(zone_price: Decimal, subtotal: Decimal, s: dict) -> Decimal:
    if s.get("free_delivery_enabled") == "1" and subtotal >= D(s.get("free_delivery_threshold", "0")) > 0:
        return Decimal("0.000")
    return D(zone_price)
