from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, Numeric, String, Text

from app.database import Base
from app.services.timeutil import now_local

ORDER_STATUSES = ("new", "confirmed", "delivered", "cancelled")


class DeliveryZone(Base):
    __tablename__ = "delivery_zones"

    id = Column(Integer, primary_key=True)
    name_ar = Column(String(150), nullable=False)
    name_en = Column(String(150), nullable=False)
    price = Column(Numeric(10, 3), nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    order_number = Column(String(20), unique=True, index=True)
    status = Column(String(20), default="new", nullable=False, index=True)
    customer_name = Column(String(150), nullable=False)
    email = Column(String(190), nullable=False)
    phone = Column(String(40), nullable=False)
    zone_name = Column(String(200), nullable=False)  # Arabic name
    zone_name_en = Column(String(200), nullable=True)
    house = Column(String(80), nullable=False)
    road = Column(String(80), nullable=False)
    block = Column(String(80), nullable=False)
    note = Column(Text, nullable=True)
    # snapshot: [{"product_id","variant_id","name_ar","name_en","label_ar","label_en","price","qty"}]
    items = Column(JSON, nullable=False, default=list)
    subtotal = Column(Numeric(10, 3), nullable=False, default=0)
    delivery_fee = Column(Numeric(10, 3), nullable=False, default=0)
    total = Column(Numeric(10, 3), nullable=False, default=0)
    lang = Column(String(5), default="ar", nullable=False)
    stock_deducted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=now_local, nullable=False, index=True)
    updated_at = Column(DateTime, default=now_local, onupdate=now_local, nullable=False)
