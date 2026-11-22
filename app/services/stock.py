from sqlalchemy.orm import Session

from app.models import Order, Product


def _adjust(db: Session, order: Order, sign: int) -> list[tuple]:
    """sign=-1 deducts stock, +1 restores it. Returns human-readable warnings."""
    warnings = []
    for it in order.items or []:
        product = db.get(Product, it.get("product_id"))
        if not product:
            continue
        variants = [dict(v) for v in (product.variants or [])]
        for v in variants:
            if v.get("id") == it.get("variant_id"):
                qty = int(it.get("qty", 0))
                before = int(v.get("stock", 0))
                after = before + sign * qty
                if after < 0:
                    warnings.append(("المخزون غير كافي لـ {name} ({label}) — تم تصفيره", {"name": product.name_ar, "label": v["label_ar"]}))
                    after = 0
                v["stock"] = after
        product.variants = variants
    return warnings


def change_status(db: Session, order: Order, new_status: str) -> list[tuple]:
    warnings = []
    if new_status in ("confirmed", "delivered") and not order.stock_deducted:
        warnings = _adjust(db, order, -1)
        order.stock_deducted = True
    elif new_status in ("new", "cancelled") and order.stock_deducted:
        _adjust(db, order, +1)
        order.stock_deducted = False
    order.status = new_status
    db.commit()
    return warnings
