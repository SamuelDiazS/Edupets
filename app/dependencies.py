import logging
import secrets
from functools import lru_cache
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from starlette.concurrency import run_in_threadpool
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.models.user import UserRecord
from app.services.google_sheets import GoogleSheetsError, GoogleSheetsRepository
from app.services.pet_service import prepare_user_state
from app.utils.security import decode_access_token


settings = get_settings()
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))
logger = logging.getLogger(__name__)


@lru_cache
def get_repository() -> GoogleSheetsRepository:
    return GoogleSheetsRepository(get_settings())


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)


async def request_payload(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            payload = await request.json()
        except Exception:
            return {}
        return payload if isinstance(payload, dict) else {}
    if "form" in content_type:
        form = await request.form()
        return dict(form)
    return {}


async def verify_csrf(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS", "TRACE"}:
        return

    settings = get_settings()
    cookie_token = request.cookies.get(settings.CSRF_COOKIE_NAME)
    submitted_token = request.headers.get("x-csrf-token")

    if not submitted_token:
        payload = await request_payload(request)
        submitted_token = str(payload.get("csrf_token", ""))

    if not cookie_token or not submitted_token or not secrets.compare_digest(cookie_token, submitted_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF invalido.")


async def get_current_user(
    request: Request,
    repo: GoogleSheetsRepository = Depends(get_repository),
) -> UserRecord:
    settings = get_settings()
    username = getattr(request.state, "username", None)
    if not username:
        token = request.cookies.get(settings.COOKIE_NAME)
        payload = decode_access_token(token or "", settings.SECRET_KEY, settings.JWT_ALGORITHM)
        username = payload.get("sub") if payload else None

    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado.")

    try:
        logger.info("Buscando usuario autenticado %s en Google Sheets", username)
        found = await run_in_threadpool(repo.get_user, username)
    except GoogleSheetsError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Error obteniendo el usuario autenticado %s", username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo cargar la sesión.",
        ) from exc

    if not found:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado.")

    _, user = found
    return prepare_user_state(user)


async def get_current_user_for_page(
    request: Request,
    repo: GoogleSheetsRepository = Depends(get_repository),
) -> UserRecord:
    try:
        return await get_current_user(request, repo)
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            raise HTTPException(
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Location": "/login"},
            ) from exc
        raise
