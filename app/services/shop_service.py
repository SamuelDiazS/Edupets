from typing import Any

SHOP_ITEMS: dict[str, dict[str, Any]] = {
    "pollo": {
        "id": "pollo",
        "name": "Comida",
        "database_name": "Comida",
        "image": "pescado.png",
        "stat": "food",
        "effect": 20,
        "description": "+20 comida",
    },
    "juguete": {
        "id": "juguete",
        "name": "Juguete",
        "database_name": "Juguete",
        "image": "juguete.png",
        "stat": "happiness",
        "effect": 20,
        "description": "+20 felicidad",
    },
    "caramelos": {
        "id": "caramelos",
        "name": "Caramelos",
        "database_name": "caramelos",
        "image": "caramelos.png",
        "stat": "sleep",
        "effect": 20,
        "description": "+20 sueño",
    },
}

PET_ITEMS: dict[str, dict[str, Any]] = {
    "oso": {
        "id": "oso",
        "name": "Oso",
        "database_name": "Oso",
        "image": "oso.png",
        "description": "Un compañero fuerte y tranquilo.",
    },
    "zorro": {
        "id": "zorro",
        "name": "Zorro",
        "database_name": "Zorro",
        "image": "zorro.png",
        "description": "El zorro fenek representa la astucia, la inteligencia, la adaptabilidad y la flexibilidad ante los cambios",
    },
    "pinguino": {
        "id": "pinguino",
        "name":"pinguino"
        "database_name":"pinguino"
        "image":"pet.png"
        "description":"pinguino parchao y estudioso"   
    }
     "nutria":{
     "id":"nutria"
     "name":"nutria"
     "database_name":"nutria"
     "image":"nutria.png"
     "description":"La nutria representa la alegría, la curiosidad, la adaptabilidad y la libertad junto a la salud de los ecosistemas acuaticos y el equilibrio natural el Colombia"
    
}

}


def build_shop_catalog(product_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    prices = {str(row["name"]).casefold(): int(row["price"]) for row in product_rows}
    items = [
        {**item, "price": prices[item["database_name"].casefold()]}
        for item in SHOP_ITEMS.values()
        if item["database_name"].casefold() in prices
    ]
    pets = [
        {**pet, "price": prices[pet["database_name"].casefold()]}
        for pet in PET_ITEMS.values()
        if pet["database_name"].casefold() in prices
    ]
    return items, pets
