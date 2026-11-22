from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product
from app.security import require_admin, verify_csrf
from app.services.images import ImageError, delete_upload, save_upload

from .common import flash, redirect, render_admin

router = APIRouter(prefix="/categories", dependencies=[Depends(require_admin)])


def _ordered(db):
    return db.query(Category).order_by(Category.sort_order, Category.id).all()


@router.get("")
def list_categories(request: Request, db: Session = Depends(get_db)):
    counts = dict(db.query(Product.category_id, func.count(Product.id)).group_by(Product.category_id).all())
    return render_admin(request, db, "admin/categories.html", categories=_ordered(db), counts=counts)


@router.get("/new")
def new_category(request: Request, db: Session = Depends(get_db)):
    return render_admin(request, db, "admin/category_form.html", cat=None)


@router.get("/{cid}/edit")
def edit_category(cid: int, request: Request, db: Session = Depends(get_db)):
    cat = db.get(Category, cid)
    if not cat:
        return redirect("/admin/categories")
    return render_admin(request, db, "admin/category_form.html", cat=cat)


async def _save(request, db, cat, name_ar, name_en, is_active, image, remove_image):
    if not name_ar.strip() or not name_en.strip():
        flash(request, "اكتب اسم القسم بالعربي والإنجليزي", "err")
        return False
    creating = cat is None
    if creating:
        cat = Category(sort_order=(db.query(func.max(Category.sort_order)).scalar() or 0) + 1)
        db.add(cat)
    cat.name_ar, cat.name_en, cat.is_active = name_ar.strip(), name_en.strip(), bool(is_active)
    if remove_image:
        delete_upload(cat.image)
        cat.image = None
    if image is not None and image.filename:
        try:
            url = await save_upload(image, max_side=1400)
            delete_upload(cat.image)
            cat.image = url
        except ImageError as e:
            flash(request, str(e), "err")
    db.commit()
    return True


@router.post("/new", dependencies=[Depends(verify_csrf)])
async def create_category(request: Request, name_ar: str = Form(""), name_en: str = Form(""),
                          is_active: str = Form(None), image: UploadFile = File(None),
                          db: Session = Depends(get_db)):
    if await _save(request, db, None, name_ar, name_en, is_active, image, False):
        flash(request, "تم إضافة القسم")
        return redirect("/admin/categories")
    return redirect("/admin/categories/new")


@router.post("/{cid}/edit", dependencies=[Depends(verify_csrf)])
async def update_category(cid: int, request: Request, name_ar: str = Form(""), name_en: str = Form(""),
                          is_active: str = Form(None), remove_image: str = Form(None),
                          image: UploadFile = File(None), db: Session = Depends(get_db)):
    cat = db.get(Category, cid)
    if not cat:
        return redirect("/admin/categories")
    if await _save(request, db, cat, name_ar, name_en, is_active, image, bool(remove_image)):
        flash(request, "تم حفظ القسم")
        return redirect("/admin/categories")
    return redirect(f"/admin/categories/{cid}/edit")


@router.post("/{cid}/move", dependencies=[Depends(verify_csrf)])
def move_category(cid: int, direction: str = Form("up"), db: Session = Depends(get_db)):
    cats = _ordered(db)
    for i, c in enumerate(cats):
        c.sort_order = i
    idx = next((i for i, c in enumerate(cats) if c.id == cid), None)
    if idx is not None:
        j = idx - 1 if direction == "up" else idx + 1
        if 0 <= j < len(cats):
            cats[idx].sort_order, cats[j].sort_order = cats[j].sort_order, cats[idx].sort_order
    db.commit()
    return redirect("/admin/categories")


@router.post("/{cid}/toggle", dependencies=[Depends(verify_csrf)])
def toggle_category(cid: int, db: Session = Depends(get_db)):
    cat = db.get(Category, cid)
    if cat:
        cat.is_active = not cat.is_active
        db.commit()
    return redirect("/admin/categories")


@router.post("/{cid}/delete", dependencies=[Depends(verify_csrf)])
def delete_category(cid: int, request: Request, db: Session = Depends(get_db)):
    cat = db.get(Category, cid)
    if not cat:
        return redirect("/admin/categories")
    if db.query(Product).filter(Product.category_id == cid).count():
        flash(request, "ما تقدر تحذف قسم فيه منتجات. انقل المنتجات أو احذفها أول، أو اخفي القسم.", "err")
    else:
        delete_upload(cat.image)
        db.delete(cat)
        db.commit()
        flash(request, "تم حذف القسم")
    return redirect("/admin/categories")
