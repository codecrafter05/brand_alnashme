from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

Base = declarative_base()

_url = make_url(DATABASE_URL)
_kwargs = {"pool_pre_ping": True}
if _url.get_backend_name() == "mysql":
    _kwargs["pool_recycle"] = 3600
elif _url.get_backend_name() == "sqlite":
    _kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_database():
    """Create the MySQL database if it does not exist yet (utf8mb4)."""
    if _url.get_backend_name() != "mysql":
        return
    import pymysql

    params = dict(
        user=_url.username,
        password=_url.password or "",
        charset="utf8mb4",
    )
    sock = _url.query.get("unix_socket")
    if sock:
        params["unix_socket"] = sock
    else:
        params["host"] = _url.host or "127.0.0.1"
        params["port"] = _url.port or 3306
    conn = pymysql.connect(**params)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{_url.database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
    finally:
        conn.close()
