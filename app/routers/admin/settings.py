from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AdminUser
from app.security import check_password, hash_password, require_admin, verify_csrf
from app.services import settings as settings_service
from app.services.images import ImageError, delete_upload, save_upload
from app.services.pricing import D
from app.services.whatsapp import normalize_number

from .common import flash, redirect, render_admin

router = APIRouter(prefix="/settings", dependencies=[Depends(require_admin)])

TEXT_FIELDS = [
    "store_name", "tagline_ar", "tagline_en", "announcement_ar", "announcement_en",
    "hero_eyebrow_ar", "hero_eyebrow_en", "hero_title_ar", "hero_title_en",
    "hero_subtitle_ar", "hero_subtitle_en", "hero_button_ar", "hero_button_en",
    "about_title_ar", "about_title_en", "about_text_ar", "about_text_en",
    "contact_phone", "contact_email", "instagram", "tiktok", "snapchat", "facebook", "x_twitter",
    "footer_text_ar", "footer_text_en",
]


@router.get("")
def settings_page(request: Request, db: Session = Depends(get_db)):
    user = db.get(AdminUser, request.session["admin_id"])
    return render_admin(request, db, "admin/settings.html", username=user.username if user else "admin")


@router.post("", dependencies=[Depends(verify_csrf)])
async def save_settings(request: Request, db: Session = Depends(get_db),
                        hero_image: UploadFile = File(None),
                        about_image: UploadFile = File(None)):
    form = await request.form()
    values = {k: str(form.get(k, "")).strip() for k in TEXT_FIELDS}
    wa = normalize_number(str(form.get("whatsapp_number", "")))
    if len(wa) < 8:
        flash(request, "رقم الواتساب غير صحيح", "err")
        return redirect("/admin/settings")
    values["whatsapp_number"] = wa
    values["free_delivery_enabled"] = "1" if form.get("free_delivery_enabled") else "0"
    values["free_delivery_threshold"] = f"{D(form.get('free_delivery_threshold') or 0):.3f}"
    current = settings_service.get_settings(db)
    if hero_image is not None and hero_image.filename:
        try:
            url = await save_upload(hero_image, max_side=2000)
            delete_upload(current.get("hero_image"))
            values["hero_image"] = url
        except ImageError as e:
            flash(request, str(e), "err")
    if about_image is not None and about_image.filename:
        try:
            url = await save_upload(about_image, max_side=2000)
            delete_upload(current.get("about_image"))
            values["about_image"] = url
        except ImageError as e:
            flash(request, str(e), "err")
    settings_service.save_settings(db, values)
    flash(request, "تم حفظ الإعدادات")
    return redirect("/admin/settings")


@router.post("/account", dependencies=[Depends(verify_csrf)])
def change_account(request: Request, username: str = Form(""), current_password: str = Form(""),
                   new_password: str = Form(""), db: Session = Depends(get_db)):
    user = db.get(AdminUser, request.session["admin_id"])
    if not user or not check_password(current_password, user.password_hash):
        flash(request, "كلمة المرور الحالية غير صحيحة", "err")
    elif new_password and len(new_password) < 6:
        flash(request, "كلمة المرور الجديدة لازم تكون 6 خانات على الأقل", "err")
    elif not username.strip():
        flash(request, "اكتب اسم المستخدم", "err")
    else:
        user.username = username.strip()
        if new_password:
            user.password_hash = hash_password(new_password)
            request.session["default_pw"] = check_password("admin", user.password_hash)
        db.commit()
        flash(request, "تم تحديث بيانات الدخول")
    return redirect("/admin/settings")
