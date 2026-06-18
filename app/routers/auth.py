from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.config import get_settings
from app.dependencies import get_current_user, get_repository, request_payload, templates, verify_csrf
from app.models.user import UserRecord
from app.services.auth_service import AuthServiceError, authenticate_user, register_user
from app.services.google_sheets import GoogleSheetsError, GoogleSheetsRepository
from app.services.pet_service import apply_pet_sync
from app.utils.security import create_access_token


router = APIRouter()


def _set_session_cookie(response: RedirectResponse, username: str) -> None:
    settings = get_settings()
    token = create_access_token(
        username,
        settings.SECRET_KEY,
        settings.JWT_ALGORITHM,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    response.set_cookie(
        settings.COOKIE_NAME,
        token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
    )


def _delete_session_cookie(response: RedirectResponse) -> None:
    settings = get_settings()
    response.delete_cookie(settings.COOKIE_NAME)


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "Iniciar sesión"},
    )


@router.post("/login")
async def login(request: Request, repo: GoogleSheetsRepository = Depends(get_repository)):
    await verify_csrf(request)
    payload = await request_payload(request)
    try:
        user = authenticate_user(repo, str(payload.get("username", "")), str(payload.get("password", "")))
    except (AuthServiceError, GoogleSheetsError) as exc:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "title": "Iniciar sesión",
                "error": str(exc),
                "username": payload.get("username", ""),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "title": "Iniciar sesión",
                "error": f"Error en el servidor: {str(exc)}",
                "username": payload.get("username", ""),
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response = RedirectResponse("/pet", status_code=status.HTTP_303_SEE_OTHER)
    _set_session_cookie(response, user.username)
    return response


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": "Registrarse"},
    )


@router.post("/register")
async def register(request: Request, repo: GoogleSheetsRepository = Depends(get_repository)):
    await verify_csrf(request)
    payload = await request_payload(request)
    try:
        user = register_user(repo, str(payload.get("username", "")), str(payload.get("password", "")))
    except (AuthServiceError, GoogleSheetsError) as exc:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "title": "Registrarse",
                "error": str(exc),
                "username": payload.get("username", ""),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "title": "Registrarse",
                "error": f"Error en el servidor: {str(exc)}",
                "username": payload.get("username", ""),
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    response = RedirectResponse("/pet", status_code=status.HTTP_303_SEE_OTHER)
    _set_session_cookie(response, user.username)
    return response


@router.post("/logout")
async def logout(
    request: Request,
    user: UserRecord = Depends(get_current_user),
    repo: GoogleSheetsRepository = Depends(get_repository),
):
    await verify_csrf(request)
    payload = await request_payload(request)
    if payload:
        apply_pet_sync(user, payload)
        try:
            repo.update_user(user)
        except GoogleSheetsError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    _delete_session_cookie(response)
    return response
