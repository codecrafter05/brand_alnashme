import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@127.0.0.1:8889/brand_alnashme?charset=utf8mb4",
)
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
SEED_DEMO = os.getenv("SEED_DEMO", "true").lower() in ("1", "true", "yes")
DEFAULT_WHATSAPP = os.getenv("WHATSAPP_NUMBER", "97337331306")
TIMEZONE = "Asia/Bahrain"

STATIC_DIR = APP_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
TEMPLATES_DIR = APP_DIR / "templates"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
