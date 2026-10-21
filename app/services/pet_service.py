from typing import Any

from app.models.user import UserRecord
from app.services.activities_service import normalize_progress, normalize_tasks


STAT_FIELDS = {
    "happiness": "happiness",
    "felicidad": "happiness",
    "food": "food",
    "comida": "food",
    "sleep": "sleep",
    "sueno": "sleep",
    "sueño": "sleep",
}

PET_IMAGES = {
    "pinguino": "images/pet.png",
    "oso": "images/oso.png",
    "zorro": "images/zorro.png",
    "salmandra": "images/ nutria.png"
}


def pet_image_path(pet_type: Any) -> str:
    return PET_IMAGES.get(str(pet_type or ""), PET_IMAGES["pinguino"])


def clamp_stat(value: Any) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = 0
    return max(0, min(100, number))


def normalize_pet_name(value: Any) -> str:
    name = str(value or "").strip()
    if not name:
        return "Mi Mascota"
    return name[:30]


def prepare_user_state(user: UserRecord) -> UserRecord:
    user.happiness = clamp_stat(user.happiness)
    user.food = clamp_stat(user.food)
    user.sleep = clamp_stat(user.sleep)
    user.pet_name = normalize_pet_name(user.pet_name)
    user.progress = normalize_progress(user.progress)
    user.tasks = normalize_tasks(user.tasks)
    return user


def apply_pet_sync(user: UserRecord, payload: dict[str, Any]) -> UserRecord:
    for incoming_key, attr in STAT_FIELDS.items():
        if incoming_key in payload:
            setattr(user, attr, clamp_stat(payload[incoming_key]))

    if "pet_name" in payload or "nombre" in payload:
        user.pet_name = normalize_pet_name(payload.get("pet_name", payload.get("nombre")))

    return prepare_user_state(user)
