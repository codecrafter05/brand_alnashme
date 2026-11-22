from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ORDER_STATUSES, Order
from app.security import require_admin, verify_csrf
from app.services.stock import change_status
from app.services.whatsapp import wa_link

from .common import STATUS_LABELS, flash, redirect, render_admin

router = APIRouter(prefix="/orders", dependencies=[Depends(require_admin)])
PER_PAGE = 25


@router.get("")
def list_orders(request: Request, status: str = "", q: str = "", page: int = 1, db: Session = Depends(get_db)):
    query = db.query(Order)
    if status in ORDER_STATUSES:
        query = query.filter(Order.status == status)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Order.order_number.like(like), Order.customer_name.like(like),
                                 Order.phone.like(like), Order.email.like(like)))
    total = query.count()
    page = max(1, page)
    orders = query.order_by(Order.id.desc()).offset((page - 1) * PER_PAGE).limit(PER_PAGE).all()
    counts = {s: db.query(Order).filter(Order.status == s).count() for s in ORDER_STATUSES}
    return render_admin(request, db, "admin/orders.html", orders=orders, status=status, q=q, page=page,
                        pages=max(1, -(-total // PER_PAGE)), counts=counts, total_all=sum(counts.values()))


@router.get("/{oid}")
def order_detail(oid: int, request: Request, db: Session = Depends(get_db)):
    order = db.get(Order, oid)
    if not order:
        return redirect("/admin/orders")
    msg = (f"مرحباً {order.customer_name}، تم تأكيد طلبك #{order.order_number} بمبلغ {order.total} د.ب. شكراً لك."
           if order.lang == "ar" else
           f"Hello {order.customer_name}, your order #{order.order_number} ({order.total} BHD) is confirmed. Thank you!")
    return render_admin(request, db, "admin/order_detail.html", o=order, customer_wa=wa_link(order.phone, msg))


@router.post("/{oid}/status", dependencies=[Depends(verify_csrf)])
def set_status(oid: int, request: Request, status: str = Form(""), db: Session = Depends(get_db)):
    order = db.get(Order, oid)
    if order and status in ORDER_STATUSES and status != order.status:
        for text, kw in change_status(db, order, status):
            flash(request, text, "err", **kw)
        flash(request, "تم تغيير حالة الطلب إلى: {status}", status=STATUS_LABELS[status])
    return redirect(f"/admin/orders/{oid}")
