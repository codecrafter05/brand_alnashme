import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from app import models  # noqa: F401  (registers tables)
from app.config import SECRET_KEY, STATIC_DIR
from app.database import Base, SessionLocal, engine, ensure_database
from app.models import Visit
from app.routers import admin, api, public
from app.security import NotAuthenticated
from app.seed import seed_all
from app.templating import render_public


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_database()
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed_all(db)
    yield


app = FastAPI(title="Brand Alnashme", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, session_cookie="ban_session",
                   max_age=60 * 60 * 24 * 14, same_site="lax")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_SKIP = ("/admin", "/api", "/static", "/lang")
_BOTS = ("bot", "spider", "crawl", "slurp", "monitor")


def _record_visit(vid: str, path: str) -> None:
    with SessionLocal() as db:
        db.add(Visit(visitor_id=vid, path=path[:255]))
        db.commit()


@app.middleware("http")
async def track_visits(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if (request.method == "GET" and response.status_code == 200 and not path.startswith(_SKIP)
            and "text/html" in response.headers.get("content-type", "")):
        ua = request.headers.get("user-agent", "").lower()
        if not any(b in ua for b in _BOTS):
            vid = request.cookies.get("vid") or uuid.uuid4().hex
            try:
                await run_in_threadpool(_record_visit, vid, path)
            except Exception:
                pass
            if not request.cookies.get("vid"):
                response.set_cookie("vid", vid, max_age=60 * 60 * 24 * 365, httponly=True, samesite="lax")
    return response


@app.exception_handler(NotAuthenticated)
async def not_authenticated(request: Request, exc: NotAuthenticated):
    return RedirectResponse("/admin/login", status_code=303)


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    path = request.url.path
    if path.startswith("/api"):
        return JSONResponse({"ok": False, "error": exc.detail}, status_code=exc.status_code)
    if exc.status_code == 404 and not path.startswith(("/admin", "/static")):
        with SessionLocal() as db:
            return render_public(request, db, "public/404.html", status_code=404)
    if exc.status_code == 404:
        return RedirectResponse("/admin", status_code=303) if path.startswith("/admin") else PlainTextResponse("Not found", 404)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


app.include_router(public.router)
app.include_router(api.router)
app.include_router(admin.router)
