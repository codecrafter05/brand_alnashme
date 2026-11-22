from sqlalchemy.orm import Session

from app.config import SEED_DEMO
from app.models import AdminUser, Category, DeliveryZone, Product
from app.security import hash_password
from app.services.pricing import new_vid


def _v(ar, en, price, stock, sale=None):
    return {"id": new_vid(), "label_ar": ar, "label_en": en, "price": price, "sale_price": sale, "stock": stock}


ZONES = [
    ("المنامة", "Manama", "1.500"), ("المحرق", "Muharraq", "1.500"), ("الرفاع", "Riffa", "2.000"),
    ("مدينة عيسى", "Isa Town", "2.000"), ("مدينة حمد", "Hamad Town", "2.000"), ("سترة", "Sitra", "2.000"),
    ("سار", "Saar", "1.500"), ("البديع", "Budaiya", "2.000"), ("الجنبية", "Janabiya", "2.000"),
    ("الزلاق", "Zallaq", "3.000"), ("سند", "Sanad", "1.500"), ("جدحفص", "Jidhafs", "1.500"),
]

DEMO = [
    ("عطور سيغنتشر", "Signature Perfumes", "p3", [
        ("نوار أبسولو", "Noir Absolu", "عطر شرقي دافئ بنفحات العنبر والخشب.", "A warm oriental scent of amber and wood.",
         [_v("50 مل", "50 ml", 18.0, 12), _v("100 مل", "100 ml", 28.0, 8, 24.0)], True),
        ("أمبر نايتس", "Amber Nights", "عنبر وفانيلا لأمسيات هادئة.", "Amber and vanilla for quiet evenings.",
         [_v("50 مل", "50 ml", 16.5, 10), _v("100 مل", "100 ml", 26.0, 6)], False),
        ("فانيلا رويال", "Royal Vanilla", "فانيلا ناعمة مع لمسة مسك.", "Soft vanilla with a touch of musk.",
         [_v("100 مل", "100 ml", 22.0, 9)], False),
    ]),
    ("عطور براندات عالمية", "International Brands", "p4", [
        ("بلاك إكس إل إكسس", "Black XS L'Exces", "عطر جريء بحضور قوي.", "A bold fragrance with a strong presence.",
         [_v("30 مل", "30 ml", 14.0, 15), _v("60 مل", "60 ml", 22.5, 10), _v("100 مل", "100 ml", 32.0, 5)], True),
        ("إليغانس بلو", "Elegance Bleu", "انتعاش حمضي مع قاعدة خشبية.", "Fresh citrus over a woody base.",
         [_v("60 مل", "60 ml", 24.0, 7), _v("100 مل", "100 ml", 34.0, 0)], False),
        ("وود إنتنس", "Wood Intense", "خشب مدخن وتوابل دافئة.", "Smoky wood and warm spices.",
         [_v("100 مل", "100 ml", 29.0, 4, 25.0)], False),
    ]),
    ("عطور عربية", "Arabic Perfumes", "p1", [
        ("مسك الغزال", "Musk Al Ghazal", "مسك أبيض نقي وخفيف.", "Pure, light white musk.",
         [_v("12 مل", "12 ml", 6.0, 30), _v("30 مل", "30 ml", 11.0, 20)], True),
        ("عنبر ملكي", "Royal Amber", "عنبر غني بطابع عربي أصيل.", "Rich amber with an authentic Arabian character.",
         [_v("30 مل", "30 ml", 9.5, 14), _v("60 مل", "60 ml", 16.0, 9, 13.5)], False),
        ("ورد طائفي", "Taif Rose", "ورد طائفي مركز.", "Concentrated Taif rose.",
         [_v("50 مل", "50 ml", 14.0, 11)], False),
    ]),
    ("دهن عود", "Oud Oil", "p6", [
        ("دهن عود كمبودي", "Cambodian Oud Oil", "دهن عود كمبودي فاخر.", "Premium Cambodian oud oil.",
         [_v("3 جرام", "3 g", 18.0, 10), _v("6 جرام", "6 g", 32.0, 6), _v("12 جرام", "12 g", 58.0, 3)], True),
        ("دهن عود هندي", "Indian Oud Oil", "رائحة عميقة ودافئة تدوم.", "Deep, warm and long-lasting.",
         [_v("3 جرام", "3 g", 25.0, 8), _v("6 جرام", "6 g", 46.0, 5, 39.0)], False),
        ("دهن عود معتق", "Aged Oud Oil", "معتق لسنوات للحصول على نعومة فريدة.", "Aged for years for a unique smoothness.",
         [_v("3 جرام", "3 g", 35.0, 4)], False),
    ]),
    ("بخور", "Bakhoor", "p5", [
        ("بخور عود مبخر", "Oud Bakhoor", "بخور عود غني بدخان كثيف.", "Rich oud bakhoor with dense smoke.",
         [_v("40 جرام", "40 g", 5.5, 25), _v("100 جرام", "100 g", 11.0, 12)], False),
        ("بخور صندل", "Sandal Bakhoor", "صندل ناعم ورائحة هادئة.", "Smooth sandalwood, calm aroma.",
         [_v("50 جرام", "50 g", 6.5, 18)], False),
        ("بخور ملكي", "Royal Bakhoor", "خلطة ملكية من العود والعنبر.", "A royal blend of oud and amber.",
         [_v("100 جرام", "100 g", 12.0, 9, 9.5)], True),
    ]),
]


def seed_all(db: Session) -> None:
    if not db.query(AdminUser).count():
        db.add(AdminUser(username="admin", password_hash=hash_password("admin")))
        db.commit()
    if not SEED_DEMO:
        return
    if not db.query(DeliveryZone).count():
        for i, (ar, en, price) in enumerate(ZONES):
            db.add(DeliveryZone(name_ar=ar, name_en=en, price=price, sort_order=i))
        db.commit()
    if not db.query(Category).count():
        for i, (cat_ar, cat_en, img, products) in enumerate(DEMO):
            cat = Category(name_ar=cat_ar, name_en=cat_en, image=f"/static/demo/{img}.jpg", sort_order=i)
            db.add(cat)
            db.flush()
            for j, (n_ar, n_en, d_ar, d_en, variants, featured) in enumerate(products):
                pimg = ["p1", "p2", "p3", "p4", "p5", "p6"][(i + j) % 6]
                db.add(Product(category_id=cat.id, name_ar=n_ar, name_en=n_en, desc_ar=d_ar, desc_en=d_en,
                               image=f"/static/demo/{pimg}.jpg", variants=variants, is_featured=featured))
        db.commit()
