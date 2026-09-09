from __future__ import annotations

from collections import defaultdict
from typing import Any

import asyncpg
from loguru import logger

from app.config import Settings
from app.models.user import UserRecord


class RepositoryError(RuntimeError):
	"""Error de acceso a la base de datos."""


class DatabaseRepository:
	def __init__(self, settings: Settings):
		self.settings = settings
		self._pool: asyncpg.Pool | None = None

	async def connect(self) -> None:
		if self._pool is not None:
			return
		if not self.settings.DATABASE_URL:
			raise RepositoryError("DATABASE_URL es obligatorio para conectar con Neon.")
		try:
			self._pool = await asyncpg.create_pool(self.settings.DATABASE_URL, min_size=1, max_size=5)
			await self._pool.fetchval("SELECT 1")
			logger.info("Conexión con Neon establecida")
		except (asyncpg.PostgresError, OSError, ValueError) as exc:
			self._pool = None
			logger.exception("No se pudo conectar con Neon")
			raise RepositoryError("No se pudo conectar con la base de datos.") from exc

	async def close(self) -> None:
		if self._pool is not None:
			await self._pool.close()
			self._pool = None

	async def _get_pool(self) -> asyncpg.Pool:
		await self.connect()
		if self._pool is None:
			raise RepositoryError("El pool de base de datos no está disponible.")
		return self._pool

	async def check_connection(self) -> None:
		pool = await self._get_pool()
		try:
			await pool.fetchval("SELECT 1")
		except asyncpg.PostgresError as exc:
			raise RepositoryError("La base de datos no está disponible.") from exc

	@staticmethod
	def _module_key(value: str) -> str:
		return value.strip().lower().replace("multiplicación", "multiplicacion")

	async def get_user(self, username: str) -> tuple[int, UserRecord] | None:
		pool = await self._get_pool()
		row = await pool.fetchrow(
			"""
			SELECT u.id AS usuario_id, u.nombre, c.contrasena,
				   m.id AS mascota_id, m.nombre AS mascota,
				   m.comida, m.sueno, m.felicidad,
				   COALESCE(w.saldo_plata, 0) AS monedas
			FROM usuario AS u
			JOIN credenciales AS c ON c.usuario_id = u.id
			LEFT JOIN mascota AS m ON m.usuario_id = u.id
			LEFT JOIN monedero AS w ON w.usuario_id = u.id
			WHERE LOWER(c.usuario) = LOWER($1)
			""",
			username.strip(),
		)
		if row is None:
			return None

		progress_rows = await pool.fetch(
			"""
			SELECT e.tipo, e.operacion
			FROM resultado AS r
			JOIN ejercicio AS e ON e.id = r.ejercicio_id
			WHERE r.mascota_id = $1
			""",
			row["mascota_id"],
		) if row["mascota_id"] else []
		completed: dict[str, set[int]] = defaultdict(set)
		counts: dict[str, int] = defaultdict(int)
		for progress_row in progress_rows:
			module = self._module_key(progress_row["tipo"])
			try:
				level = int(progress_row["operacion"])
			except (TypeError, ValueError):
				continue
			completed[module].add(level)
			counts[module] += 1

		modules = ("sumas", "restas", "multiplicacion", "division")
		progress = {"completed": {module: sorted(completed[module]) for module in modules}}
		tasks = {
			module: {
				"label": f"Completa 5 {module}",
				"target": 5,
				"progress": min(counts[module], 5),
				"reward": 20 if module in {"multiplicacion", "division"} else 15,
				"claimed": counts[module] >= 5,
			}
			for module in modules
		}
		user = UserRecord(
			username=row["nombre"],
			password_hash=row["contrasena"],
			coins=int(row["monedas"]),
			happiness=int(row["felicidad"] if row["felicidad"] is not None else 100),
			food=int(row["comida"] if row["comida"] is not None else 100),
			sleep=int(row["sueno"] if row["sueno"] is not None else 100),
			pet_name=row["mascota"] or "Mi Mascota",
			progress=progress,
			tasks=tasks,
		)
		return int(row["usuario_id"]), user

	async def append_user(self, user: UserRecord) -> None:
		pool = await self._get_pool()
		try:
			async with pool.acquire() as connection:
				async with connection.transaction():
					user_row = await connection.fetchrow(
						"INSERT INTO usuario (nombre) VALUES ($1) RETURNING id",
						user.username,
					)
					user_id = user_row["id"]
					await connection.execute(
						"INSERT INTO credenciales (usuario, contrasena, usuario_id) VALUES ($1, $2, $3)",
						user.username,
						user.password_hash,
						user_id,
					)
					await connection.execute(
						"INSERT INTO mascota (nombre, comida, sueno, felicidad, usuario_id) VALUES ($1, $2, $3, $4, $5)",
						user.pet_name,
						user.food,
						user.sleep,
						user.happiness,
						user_id,
					)
					await connection.execute(
						"INSERT INTO monedero (usuario_id, saldo_plata) VALUES ($1, $2)",
						user_id,
						user.coins,
					)
		except asyncpg.UniqueViolationError as exc:
			raise RepositoryError("Ese usuario ya existe.") from exc
		except asyncpg.PostgresError as exc:
			raise RepositoryError("No se pudo registrar el usuario.") from exc

	async def update_user(self, user: UserRecord) -> None:
		pool = await self._get_pool()
		try:
			async with pool.acquire() as connection:
				async with connection.transaction():
					row = await connection.fetchrow(
						"SELECT id FROM usuario WHERE LOWER(nombre) = LOWER($1)", user.username
					)
					if row is None:
						raise RepositoryError(f"No se encontró el usuario {user.username}.")
					await connection.execute(
						"""
						UPDATE mascota
						SET nombre = $1, comida = $2, sueno = $3, felicidad = $4
						WHERE usuario_id = $5
						""",
						user.pet_name,
						user.food,
						user.sleep,
						user.happiness,
						row["id"],
					)
					await connection.execute(
						"""
						INSERT INTO monedero (usuario_id, saldo_plata) VALUES ($1, $2)
						ON CONFLICT (usuario_id) DO UPDATE SET saldo_plata = EXCLUDED.saldo_plata,
							ultima_actualizacion = CURRENT_TIMESTAMP
						""",
						row["id"],
						user.coins,
					)
		except RepositoryError:
			raise
		except asyncpg.PostgresError as exc:
			raise RepositoryError("No se pudo guardar el usuario.") from exc

	async def record_activity(self, username: str, module: str, level: int, correct_count: int) -> None:
		pool = await self._get_pool()
		row = await pool.fetchrow(
			"SELECT u.id AS usuario_id, m.id AS mascota_id FROM usuario u JOIN mascota m ON m.usuario_id = u.id WHERE LOWER(u.nombre) = LOWER($1)",
			username,
		)
		if row is None:
			raise RepositoryError("No se encontró la mascota del usuario.")
		try:
			async with pool.acquire() as connection:
				async with connection.transaction():
					exercise = await connection.fetchrow(
						"SELECT id FROM ejercicio WHERE tipo = $1 AND operacion = $2 LIMIT 1",
						module,
						str(level),
					)
					if exercise is None:
						exercise = await connection.fetchrow(
							"INSERT INTO ejercicio (tipo, operacion) VALUES ($1, $2) RETURNING id",
							module,
							str(level),
						)
					await connection.execute(
						"INSERT INTO resultado (puntaje, mascota_id, ejercicio_id) VALUES ($1, $2, $3)",
						max(0, correct_count),
						row["mascota_id"],
						exercise["id"],
					)
		except asyncpg.PostgresError as exc:
			raise RepositoryError("No se pudo guardar el resultado de la actividad.") from exc
