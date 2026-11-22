from datetime import datetime

from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import TEMPLATES_DIR
from app.models import Category, DeliveryZone
from app.services import pricing
from app.services.i18n import DEFAULT_LANG, LANGS, make_translator
from app.services.settings import get_settings

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals.update(
    fmt=pricing.fmt,
    eff_price=pricing.eff_price,
    on_sale=pricing.on_sale,
    discount_pct=pricing.discount_pct,
    summary=pricing.summary,
    D=pricing.D,
    now_year=datetime.now().year,
)


def get_lang(request: Request) -> str:
    lang = request.cookies.get("lang")
    return lang if lang in LANGS else DEFAULT_LANG


def public_ctx(request: Request, db: Session, **extra) -> dict:
    lang = get_lang(request)
    s = get_settings(db)
    zones = (
        db.query(DeliveryZone).filter(DeliveryZone.is_active.is_(True))
        .order_by(DeliveryZone.sort_order, DeliveryZone.id).all()
    )
    t = make_translator(lang)

    def L(obj, field):
        primary = getattr(obj, f"{field}_{lang}", None)
        if primary:
            return primary
        return getattr(obj, f"{field}_{'en' if lang == 'ar' else 'ar'}", "") or ""

    def S(key):  # localized setting
        return s.get(f"{key}_{lang}") or s.get(f"{key}_{'en' if lang == 'ar' else 'ar'}") or ""

    store = {
        "lang": lang,
        "currency": t("currency"),
        "zones": [{"id": z.id, "name": L(z, "name"), "price": pricing.fmt(z.price)} for z in zones],
        "freeDelivery": {
            "enabled": s["free_delivery_enabled"] == "1",
            "threshold": pricing.fmt(s["free_delivery_threshold"]),
        },
        "i18n": {k: t(k) for k in (
            "cart_empty", "free", "choose_area_first", "err_required", "err_email", "err_phone",
            "err_generic", "only_left", "free_over", "free_more", "free_unlocked", "sending",
            "place_order", "quick_add", "out_of_stock",
        )},
    }
    ctx = {
        "request": request,
        "lang": lang,
        "dir": "rtl" if lang == "ar" else "ltr",
        "t": t,
        "L": L,
        "S": S,
        "s": s,
        "store": store,
        "zones": zones,
        "nav_categories": db.query(Category).filter(Category.is_active.is_(True))
        .order_by(Category.sort_order, Category.id).all(),
        "path": request.url.path,
    }
    ctx.update(extra)
    return ctx


def render_public(request: Request, db: Session, name: str, status_code: int = 200, **extra):
    return templates.TemplateResponse(request, name, public_ctx(request, db, **extra), status_code=status_code)
