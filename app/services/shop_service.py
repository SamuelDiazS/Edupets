from typing import Any

from app.models.user import UserRecord
from app.services.pet_service import clamp_stat


SHOP_ITEMS: dict[str, dict[str, Any]] = {
    "pollo": {
        "id": "pollo",
        "name": "Pollo",
        "image": "comida.png",
        "price": 20,
        "stat": "food",
        "effect": 20,
        "description": "+20 comida",
    },
    "juguete": {
        "id": "juguete",
        "name": "Juguete",
        "image": "felicidad.png",
        "price": 30,
        "stat": "happiness",
        "effect": 20,
        "description": "+20 felicidad",
    },
    "vive100": {
        "id": "vive100",
        "name": "Vive 100",
        "image": "vive100.png",
        "price": 25,
        "stat": "sleep",
        "effect": 20,
        "description": "+20 sueño",
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
