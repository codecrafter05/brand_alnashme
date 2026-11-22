from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AdminUser
from app.security import check_password, client_ip, csrf_token, rate_limited, verify_csrf
from app.templating import templates

from .common import i18n_ctx, redirect

router = APIRouter()


@router.get("/login")
def login_page(request: Request):
    if request.session.get("admin_id"):
        return redirect("/admin")
    return templates.TemplateResponse(request, "admin/login.html", {"request": request, "csrf": csrf_token(request), "error": None, **i18n_ctx(request)})


@router.post("/login", dependencies=[Depends(verify_csrf)])
def login(request: Request, username: str = Form(""), password: str = Form(""), db: Session = Depends(get_db)):
    if rate_limited(f"login:{client_ip(request)}", limit=10, window=600):
        error = "محاولات كثيرة، حاول بعد شوي"
    else:
        user = db.query(AdminUser).filter(AdminUser.username == username.strip()).first()
        if user and check_password(password, user.password_hash):
            request.session.clear()
            request.session["admin_id"] = user.id
            request.session["default_pw"] = check_password("admin", user.password_hash)
            return redirect("/admin")
        error = "اسم المستخدم أو كلمة المرور غير صحيحة"
    return templates.TemplateResponse(
        request, "admin/login.html",
        {"request": request, "csrf": csrf_token(request), "error": error, **i18n_ctx(request)}, status_code=401,
    )


@router.post("/logout", dependencies=[Depends(verify_csrf)])
def logout(request: Request):
    request.session.clear()
    return redirect("/admin/login")


@router.get("/lang/{code}")
def switch_lang(code: str, next: str = "/admin"):
    target = next if next.startswith("/admin") and not next.startswith("//") else "/admin"
    resp = redirect(target)
    resp.set_cookie("alang", "en" if code == "en" else "ar", max_age=60 * 60 * 24 * 365, samesite="lax")
    return resp
