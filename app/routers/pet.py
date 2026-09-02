import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from starlette.concurrency import run_in_threadpool

from app.dependencies import (
    get_current_user,
    get_current_user_for_page,
    get_repository,
    request_payload,
    templates,
    verify_csrf,
)
from app.models.user import UserRecord
from app.services.google_sheets import GoogleSheetsError, GoogleSheetsRepository
from app.services.pet_service import apply_pet_sync, normalize_pet_name


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/pet")
async def pet_page(request: Request, user: UserRecord = Depends(get_current_user_for_page)):
    return templates.TemplateResponse(
        "pet.html",
        {
            "request": request,
            "title": "Mascota",
            "user": user,
            "user_public": user.public_dict(),
        },
    )


@router.get("/api/pet")
async def pet_state(user: UserRecord = Depends(get_current_user)):
    return {"user": user.public_dict()}


@router.patch("/api/pet/name")
async def update_pet_name(
    request: Request,
    user: UserRecord = Depends(get_current_user),
    repo: GoogleSheetsRepository = Depends(get_repository),
):
    await verify_csrf(request)
    payload = await request_payload(request)
    user.pet_name = normalize_pet_name(payload.get("pet_name", payload.get("nombre", "")))
    try:
        await run_in_threadpool(repo.update_user, user)
    except GoogleSheetsError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {"user": user.public_dict()}


@router.post("/api/pet/sync")
async def sync_pet(
    request: Request,
    user: UserRecord = Depends(get_current_user),
    repo: GoogleSheetsRepository = Depends(get_repository),
):
    await verify_csrf(request)
    payload = await request_payload(request)
    logger.info("Sincronización de mascota iniciada para usuario %s", user.username)
    apply_pet_sync(user, payload)
    try:
        await run_in_threadpool(repo.update_user, user)
    except GoogleSheetsError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    logger.info("Sincronización de mascota completada para usuario %s", user.username)
    return {"user": user.public_dict()}
