import time

from sqlalchemy.orm import Session

from app.config import DEFAULT_WHATSAPP
from app.models.system import Setting

DEFAULTS = {
    "store_name": "Brand Alnashme",
    "tagline_ar": "عطور · بخور · وأكثر",
    "tagline_en": "Perfumes · Bakhoor · More",
    "announcement_ar": "الطلب عن طريق الواتساب — نوصل لجميع مناطق البحرين",
    "announcement_en": "Order via WhatsApp — delivery across Bahrain",
    "hero_image": "/static/demo/hero.jpg",
    "hero_eyebrow_ar": "مجموعة الموسم",
    "hero_eyebrow_en": "The Collection",
    "hero_title_ar": "عطور تحكي حضورك",
    "hero_title_en": "Fragrances that speak for you",
    "hero_subtitle_ar": "تشكيلة مختارة من العطور العربية والعالمية والبخور ودهن العود، بأناقة تليق بذوقك.",
    "hero_subtitle_en": "A curated selection of Arabic and international perfumes, oud oils and bakhoor.",
    "hero_button_ar": "تسوق الآن",
    "hero_button_en": "Shop now",
    "about_title_ar": "عن براند النعشمي",
    "about_title_en": "About Brand Alnashme",
    "about_text_ar": "نختار لك العطور بعناية، من العطور العربية الأصيلة إلى أشهر البراندات العالمية، مع دهن العود والبخور. اطلب عبر الواتساب وبنوصلك الطلب لين باب البيت.",
    "about_text_en": "We hand-pick fragrances for you, from authentic Arabic perfumes to leading international brands, alongside oud oils and bakhoor. Order via WhatsApp and we deliver to your door.",
    "about_image": "/static/demo/wall.jpg",
    "whatsapp_number": DEFAULT_WHATSAPP,
    "contact_phone": "",
    "contact_email": "",
    "instagram": "",
    "tiktok": "",
    "snapchat": "",
    "facebook": "",
    "x_twitter": "",
    "free_delivery_enabled": "0",
    "free_delivery_threshold": "10.000",
    "footer_text_ar": "جميع الحقوق محفوظة",
    "footer_text_en": "All rights reserved",
}

_cache = {"data": None, "ts": 0.0}
_TTL = 5.0


def get_settings(db: Session) -> dict:
    now = time.time()
    if _cache["data"] is not None and now - _cache["ts"] < _TTL:
        return _cache["data"]
    data = dict(DEFAULTS)
    for row in db.query(Setting).all():
        if row.key in DEFAULTS and row.value is not None:
            data[row.key] = row.value
    _cache.update(data=data, ts=now)
    return data


def save_settings(db: Session, values: dict) -> None:
    for key, value in values.items():
        if key not in DEFAULTS:
            continue
        row = db.get(Setting, key)
        if row is None:
            db.add(Setting(key=key, value=value))
        else:
            row.value = value
    db.commit()
    invalidate()


def invalidate() -> None:
    _cache["data"] = None
