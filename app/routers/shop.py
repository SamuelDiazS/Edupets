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
from app.services.shop_service import SHOP_ITEMS, buy_item


router = APIRouter()


@router.get("/shop")
async def shop_page(request: Request, user: UserRecord = Depends(get_current_user_for_page)):
    return templates.TemplateResponse(
        "shop.html",
        {
            "request": request,
            "title": "Tienda",
            "user": user,
            "user_public": user.public_dict(),
            "items": SHOP_ITEMS.values(),
        },
    )


@router.post("/api/shop/buy")
async def buy_shop_item(
    request: Request,
    user: UserRecord = Depends(get_current_user),
    repo: GoogleSheetsRepository = Depends(get_repository),
):
    await verify_csrf(request)
    payload = await request_payload(request)
    try:
        item = buy_item(user, str(payload.get("item_id", "")))
        await run_in_threadpool(repo.update_user, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GoogleSheetsError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {"user": user.public_dict(), "item": item}
