from typing import Any

from pydantic import BaseModel, Field


class UserRecord(BaseModel):
    username: str
    password_hash: str
    coins: int = 0
    happiness: int = 100
    food: int = 100
    sleep: int = 100
    pet_name: str = "Mi Mascota"
    pet_type: str = "predeterminada"
    owned_pets: list[str] = Field(default_factory=list)
    inventory: list[dict[str, Any]] = Field(default_factory=list)
    progress: dict[str, Any] = Field(default_factory=dict)
    tasks: dict[str, Any] = Field(default_factory=dict)

    def public_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "coins": self.coins,
            "happiness": self.happiness,
            "food": self.food,
            "sleep": self.sleep,
            "pet_name": self.pet_name,
            "pet_type": self.pet_type,
            "owned_pets": self.owned_pets,
            "inventory": self.inventory,
            "progress": self.progress,
            "tasks": self.tasks,
        }
