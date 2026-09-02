from copy import deepcopy
from typing import Any

from app.models.user import UserRecord


MODULES = {
    "sumas": {"label": "Sumas", "symbol": "+"},
    "restas": {"label": "Restas", "symbol": "-"},
    "multiplicacion": {"label": "Multiplicación", "symbol": "×"},
    "division": {"label": "División", "symbol": "÷"},
}

DEFAULT_TASKS: dict[str, dict[str, Any]] = {
    "sumas": {
        "label": "Completa 5 sumas",
        "target": 5,
        "progress": 0,
        "reward": 15,
        "claimed": False,
    },
    "restas": {
        "label": "Completa 5 restas",
        "target": 5,
        "progress": 0,
        "reward": 15,
        "claimed": False,
    },
    "multiplicacion": {
        "label": "Completa 5 multiplicaciones",
        "target": 5,
        "progress": 0,
        "reward": 20,
        "claimed": False,
    },
    "division": {
        "label": "Completa 5 divisiones",
        "target": 5,
        "progress": 0,
        "reward": 20,
        "claimed": False,
    },
}


def default_progress() -> dict[str, Any]:
    return {"completed": {module: [] for module in MODULES}}


def normalize_progress(progress: dict[str, Any] | None) -> dict[str, Any]:
    normalized = default_progress()
    if isinstance(progress, dict):
        completed = progress.get("completed", {})
        if isinstance(completed, dict):
            for module in MODULES:
                levels = completed.get(module, [])
                if isinstance(levels, list):
                    normalized["completed"][module] = sorted({int(level) for level in levels if str(level).isdigit()})
    return normalized


def normalize_tasks(tasks: dict[str, Any] | None) -> dict[str, Any]:
    normalized = deepcopy(DEFAULT_TASKS)
    if isinstance(tasks, dict):
        for key, template in normalized.items():
            incoming = tasks.get(key, {})
            if not isinstance(incoming, dict):
                continue
            template["progress"] = max(0, min(int(incoming.get("progress", 0)), template["target"]))
            template["claimed"] = bool(incoming.get("claimed", False))
    return normalized


def record_level_completion(
    user: UserRecord,
    module: str,
    level: int,
    correct_count: int,
) -> dict[str, Any]:
    if module not in MODULES:
        raise ValueError("Modulo no valido.")
    if level < 1 or level > 5:
        raise ValueError("Nivel no valido.")

    progress = normalize_progress(user.progress)
    tasks = normalize_tasks(user.tasks)
    completed_levels = set(progress["completed"][module])
    reward = 0

    reward += 10 + level * 2
    if level not in completed_levels:
        completed_levels.add(level)
        progress["completed"][module] = sorted(completed_levels)

    if module in tasks:
        task = tasks[module]
        task["progress"] = min(task["target"], task["progress"] + max(0, correct_count))
        if task["progress"] >= task["target"] and not task["claimed"]:
            task["claimed"] = True
            reward += int(task["reward"])

    user.coins += reward
    user.progress = progress
    user.tasks = tasks
    return {"reward": reward, "progress": progress, "tasks": tasks}
