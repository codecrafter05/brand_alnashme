"""Admin panel translations. Source language is Arabic; EN maps Arabic text -> English.

Templates call  _('نص عربي')  and Python flashes use Arabic text; when the admin picks English the
string is looked up here. Missing keys simply fall back to the Arabic text.
"""
import os

ALANGS = ("ar", "en")
_DEBUG = os.getenv("ADMIN_I18N_DEBUG") == "1"

EN = {
    # navigation / general
    "لوحة التحكم": "Dashboard", "الطلبات": "Orders", "المنتجات": "Products", "الأقسام": "Categories",
    "التوصيل": "Delivery", "الإعدادات": "Settings", "عرض المتجر": "View store", "تسجيل الخروج": "Log out",
    "تسجيل الدخول": "Sign in", "دخول": "Sign in", "اسم المستخدم": "Username", "كلمة المرور": "Password",
    "اسم المستخدم أو كلمة المرور غير صحيحة": "Wrong username or password",
    "محاولات كثيرة، حاول بعد شوي": "Too many attempts, try again shortly",
    "كلمة المرور الحالية هي الافتراضية (admin). غيّرها من": "Your password is still the default (admin). Change it from",
    "د.ب": "BHD", "الكل": "All", "حفظ": "Save", "رجوع": "Back", "تعديل": "Edit", "حذف": "Delete", "عرض": "View",
    "بحث": "Search", "بحث بالاسم": "Search by name", "الحالة": "Status", "الصورة": "Image", "الاسم": "Name",
    "الترتيب": "Order", "ظاهر": "Visible", "مخفي": "Hidden", "مميز": "Featured", "غير مميز": "Not featured",
    "مفعّل": "Enabled", "مفعّلة": "Active", "مجاني": "Free", "عربي": "Arabic", "بدون صورة": "No image",
    "حذف الصورة": "Remove image", "يفضل صورة طولية": "A portrait image works best,",
    "تتحول تلقائياً لصيغة خفيفة": "converted automatically to a light format",
    # statuses
    "جديد": "New", "مؤكد": "Confirmed", "تم التوصيل": "Delivered", "ملغي": "Cancelled",
    # dashboard
    "7 أيام": "7 days", "30 يوم": "30 days", "90 يوم": "90 days", "عدد الطلبات": "Orders", "بدون الملغية": "excluding cancelled",
    "المبيعات المؤكدة": "Confirmed sales", "د.ب — مؤكد + تم التوصيل": "BHD — confirmed + delivered",
    "طلبات تنتظر التأكيد": "Orders awaiting confirmation", "بقيمة {v} د.ب": "worth {v} BHD",
    "مبالغ التوصيل": "Delivery fees", "د.ب — من الطلبات المؤكدة": "BHD — from confirmed orders",
    "العملاء": "Customers", "حسب رقم الهاتف": "by phone number", "متوسط قيمة الطلب": "Average order value",
    "زوار الموقع": "Site visitors", "اليوم: {t} · مشاهدات: {v}": "Today: {t} · Page views: {v}",
    "نسبة التحويل": "Conversion rate", "طلبات ÷ زوار": "orders ÷ visitors",
    "الطلبات يومياً": "Orders per day", "آخر {n} يوم": "last {n} days", "المبيعات يومياً (د.ب)": "Sales per day (BHD)",
    "الزوار يومياً": "Visitors per day", "زائر فريد": "unique visitors", "الأكثر طلباً": "Top products",
    "حسب منطقة التوصيل": "By delivery area", "لا توجد بيانات بعد": "No data yet", "حالات الطلبات": "Order statuses",
    "المنتج": "Product", "الكمية": "Quantity", "المبلغ": "Amount", "المنطقة": "Area",
    # categories
    "قسم جديد": "New category", "تعديل القسم": "Edit category", "تعديل قسم": "Edit category",
    "اسم القسم (عربي)": "Category name (Arabic)", "صورة القسم": "Category image", "ظاهر في المتجر": "Visible in the store",
    "ما فيه أقسام بعد": "No categories yet", "أضف أول قسم": "Add your first category",
    "حذف القسم «{name}»؟": "Delete category “{name}”?",
    "اكتب اسم القسم بالعربي والإنجليزي": "Enter the category name in Arabic and English",
    "تم إضافة القسم": "Category added", "تم حفظ القسم": "Category saved", "تم حذف القسم": "Category deleted",
    "ما تقدر تحذف قسم فيه منتجات. انقل المنتجات أو احذفها أول، أو اخفي القسم.":
        "You can't delete a category that has products. Move or delete its products first, or hide the category.",
    # products
    "منتج جديد": "New product", "تعديل المنتج": "Edit product", "تعديل منتج": "Edit product",
    "كل الأقسام": "All categories", "كل الحالات": "All statuses", "القسم": "Category", "الأسعار": "Prices",
    "المخزون": "Stock", "ما فيه منتجات": "No products", "حذف المنتج «{name}»؟": "Delete product “{name}”?",
    "بيانات المنتج": "Product details", "اسم المنتج (عربي)": "Product name (Arabic)", "الوصف (عربي)": "Description (Arabic)",
    "الصورة والظهور": "Image & visibility", "منتج مميز (يطلع في الصفحة الرئيسية)": "Featured product (shown on the home page)",
    "الأحجام والأسعار": "Sizes & prices",
    "لكل حجم: السعر، وسعر بعد التخفيض (اختياري)، والكمية المتوفرة": "For each size: price, sale price (optional) and available quantity",
    "الحجم (عربي)": "Size (Arabic)", "الحجم": "Size", "السعر (د.ب)": "Price (BHD)", "بعد التخفيض": "Sale price",
    "إضافة حجم": "Add size", "حفظ المنتج": "Save product", "السعر": "Price",
    "اختر القسم": "Choose a category", "اكتب اسم المنتج بالعربي والإنجليزي": "Enter the product name in Arabic and English",
    "أضف قسم أول قبل ما تضيف منتج": "Add a category before adding a product",
    "تم حفظ المنتج": "Product saved", "تم حذف المنتج (الطلبات القديمة تبقى محفوظة)": "Product deleted (past orders are kept)",
    "صيغة الأحجام غير صحيحة": "Invalid sizes format", "الصنف {n}: اكتب اسم الحجم": "Size {n}: enter the size name",
    "الصنف {n}: السعر مطلوب": "Size {n}: price is required",
    "الصنف {n}: سعر التخفيض لازم يكون أقل من السعر": "Size {n}: the sale price must be lower than the price",
    "أضف حجم واحد على الأقل مع السعر": "Add at least one size with a price",
    # delivery
    "مناطق التوصيل": "Delivery areas",
    "أضف مناطق البحرين اللي توصلها وحدد سعر التوصيل لكل منطقة، وبعدين اضغط حفظ":
        "Add the areas in Bahrain you deliver to, set the delivery price for each, then press save",
    "تقدر ترجع تضيف مناطق ثانية بأي وقت": "You can come back and add more areas at any time",
    "المنطقة (عربي)": "Area (Arabic)", "سعر التوصيل (د.ب)": "Delivery price (BHD)", "إضافة منطقة": "Add area",
    "حفظ المناطق": "Save areas", "تم حفظ مناطق التوصيل": "Delivery areas saved",
    "صيغة البيانات غير صحيحة": "Invalid data format", "السطر {n}: السعر غير صحيح": "Row {n}: invalid price",
    # orders
    "رقم الطلب، الاسم، الهاتف، الإيميل": "Order no., name, phone, email", "الطلب": "Order", "التاريخ": "Date",
    "العميل": "Customer", "الهاتف": "Phone", "الإيميل": "Email", "الإجمالي": "Total", "ما فيه طلبات": "No orders",
    "طلب": "Order", "إجراءات الطلب": "Order actions",
    "عند تأكيد الطلب ينقص المخزون تلقائياً، وإذا ألغيته يرجع": "Confirming an order deducts stock automatically; cancelling it puts the stock back",
    "تأكيد الطلب": "Confirm order", "إلغاء الطلب": "Cancel order", "رجوع إلى مؤكد": "Back to confirmed",
    "إعادة فتح الطلب": "Reopen order", "مراسلة العميل على الواتساب": "Message customer on WhatsApp",
    "المجموع": "Subtotal", "بيانات العميل": "Customer details", "العنوان": "Address", "الملاحظات": "Notes",
    "لغة الطلب": "Order language", "منزل {h}، طريق {r}، بلوك {b}": "House {h}, Road {r}, Block {b}",
    "تم تغيير حالة الطلب إلى: {status}": "Order status changed to: {status}",
    "المخزون غير كافي لـ {name} ({label}) — تم تصفيره": "Not enough stock for {name} ({label}) — set to zero",
    # settings
    "الواتساب والتوصيل": "WhatsApp & delivery", "رقم الواتساب لاستقبال الطلبات": "WhatsApp number that receives orders",
    "بالصيغة الدولية مثل 97337331306 (إذا كتبت 8 أرقام يضاف رمز البحرين تلقائياً)":
        "International format, e.g. 97337331306 (if you type 8 digits the Bahrain code is added automatically)",
    "التوصيل المجاني": "Free delivery",
    "إذا فعلته، أي طلب يوصل للمبلغ المحدد يكون توصيله مجاني": "When enabled, any order reaching the set amount gets free delivery",
    "الحد الأدنى للتوصيل المجاني (د.ب)": "Minimum order for free delivery (BHD)",
    "الصفحة الرئيسية (الهيرو)": "Home page (hero)", "صورة الهيرو": "Hero image",
    "العنوان الصغير (عربي)": "Small heading (Arabic)", "العنوان الرئيسي (عربي)": "Main title (Arabic)",
    "النص (عربي)": "Text (Arabic)", "نص الزر (عربي)": "Button text (Arabic)", "نصوص المتجر": "Store texts",
    "اسم المتجر": "Store name", "الشعار النصي (عربي)": "Tagline (Arabic)",
    "شريط الإعلان العلوي (عربي)": "Top announcement bar (Arabic)", "عنوان قسم «من نحن» (عربي)": "“About us” title (Arabic)",
    "نص «من نحن» (عربي)": "“About us” text (Arabic)", "نص أسفل الصفحة (عربي)": "Footer text (Arabic)",
    "التواصل وروابط السوشل ميديا": "Contact & social media links", "اترك الحقل فاضي لإخفاء الرابط": "leave a field empty to hide the link",
    "رقم الهاتف للعرض": "Phone number to display", "بيانات الدخول": "Login details",
    "كلمة المرور الحالية": "Current password", "كلمة المرور الجديدة": "New password",
    "اتركها فاضية إذا ما تبي تغيرها)": "leave empty to keep it)", "تحديث بيانات الدخول": "Update login details",
    "حفظ الإعدادات": "Save settings", "تم حفظ الإعدادات": "Settings saved", "رقم الواتساب غير صحيح": "Invalid WhatsApp number",
    "كلمة المرور الحالية غير صحيحة": "Current password is incorrect",
    "كلمة المرور الجديدة لازم تكون 6 خانات على الأقل": "The new password must be at least 6 characters",
    "اكتب اسم المستخدم": "Enter a username", "تم تحديث بيانات الدخول": "Login details updated",
    # admin.js strings
    "الحجم بالعربي (50 مل)": "Size in Arabic (50 مل)", "Size (50 ml)": "Size (50 ml)", "بعد التخفيض ": "Sale price",
    "المنطقة بالعربي": "Area in Arabic", "Area (English)": "Area (English)", "سعر التوصيل": "Delivery price",
}


def tr(text: str, lang: str = "ar", **kw) -> str:
    if lang == "en":
        if text not in EN and _DEBUG:
            print(f"[admin_i18n] missing EN: {text!r}", flush=True)
        text = EN.get(text, text)
        kw = {k: (EN.get(v, v) if isinstance(v, str) else v) for k, v in kw.items()}
    return text.format(**kw) if kw else text
