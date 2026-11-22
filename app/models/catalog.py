from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base
from app.services.timeutil import now_local


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name_ar = Column(String(150), nullable=False)
    name_en = Column(String(150), nullable=False)
    image = Column(String(255), nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name_ar = Column(String(200), nullable=False)
    name_en = Column(String(200), nullable=False)
    desc_ar = Column(Text, nullable=True)
    desc_en = Column(Text, nullable=True)
    image = Column(String(255), nullable=True)
    # [{"id","label_ar","label_en","price","sale_price","stock"}]
    variants = Column(JSON, nullable=False, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=now_local, nullable=False)
    category = relationship("Category", back_populates="products")
