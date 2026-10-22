from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import (
    get_current_user,
    get_current_user_for_page,
    get_repository,
    request_payload,
    templates,
    verify_csrf,
)
from app.models.user import UserRecord
from database.repository import DatabaseRepository, RepositoryError
from app.services.shop_service import PET_ITEMS, SHOP_ITEMS, build_shop_catalog


router = APIRouter()


@router.get("/shop")
async def shop_page(
    request: Request,
    user: UserRecord = Depends(get_current_user_for_page),
    repo: DatabaseRepository = Depends(get_repository),
):
    try:
        items, pets = build_shop_catalog(await repo.get_products())
    except RepositoryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    inventory_counts = {entry["item_id"]: entry["quantity"] for entry in user.inventory}
    items = [{**item, "quantity": inventory_counts.get(item["id"], 0)} 
    for item in items]
    return templates.TemplateResponse(
        "shop.html",
        {
            "request": request,
            "title": "Tienda",
            "user": user,
            "user_public": user.public_dict(),
            "items": items,
            "pets": pets,
        },
    )


@router.post("/api/shop/buy")
async def buy_shop_item(
    request: Request,
    user: UserRecord = Depends(get_current_user),
    repo: DatabaseRepository = Depends(get_repository),
):
    await verify_csrf(request)
    payload = await request_payload(request)
    try:
        item = SHOP_ITEMS.get(str(payload.get("item_id", "")))
        if item is None:
            raise ValueError("Producto no válido.")
        result = await repo.purchase_item(user.username, item["database_name"])
        user.coins = result["coins"]
        user.inventory = result["inventory"]
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {"user": user.public_dict(), "item": {**item, "price": result["price"]}}


@router.post("/api/shop/pet")
async def select_shop_pet(
    request: Request,
    user: UserRecord = Depends(get_current_user),
    repo: DatabaseRepository = Depends(get_repository),
):
    await verify_csrf(request)
    payload = await request_payload(request)
    pet = PET_ITEMS.get(str(payload.get("pet_id", "")))
    if not pet:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mascota no válida.")

    try:
        purchased = await repo.purchase_pet(user.username, pet["id"], pet["database_name"])
        found = await repo.get_user(user.username)
        if found is None:
            raise RepositoryError("No se encontró el usuario después de la compra.")
        _, updated_user = found
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RepositoryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return {"user": updated_user.public_dict(), "item": pet, "purchased": purchased}
