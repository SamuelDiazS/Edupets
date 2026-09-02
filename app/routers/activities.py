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
from app.services.activities_service import MODULES, normalize_progress, normalize_tasks, record_level_completion
from app.services.google_sheets import GoogleSheetsError, GoogleSheetsRepository


router = APIRouter()


@router.get("/activities")
async def activities_page(request: Request, user: UserRecord = Depends(get_current_user_for_page)):
    return templates.TemplateResponse(
        "activities.html",
        {
            "request": request,
            "title": "Actividades",
            "user": user,
            "user_public": user.public_dict(),
            "modules": MODULES,
        },
    )


@router.get("/api/activities/state")
async def activities_state(user: UserRecord = Depends(get_current_user)):
    user.progress = normalize_progress(user.progress)
    user.tasks = normalize_tasks(user.tasks)
    return {"user": user.public_dict()}


@router.post("/api/activities/complete")
async def complete_activity(
    request: Request,
    user: UserRecord = Depends(get_current_user),
    repo: GoogleSheetsRepository = Depends(get_repository),
):
    await verify_csrf(request)
    payload = await request_payload(request)
    module = str(payload.get("module", ""))
    try:
        level = int(payload.get("level", 0))
        correct_count = int(payload.get("correct_count", 0))
        result = record_level_completion(user, module, level, correct_count)
        await run_in_threadpool(repo.update_user, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GoogleSheetsError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return {"user": user.public_dict(), **result}
