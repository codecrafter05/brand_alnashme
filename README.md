# Brand Alnashme

متجر عطور بسيط يستقبل الطلبات عبر الواتساب. FastAPI + Jinja2 (HTML) + MySQL.

## تشغيل المشروع (على الماك)
1. شغّل MAMP (MySQL على بورت 8889 — الافتراضي root / root).
2. من التيرمنال داخل مجلد المشروع:
   ```bash
   ./run.sh
   ```
   أول مرة ينشئ الـ venv ويسطّب المكتبات وينشئ قاعدة البيانات `brand_alnashme` والجداول وبيانات تجريبية تلقائياً.
3. المتجر: http://localhost:8000 — لوحة التحكم: http://localhost:8000/admin (admin / admin)

إذا فشل الاتصال بقاعدة البيانات، افتح `.env` وجرّب سطر الـ socket الموجود فيه، أو غيّر البورت حسب إعدادات MAMP عندك.

## الهيكل
```
app/
  main.py            تشغيل التطبيق، الجلسات، تتبع الزوار
  config.py          قراءة .env
  database.py        الاتصال بـ MySQL وإنشاء القاعدة
  models/            catalog (أقسام ومنتجات) · orders (طلبات ومناطق توصيل) · system (إعدادات، أدمن، زيارات)
  routers/
    public.py        صفحات الزبون
    api.py           السلة وإنشاء الطلب (/api/order)
    admin/           الداشبورد، الأقسام، المنتجات، التوصيل، الطلبات، الإعدادات
  services/          pricing (الأسعار والأحجام) · cart · whatsapp · stock · images · analytics · settings · i18n
  templates/public/  واجهة الزبون        templates/admin/  لوحة التحكم
  static/            css · js · img (اللوقو) · demo (صور تجريبية) · uploads (صور الأدمن)
.env                 إعدادات القاعدة والمفتاح السري ورقم الواتساب الافتراضي
```

## ملاحظات
- رقم الواتساب يتغير من لوحة التحكم ← الإعدادات (الافتراضي من `.env`).
- لحذف البيانات التجريبية: ضع `SEED_DEMO=false` في `.env` قبل أول تشغيل على قاعدة جديدة، أو احذف المنتجات والأقسام من اللوحة.
- عند الرفع على سيرفر: غيّر `SECRET_KEY` وكلمة مرور الأدمن، وشغّل `uvicorn app.main:app --host 0.0.0.0 --port 8000` خلف Nginx مع HTTPS.
