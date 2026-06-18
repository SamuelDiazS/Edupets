import json
from typing import Any

from pydantic import BaseModel, Field


def _parse_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_json_dict(value: Any) -> dict[str, Any]:
    if not value:
        return {}
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


class UserRecord(BaseModel):
    username: str
    password_hash: str
    coins: int = 0
    happiness: int = 100
    food: int = 100
    sleep: int = 100
    pet_name: str = "Mi Mascota"
    progress: dict[str, Any] = Field(default_factory=dict)
    tasks: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_sheet_row(cls, row: list[Any]) -> "UserRecord":
        print(f"[DEBUG from_sheet_row] START - row_len: {len(row)}")
        padded = [*row, *[""] * (9 - len(row))]
        print(f"[DEBUG from_sheet_row] padded[1] (password_hash) type: {type(padded[1])}, len: {len(str(padded[1]))}")
        print(f"[DEBUG from_sheet_row] padded[1] first 50 chars: {str(padded[1])[:50]}")
        result = cls(
            username=str(padded[0]).strip(),
            password_hash=str(padded[1]),
            coins=_parse_int(padded[2], 0),
            happiness=_parse_int(padded[3], 100),
            food=_parse_int(padded[4], 100),
            sleep=_parse_int(padded[5], 100),
            pet_name=str(padded[6]).strip() or "Mi Mascota",
            progress=_parse_json_dict(padded[7]),
            tasks=_parse_json_dict(padded[8]),
        )
        print(f"[DEBUG from_sheet_row] SUCCESS - password_hash len: {len(result.password_hash)}")
        return result

    def to_sheet_row(self) -> list[Any]:
        return [
            self.username,
            self.password_hash,
            self.coins,
            self.happiness,
            self.food,
            self.sleep,
            self.pet_name,
            json.dumps(self.progress, ensure_ascii=False),
            json.dumps(self.tasks, ensure_ascii=False),
        ]

    def public_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "coins": self.coins,
            "happiness": self.happiness,
            "food": self.food,
            "sleep": self.sleep,
            "pet_name": self.pet_name,
            "progress": self.progress,
            "tasks": self.tasks,
        }
