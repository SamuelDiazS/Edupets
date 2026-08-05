import secrets

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.dependencies import new_csrf_token, templates
from app.routers import activities, auth, pet, shop
from app.utils.security import decode_access_token


settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
app.include_router(auth.router)
app.include_router(pet.router)
app.include_router(activities.router)
app.include_router(shop.router)


@app.middleware("http")
async def session_context_middleware(request: Request, call_next):
    csrf_token = request.cookies.get(settings.CSRF_COOKIE_NAME) or new_csrf_token()
    request.state.csrf_token = csrf_token
    request.state.username = None

    token = request.cookies.get(settings.COOKIE_NAME)
    if token:
        payload = decode_access_token(token, settings.SECRET_KEY, settings.JWT_ALGORITHM)
        if payload:
            request.state.username = payload.get("sub")

    response = await call_next(request)
    if not request.cookies.get(settings.CSRF_COOKIE_NAME):
        response.set_cookie(
            settings.CSRF_COOKIE_NAME,
            csrf_token,
            httponly=False,
            secure=settings.COOKIE_SECURE,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    return response


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Edupets"},
    )


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}


@app.exception_handler(303)
async def redirect_exception_handler(request: Request, exc):  # pragma: no cover
    location = exc.headers.get("Location", "/login")
    return RedirectResponse(location, status_code=303)
