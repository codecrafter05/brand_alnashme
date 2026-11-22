from sqlalchemy import Column, DateTime, Integer, String, Text, Date

from app.database import Base
from app.services.timeutil import now_local, today_local


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String(80), primary_key=True)
    value = Column(Text, nullable=True)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    visitor_id = Column(String(40), nullable=False, index=True)
    day = Column(Date, default=today_local, nullable=False, index=True)
    path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=now_local, nullable=False)
