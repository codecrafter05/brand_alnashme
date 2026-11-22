import secrets
import time

import bcrypt
from fastapi import Form, HTTPException, Request


class NotAuthenticated(Exception):
    pass


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()


def check_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode(), hashed.encode())
    except ValueError:
        return False


def csrf_token(request: Request) -> str:
    tok = request.session.get("csrf")
    if not tok:
        tok = secrets.token_urlsafe(24)
        request.session["csrf"] = tok
    return tok


def verify_csrf(request: Request, csrf_token_field: str = Form("", alias="csrf_token")):
    expected = request.session.get("csrf")
    if not expected or not secrets.compare_digest(expected, csrf_token_field or ""):
        raise HTTPException(status_code=403, detail="CSRF check failed")


def require_admin(request: Request):
    if not request.session.get("admin_id"):
        raise NotAuthenticated()
    return request.session["admin_id"]


# --- tiny in-memory rate limiter (per process) ---
_hits: dict = {}


def rate_limited(key: str, limit: int, window: int) -> bool:
    now = time.time()
    bucket = [t for t in _hits.get(key, []) if now - t < window]
    if len(bucket) >= limit:
        _hits[key] = bucket
        return True
    bucket.append(now)
    _hits[key] = bucket
    return False


def client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
