from fastapi import Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.models import Order
from app.security import csrf_token
from app.services.admin_i18n import ALANGS, tr
from app.services.settings import get_settings
from app.templating import templates

# Arabic source strings; translated per request by tr()
STATUS_LABELS = {"new": "جديد", "confirmed": "مؤكد", "delivered": "تم التوصيل", "cancelled": "ملغي"}


def get_alang(request: Request) -> str:
    lang = request.cookies.get("alang")
    return lang if lang in ALANGS else "en"


def flash(request: Request, message: str, kind: str = "ok", **kw):
    request.session.setdefault("flash", []).append({"m": message, "k": kind, "kw": kw})


def redirect(url: str):
    return RedirectResponse(url, status_code=303)


def i18n_ctx(request: Request) -> dict:
    """Language bits every admin template needs (also used by the login page)."""
    lang = get_alang(request)
    return {
        "alang": lang,
        "adir": "rtl" if lang == "ar" else "ltr",
        "_": lambda text, **kw: tr(text, lang, **kw),
        "js_i18n": {k: tr(v, lang) for k, v in {
            "size_ar": "الحجم بالعربي (50 مل)", "size_en": "Size (50 ml)", "price": "السعر",
            "sale_price": "بعد التخفيض", "stock": "الكمية", "area_ar": "المنطقة بالعربي",
            "area_en": "Area (English)", "delivery_price": "سعر التوصيل", "active": "مفعّلة", "remove": "حذف",
        }.items()},
    }


def render_admin(request: Request, db: Session, name: str, status_code: int = 200, **ctx):
    base = i18n_ctx(request)
    lang = base["alang"]
    base.update({
        "request": request,
        "csrf": csrf_token(request),
        "flashes": [
            {"m": tr(f["m"], lang, **f.get("kw", {})), "k": f["k"]} for f in request.session.pop("flash", [])
        ],
        "pending_orders": db.query(Order).filter(Order.status == "new").count(),
        "default_password": bool(request.session.get("default_pw")),
        "s": get_settings(db),
        "status_labels": {k: tr(v, lang) for k, v in STATUS_LABELS.items()},
        "path": request.url.path,
    })
    base.update(ctx)
    return templates.TemplateResponse(request, name, base, status_code=status_code)
