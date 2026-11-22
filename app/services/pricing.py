"""Money + variant helpers. Variants live as JSON on the product."""
import json
import uuid
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

_Q = Decimal("0.001")


def D(value) -> Decimal:
    try:
        return Decimal(str(value)).quantize(_Q, ROUND_HALF_UP)
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.000")


def fmt(value) -> str:
    return f"{D(value):.3f}"


def eff_price(v: dict) -> Decimal:
    price = D(v.get("price", 0))
    sp = v.get("sale_price")
    if sp not in (None, "", 0, "0"):
        sale = D(sp)
        if 0 < sale < price:
            return sale
    return price


def on_sale(v: dict) -> bool:
    return eff_price(v) < D(v.get("price", 0))


def discount_pct(v: dict) -> int:
    price = D(v.get("price", 0))
    if price <= 0 or not on_sale(v):
        return 0
    return int(((price - eff_price(v)) / price * 100).quantize(Decimal("1"), ROUND_HALF_UP))


def new_vid() -> str:
    return uuid.uuid4().hex[:8]


def find_variant(product, vid: str):
    for v in product.variants or []:
        if v.get("id") == vid:
            return v
    return None


def summary(product) -> dict:
    """What a product card needs: from-price, sale flag, stock flag."""
    vs = product.variants or []
    if not vs:
        return {"price": D(0), "orig": None, "on_sale": False, "pct": 0, "in_stock": False, "multi": False}
    in_stock_vs = [v for v in vs if int(v.get("stock", 0)) > 0]
    pool = in_stock_vs or vs
    best = min(pool, key=eff_price)
    return {
        "price": eff_price(best),
        "orig": D(best["price"]) if on_sale(best) else None,
        "on_sale": any(on_sale(v) for v in pool),
        "pct": max((discount_pct(v) for v in pool), default=0),
        "in_stock": bool(in_stock_vs),
        "multi": len(vs) > 1,
    }


def has_sale(product) -> bool:
    return any(on_sale(v) and int(v.get("stock", 0)) > 0 for v in (product.variants or []))


def parse_variants_json(raw: str, previous: list | None = None):
    """Validate the variants JSON coming from the admin form."""
    errors = []
    try:
        data = json.loads(raw or "[]")
        if not isinstance(data, list):
            raise ValueError
    except ValueError:
        return [], [("صيغة الأحجام غير صحيحة", {})]

    old_ids = {v.get("id") for v in (previous or [])}
    out, seen = [], set()
    for i, row in enumerate(data, 1):
        if not isinstance(row, dict):
            continue
        label_ar = str(row.get("label_ar", "")).strip()
        label_en = str(row.get("label_en", "")).strip()
        if not label_ar and not label_en:
            errors.append(("الصنف {n}: اكتب اسم الحجم", {"n": i}))
            continue
        label_ar, label_en = label_ar or label_en, label_en or label_ar
        price = D(row.get("price"))
        if price <= 0:
            errors.append(("الصنف {n}: السعر مطلوب", {"n": i}))
            continue
        sale_raw = row.get("sale_price")
        sale = None
        if sale_raw not in (None, "", "0"):
            sale = D(sale_raw)
            if not (0 < sale < price):
                errors.append(("الصنف {n}: سعر التخفيض لازم يكون أقل من السعر", {"n": i}))
                continue
        try:
            stock = max(0, int(float(row.get("stock") or 0)))
        except ValueError:
            stock = 0
        vid = str(row.get("id") or "")
        if not vid or vid in seen:
            vid = new_vid()
        seen.add(vid)
        out.append({
            "id": vid, "label_ar": label_ar, "label_en": label_en,
            "price": float(price), "sale_price": float(sale) if sale else None, "stock": stock,
        })
    if not out and not errors:
        errors.append(("أضف حجم واحد على الأقل مع السعر", {}))
    return out, errors
