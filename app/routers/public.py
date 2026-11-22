from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Product
from app.services import pricing
from app.services.i18n import DEFAULT_LANG, LANGS
from app.templating import render_public

router = APIRouter()


def visible_products(db: Session):
    return (
        db.query(Product).join(Category, Product.category_id == Category.id)
        .filter(Product.is_active.is_(True), Category.is_active.is_(True))
    )


def active_categories(db: Session):
    return db.query(Category).filter(Category.is_active.is_(True)).order_by(Category.sort_order, Category.id).all()


def sort_products(items, sort: str):
    if sort == "price_asc":
        return sorted(items, key=lambda p: pricing.summary(p)["price"])
    if sort == "price_desc":
        return sorted(items, key=lambda p: pricing.summary(p)["price"], reverse=True)
    return items  # newest first (already ordered by query)


@router.get("/lang/{code}")
def switch_lang(code: str, next: str = "/"):
    if code not in LANGS:
        code = DEFAULT_LANG
    target = next if next.startswith("/") and not next.startswith("//") and not urlparse(next).netloc else "/"
    resp = RedirectResponse(target, status_code=303)
    resp.set_cookie("lang", code, max_age=60 * 60 * 24 * 365, samesite="lax")
    return resp


@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    base = visible_products(db).order_by(Product.created_at.desc(), Product.id.desc())
    featured = base.filter(Product.is_featured.is_(True)).limit(8).all()
    if len(featured) < 8:  # pad with the newest products so the grid never ends with an orphan card
        have = {p.id for p in featured}
        featured += [p for p in base.limit(16).all() if p.id not in have][: 8 - len(featured)]
    if len(featured) >= 4:
        featured = featured[: len(featured) // 4 * 4]
    sale = [p for p in base.all() if pricing.has_sale(p)][:4]
    return render_public(request, db, "public/home.html", categories=active_categories(db),
                         featured=featured, sale_products=sale)


@router.get("/categories")
def categories_page(request: Request, db: Session = Depends(get_db)):
    cats = active_categories(db)
    counts = {c.id: visible_products(db).filter(Product.category_id == c.id).count() for c in cats}
    return render_public(request, db, "public/categories.html", categories=cats, counts=counts)


@router.get("/products")
def products_page(request: Request, q: str = "", cat: int | None = None, sort: str = "new",
                  db: Session = Depends(get_db)):
    query = visible_products(db)
    if cat:
        query = query.filter(Product.category_id == cat)
    q = q.strip()[:80]
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Product.name_ar.like(like), Product.name_en.like(like)))
    items = sort_products(query.order_by(Product.created_at.desc(), Product.id.desc()).all(), sort)
    return render_public(request, db, "public/products.html", products=items, categories=active_categories(db),
                         current_cat=cat, q=q, sort=sort)


@router.get("/category/{category_id}")
def category_page(category_id: int, request: Request, sort: str = "new", db: Session = Depends(get_db)):
    cat = db.get(Category, category_id)
    if not cat or not cat.is_active:
        raise HTTPException(404)
    items = visible_products(db).filter(Product.category_id == cat.id) \
        .order_by(Product.created_at.desc(), Product.id.desc()).all()
    return render_public(request, db, "public/category.html", category=cat,
                         products=sort_products(items, sort), sort=sort)


@router.get("/sale")
def sale_page(request: Request, db: Session = Depends(get_db)):
    items = [p for p in visible_products(db).order_by(Product.created_at.desc()).all() if pricing.has_sale(p)]
    return render_public(request, db, "public/sale.html", products=items)


@router.get("/product/{product_id}")
def product_page(product_id: int, request: Request, db: Session = Depends(get_db)):
    p = visible_products(db).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404)
    related = visible_products(db).filter(Product.category_id == p.category_id, Product.id != p.id) \
        .order_by(Product.created_at.desc()).limit(4).all()
    return render_public(request, db, "public/product.html", product=p, related=related)
