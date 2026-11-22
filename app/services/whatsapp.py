import re
from urllib.parse import quote

from app.services.pricing import fmt


def normalize_number(raw: str, default_cc: str = "973") -> str:
    digits = re.sub(r"\D", "", raw or "")
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) == 8:  # local Bahrain number
        digits = default_cc + digits
    return digits


def wa_link(number: str, text: str) -> str:
    return f"https://wa.me/{normalize_number(number)}?text={quote(text)}"


def build_order_message(order, lang: str) -> str:
    ar = lang == "ar"
    cur = "د.ب" if ar else "BHD"
    lines = []
    lines.append(("طلب جديد" if ar else "New order") + f" #{order.order_number}")
    lines.append("")
    lines.append(("الاسم: " if ar else "Name: ") + order.customer_name)
    lines.append(("الهاتف: " if ar else "Phone: ") + order.phone)
    lines.append(("الإيميل: " if ar else "Email: ") + order.email)
    lines.append(("المنطقة: " if ar else "Area: ") + (order.zone_name if ar else (order.zone_name_en or order.zone_name)))
    if ar:
        lines.append(f"العنوان: منزل {order.house}، طريق {order.road}، بلوك {order.block}")
    else:
        lines.append(f"Address: House {order.house}, Road {order.road}, Block {order.block}")
    if order.note:
        lines.append(("ملاحظات: " if ar else "Notes: ") + order.note)
    lines.append("")
    lines.append("المنتجات:" if ar else "Items:")
    for i, it in enumerate(order.items, 1):
        name = it["name_ar"] if ar else it["name_en"]
        label = it["label_ar"] if ar else it["label_en"]
        line_total = fmt(float(it["price"]) * int(it["qty"]))
        lines.append(f"{i}) {name} ({label}) x{it['qty']} = {line_total} {cur}")
    lines.append("")
    lines.append(("المجموع: " if ar else "Subtotal: ") + f"{fmt(order.subtotal)} {cur}")
    fee = "مجاني" if (ar and float(order.delivery_fee) == 0) else ("Free" if float(order.delivery_fee) == 0 else f"{fmt(order.delivery_fee)} {cur}")
    lines.append(("التوصيل: " if ar else "Delivery: ") + fee)
    lines.append(("الإجمالي: " if ar else "Total: ") + f"{fmt(order.total)} {cur}")
    return "\n".join(lines)
