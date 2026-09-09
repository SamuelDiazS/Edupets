#!/usr/bin/env python
"""Verifica la configuración de conexión de Edupets con Neon."""

import asyncio
import sys
from pathlib import Path

import asyncpg


def load_environment() -> dict[str, str]:
    env_file = Path(".env")
    if not env_file.exists():
        raise RuntimeError("No se encontró archivo .env. Crea uno basado en .env.example.")

    values: dict[str, str] = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
    return values


async def check_database(database_url: str) -> None:
    connection = await asyncpg.connect(database_url)
    try:
        await connection.fetchval("SELECT 1")
    finally:
        await connection.close()


def check_environment() -> bool:
    try:
        env_vars = load_environment()
        database_url = env_vars.get("DATABASE_URL", "").strip()
        if not database_url:
            print("DATABASE_URL no está configurado en .env")
            return False

        asyncio.run(check_database(database_url))
    except (OSError, RuntimeError, asyncpg.PostgresError, ValueError) as exc:
        print(f"No se pudo conectar con Neon: {exc}")
        return False

    print("Configuración de Neon verificada correctamente.")
    return True


if __name__ == "__main__":
    sys.exit(0 if check_environment() else 1)
