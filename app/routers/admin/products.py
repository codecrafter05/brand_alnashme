import json
from types import SimpleNamespace

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product
from app.security import require_admin, verify_csrf
from app.services.images import ImageError, delete_upload, save_upload
from app.services.pricing import parse_variants_json

from .common import flash, redirect, render_admin

router = APIRouter(prefix="/products", dependencies=[Depends(require_admin)])


def _categories(db):
    return db.query(Category).order_by(Category.sort_order, Category.id).all()


@router.get("")
def list_products(request: Request, cat: int | None = None, q: str = "", status: str = "",
                  db: Session = Depends(get_db)):
    query = db.query(Product)
    if cat:
        query = query.filter(Product.category_id == cat)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Product.name_ar.like(like), Product.name_en.like(like)))
    if status == "active":
        query = query.filter(Product.is_active.is_(True))
    elif status == "hidden":
        query = query.filter(Product.is_active.is_(False))
    products = query.order_by(Product.id.desc()).all()
    return render_admin(request, db, "admin/products.html", products=products, categories=_categories(db),
                        cat=cat, q=q, status=status)


@router.get("/new")
def new_product(request: Request, cat: int | None = None, db: Session = Depends(get_db)):
    cats = _categories(db)
    if not cats:
        flash(request, "أضف قسم أول قبل ما تضيف منتج", "err")
        return redirect("/admin/categories/new")
    form = SimpleNamespace(id=None, category_id=cat or cats[0].id, name_ar="", name_en="", desc_ar="", desc_en="",
                           image=None, is_active=True, is_featured=False,
                           variants=[{"id": "", "label_ar": "", "label_en": "", "price": "", "sale_price": "", "stock": 0}])
    return render_admin(request, db, "admin/product_form.html", p=form, categories=cats, errors=[])


@router.get("/{pid}/edit")
def edit_product(pid: int, request: Request, db: Session = Depends(get_db)):
    p = db.get(Product, pid)
    if not p:
        return redirect("/admin/products")
    return render_admin(request, db, "admin/product_form.html", p=p, categories=_categories(db), errors=[])


async def _save(request, db, pid, data, image, remove_image):
    product = db.get(Product, pid) if pid else None
    variants, errors = parse_variants_json(data["variants_json"], product.variants if product else None)
    if not data["name_ar"].strip() or not data["name_en"].strip():
        errors.append(("اكتب اسم المنتج بالعربي والإنجليزي", {}))
    if not db.get(Category, data["category_id"] or 0):
        errors.append(("اختر القسم", {}))
    if errors:
        try:
            raw_variants = json.loads(data["variants_json"] or "[]")
        except ValueError:
            raw_variants = []
        form = SimpleNamespace(
            id=pid, category_id=data["category_id"], name_ar=data["name_ar"], name_en=data["name_en"],
            desc_ar=data["desc_ar"], desc_en=data["desc_en"], image=product.image if product else None,
            is_active=data["is_active"], is_featured=data["is_featured"], variants=raw_variants,
        )
        return render_admin(request, db, "admin/product_form.html", status_code=422, p=form,
                            categories=_categories(db), errors=errors)
    if product is None:
        product = Product()
        db.add(product)
    product.category_id = data["category_id"]
    product.name_ar, product.name_en = data["name_ar"].strip(), data["name_en"].strip()
    product.desc_ar, product.desc_en = data["desc_ar"].strip() or None, data["desc_en"].strip() or None
    product.is_active, product.is_featured = data["is_active"], data["is_featured"]
    product.variants = variants
    if remove_image:
        delete_upload(product.image)
        product.image = None
    if image is not None and image.filename:
        try:
            url = await save_upload(image, max_side=1600)
            delete_upload(product.image)
            product.image = url
        except ImageError as e:
            flash(request, str(e), "err")
    db.commit()
    flash(request, "تم حفظ المنتج")
    return redirect("/admin/products")


def _data(category_id, name_ar, name_en, desc_ar, desc_en, is_active, is_featured, variants_json):
    return {
        "category_id": category_id, "name_ar": name_ar, "name_en": name_en, "desc_ar": desc_ar,
        "desc_en": desc_en, "is_active": bool(is_active), "is_featured": bool(is_featured),
        "variants_json": variants_json,
    }


@router.post("/new", dependencies=[Depends(verify_csrf)])
async def create_product(request: Request, category_id: int = Form(0), name_ar: str = Form(""),
                         name_en: str = Form(""), desc_ar: str = Form(""), desc_en: str = Form(""),
                         is_active: str = Form(None), is_featured: str = Form(None),
                         variants_json: str = Form("[]"), image: UploadFile = File(None),
                         db: Session = Depends(get_db)):
    return await _save(request, db, None, _data(category_id, name_ar, name_en, desc_ar, desc_en,
                                                is_active, is_featured, variants_json), image, False)


@router.post("/{pid}/edit", dependencies=[Depends(verify_csrf)])
async def update_product(pid: int, request: Request, category_id: int = Form(0), name_ar: str = Form(""),
                         name_en: str = Form(""), desc_ar: str = Form(""), desc_en: str = Form(""),
                         is_active: str = Form(None), is_featured: str = Form(None),
                         variants_json: str = Form("[]"), remove_image: str = Form(None),
                         image: UploadFile = File(None), db: Session = Depends(get_db)):
    if not db.get(Product, pid):
        return redirect("/admin/products")
    return await _save(request, db, pid, _data(category_id, name_ar, name_en, desc_ar, desc_en,
                                               is_active, is_featured, variants_json), image, bool(remove_image))


@router.post("/{pid}/toggle", dependencies=[Depends(verify_csrf)])
def toggle_product(pid: int, field: str = Form("is_active"), db: Session = Depends(get_db)):
    p = db.get(Product, pid)
    if p and field in ("is_active", "is_featured"):
        setattr(p, field, not getattr(p, field))
        db.commit()
    return redirect("/admin/products")


@router.post("/{pid}/delete", dependencies=[Depends(verify_csrf)])
def delete_product(pid: int, request: Request, db: Session = Depends(get_db)):
    p = db.get(Product, pid)
    if p:
        delete_upload(p.image)
        db.delete(p)
        db.commit()
        flash(request, "تم حذف المنتج (الطلبات القديمة تبقى محفوظة)")
    return redirect("/admin/products")
