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
				   m.especie AS tipo_mascota,
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

		owned_pet_rows = await pool.fetch(
			"""
			SELECT especie AS tipo_mascota
			FROM mascota_desbloqueada
			WHERE usuario_id = $1
			ORDER BY especie
			""",
			row["usuario_id"],
		)
		inventory_rows = await pool.fetch(
			"""
			SELECT CASE LOWER(p.nombre)
					WHEN 'comida' THEN 'pollo'
					ELSE LOWER(p.nombre)
				END AS item_id,
				p.nombre, i.cantidad
			FROM inventario AS i
			JOIN producto AS p ON p.id = i.producto_id
			WHERE i.usuario_id = $1
			ORDER BY p.id
			""",
			row["usuario_id"],
		)

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
			pet_type=row["tipo_mascota"] or "pinguino",
			owned_pets=[pet_row["tipo_mascota"] for pet_row in owned_pet_rows],
			inventory=[
				{"item_id": inventory_row["item_id"], "name": inventory_row["nombre"], "quantity": inventory_row["cantidad"]}
				for inventory_row in inventory_rows
			],
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
						"INSERT INTO mascota (nombre, comida, sueno, felicidad, usuario_id, especie) VALUES ($1, $2, $3, $4, $5, 'pinguino')",
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
					await connection.execute(
						"INSERT INTO mascota_desbloqueada (usuario_id, especie) VALUES ($1, 'pinguino')",
						user_id,
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
		except RepositoryError:
			raise
		except asyncpg.PostgresError as exc:
			raise RepositoryError("No se pudo guardar el usuario.") from exc

	async def delete_user(self, username: str) -> bool:
		pool = await self._get_pool()
		try:
			async with pool.acquire() as connection:
				async with connection.transaction():
					deleted_id = await connection.fetchval(
						"DELETE FROM usuario WHERE LOWER(nombre) = LOWER($1) RETURNING id",
						username,
					)
			return deleted_id is not None
		except (asyncpg.PostgresError, OSError) as exc:
			logger.exception("No se pudo eliminar la cuenta del usuario %s", username)
			raise RepositoryError("No se pudo eliminar la cuenta.") from exc

	async def add_coins(self, username: str, amount: int) -> int:
		if amount < 0:
			raise ValueError("La recompensa no puede ser negativa.")
		pool = await self._get_pool()
		try:
			balance = await pool.fetchval(
				"""
				UPDATE monedero AS w
				SET saldo_plata = w.saldo_plata + $2,
					ultima_actualizacion = CURRENT_TIMESTAMP
				FROM usuario AS u
				WHERE w.usuario_id = u.id AND LOWER(u.nombre) = LOWER($1)
				RETURNING w.saldo_plata
				""",
				username,
				amount,
			)
			if balance is None:
				raise RepositoryError("No se encontró el monedero del usuario.")
			return int(balance)
		except RepositoryError:
			raise
		except asyncpg.PostgresError as exc:
			raise RepositoryError("No se pudo guardar la recompensa.") from exc

	async def get_products(self) -> list[dict[str, Any]]:
		pool = await self._get_pool()
		try:
			rows = await pool.fetch("SELECT nombre AS name, precio AS price FROM producto ORDER BY id")
			return [dict(row) for row in rows]
		except asyncpg.PostgresError as exc:
			raise RepositoryError("No se pudo cargar el catálogo de la tienda.") from exc

	async def _get_inventory(self, connection: asyncpg.Connection, user_id: int) -> list[dict[str, Any]]:
		rows = await connection.fetch(
			"""
			SELECT CASE LOWER(p.nombre)
					WHEN 'comida' THEN 'pollo'
					ELSE LOWER(p.nombre)
				END AS item_id,
				p.nombre, i.cantidad
			FROM inventario AS i
			JOIN producto AS p ON p.id = i.producto_id
			WHERE i.usuario_id = $1
			ORDER BY p.id
			""",
			user_id,
		)
		return [
			{"item_id": row["item_id"], "name": row["nombre"], "quantity": row["cantidad"]}
			for row in rows
		]

	async def purchase_item(self, username: str, product_name: str) -> dict[str, Any]:
		pool = await self._get_pool()
		try:
			async with pool.acquire() as connection:
				async with connection.transaction():
					row = await connection.fetchrow(
						"""
						SELECT u.id AS usuario_id, w.id_monedero
						FROM usuario AS u
						JOIN monedero AS w ON w.usuario_id = u.id
						WHERE LOWER(u.nombre) = LOWER($1)
						FOR UPDATE OF w
						""",
						username,
					)
					if row is None:
						raise RepositoryError("No se encontró el monedero del usuario.")

					product = await connection.fetchrow(
						"SELECT id, precio FROM producto WHERE LOWER(nombre) = LOWER($1)", product_name
					)
					if product is None:
						raise RepositoryError("El producto no está disponible en la tienda.")

					balance = await connection.fetchval(
						"""
						UPDATE monedero
						SET saldo_plata = saldo_plata - $1,
							ultima_actualizacion = CURRENT_TIMESTAMP
						WHERE id_monedero = $2 AND saldo_plata >= $1
						RETURNING saldo_plata
						""",
						product["precio"],
						row["id_monedero"],
					)
					if balance is None:
						raise ValueError("No tienes monedas suficientes.")

					await connection.execute(
						"INSERT INTO compra (monedero_id, producto_id) VALUES ($1, $2)",
						row["id_monedero"],
						product["id"],
					)
					await connection.execute(
						"""
						INSERT INTO inventario (usuario_id, producto_id, cantidad)
						VALUES ($1, $2, 1)
						ON CONFLICT (usuario_id, producto_id)
						DO UPDATE SET cantidad = inventario.cantidad + 1
						""",
						row["usuario_id"],
						product["id"],
					)
					inventory = await self._get_inventory(connection, row["usuario_id"])
				return {
					"coins": int(balance),
					"price": int(product["precio"]),
					"inventory": inventory,
				}
		except (RepositoryError, ValueError):
			raise
		except (asyncpg.PostgresError, OSError) as exc:
			raise RepositoryError("No se pudo completar la compra del producto.") from exc

	async def use_item(self, username: str, product_name: str, stat: str, effect: int) -> dict[str, Any]:
		pool = await self._get_pool()
		stat_columns = {"food": "comida", "sleep": "sueno", "happiness": "felicidad"}
		column = stat_columns.get(stat)
		if column is None or effect <= 0:
			raise ValueError("Efecto del producto no válido.")

		try:
			async with pool.acquire() as connection:
				async with connection.transaction():
					row = await connection.fetchrow(
						"""
						SELECT u.id AS usuario_id, m.id AS mascota_id
						FROM usuario AS u
						JOIN mascota AS m ON m.usuario_id = u.id
						WHERE LOWER(u.nombre) = LOWER($1)
						FOR UPDATE OF m
						""",
						username,
					)
					if row is None:
						raise RepositoryError("No se encontró la mascota del usuario.")

					product_id = await connection.fetchval(
						"SELECT id FROM producto WHERE LOWER(nombre) = LOWER($1)", product_name
					)
					if product_id is None:
						raise ValueError("Producto no válido.")

					inventory_row = await connection.fetchrow(
						"""
						SELECT cantidad FROM inventario
						WHERE usuario_id = $1 AND producto_id = $2
						FOR UPDATE
						""",
						row["usuario_id"],
						product_id,
					)
					if inventory_row is None or inventory_row["cantidad"] < 1:
						raise ValueError("No tienes ese objeto en el inventario.")

					if inventory_row["cantidad"] == 1:
						await connection.execute(
							"DELETE FROM inventario WHERE usuario_id = $1 AND producto_id = $2",
							row["usuario_id"],
							product_id,
						)
					else:
						await connection.execute(
							"UPDATE inventario SET cantidad = cantidad - 1 WHERE usuario_id = $1 AND producto_id = $2",
							row["usuario_id"],
							product_id,
						)

					pet = await connection.fetchrow(
						f"""
						UPDATE mascota
						SET {column} = LEAST(100, {column} + $1)
						WHERE id = $2
						RETURNING comida, sueno, felicidad
						""",
						effect,
						row["mascota_id"],
					)
					inventory = await self._get_inventory(connection, row["usuario_id"])
				return {
					"food": pet["comida"],
					"sleep": pet["sueno"],
					"happiness": pet["felicidad"],
					"inventory": inventory,
				}
		except (RepositoryError, ValueError):
			raise
		except (asyncpg.PostgresError, OSError) as exc:
			raise RepositoryError("No se pudo utilizar el producto.") from exc

	async def purchase_pet(self, username: str, pet_id: str, pet_name: str) -> bool:
		if pet_id not in {"pinguino", "oso", "zorro", "nutria"} or pet_name.casefold() != pet_id.casefold():
			raise ValueError("Mascota no válida.")
		pool = await self._get_pool()
		try:
			async with pool.acquire() as connection:
				async with connection.transaction():
					row = await connection.fetchrow(
						"""
						SELECT u.id AS usuario_id, w.id_monedero, m.id AS mascota_id
						FROM usuario AS u
						JOIN monedero AS w ON w.usuario_id = u.id
						JOIN mascota AS m ON m.usuario_id = u.id
						WHERE LOWER(u.nombre) = LOWER($1)
						FOR UPDATE OF w, m
						""",
						username,
					)
					if row is None:
						raise RepositoryError("No se encontró el monedero o la mascota del usuario.")

					product = await connection.fetchrow(
						"SELECT id, precio FROM producto WHERE LOWER(nombre) = LOWER($1)",
						pet_name,
					)
					if product is None:
						raise RepositoryError("Falta ejecutar la migración SQL de mascotas en Neon.")

					owned = await connection.fetchval(
						"""
						SELECT EXISTS (
							SELECT 1 FROM mascota_desbloqueada
							WHERE usuario_id = $1 AND especie = $2
						)
						""",
						row["usuario_id"],
						pet_id,
					)
					purchased = not owned
					if purchased:
						balance = await connection.fetchval(
							"""
							UPDATE monedero
							SET saldo_plata = saldo_plata - $1,
								ultima_actualizacion = CURRENT_TIMESTAMP
							WHERE id_monedero = $2 AND saldo_plata >= $1
							RETURNING saldo_plata
							""",
							product["precio"],
							row["id_monedero"],
						)
						if balance is None:
							raise ValueError("No tienes monedas suficientes.")
						await connection.execute(
							"INSERT INTO compra (monedero_id, producto_id) VALUES ($1, $2)",
							row["id_monedero"],
							product["id"],
						)
						await connection.execute(
							"""
							INSERT INTO mascota_desbloqueada (usuario_id, especie)
							VALUES ($1, $2)
							ON CONFLICT (usuario_id, especie) DO NOTHING
							""",
							row["usuario_id"],
							pet_id,
						)

					await connection.execute(
						"UPDATE mascota SET especie = $1 WHERE id = $2",
						pet_id,
						row["mascota_id"],
					)
			return purchased
		except (RepositoryError, ValueError):
			raise
		except (asyncpg.PostgresError, OSError) as exc:
			raise RepositoryError("No se pudo completar la compra de la mascota.") from exc

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
