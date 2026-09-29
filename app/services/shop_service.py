from typing import Any

from app.models.user import UserRecord
from app.services.pet_service import clamp_stat


SHOP_ITEMS: dict[str, dict[str, Any]] = {
    "pollo": {
        "id": "pollo",
        "name": "Comida",
        "image": "pescado.png",
        "price": 20,
        "stat": "food",
        "effect": 20,
        "description": "+20 comida",
    },
    "juguete": {
        "id": "juguete",
        "name": "Juguete",
        "image": "juguete.png",
        "price": 30,
        "stat": "happiness",
        "effect": 20,
        "description": "+20 felicidad",
    },
    "caramelos": {
        "id": "caramelos",
        "name": "Caramelos",
        "image": "caramelos.png",
        "price": 25,
        "stat": "sleep",
        "effect": 20,
        "description": "+20 sueño",
    },
}

PET_ITEMS: dict[str, dict[str, Any]] = {
    "oso": {
        "id": "oso",
        "name": "Oso",
        "image": "oso.png",
        "price": 100,
        "description": "Un compañero fuerte y tranquilo.",
    },
    "zorro": {
        "id": "zorro",
        "name": "Zorro",
        "image": "zorro.png",
        "price": 150,
        "description": "Un compañero curioso y ágil.",
    },
}


def buy_item(user: UserRecord, item_id: str) -> dict[str, Any]:
    item = SHOP_ITEMS.get(item_id)
    if not item:
        raise ValueError("Producto no valido.")
    if user.coins < item["price"]:
        raise ValueError("No tienes monedas suficientes.")

    user.coins -= item["price"]
    current_value = getattr(user, item["stat"])
    setattr(user, item["stat"], clamp_stat(current_value + item["effect"]))
    return item
