-- Registra al usuario y devuelve su identificador para crear su mascota.
-- Tabla: usuario
INSERT INTO usuario (nombre)
VALUES (:nombre)
RETURNING id, nombre;

-- Guarda el usuario de login y su hash después de crear el registro principal.
-- Tabla: credenciales
INSERT INTO credenciales (usuario, contrasena, usuario_id)
VALUES (:usuario, :contrasena_hash, :usuario_id)
RETURNING id, usuario, usuario_id;

-- Crea la mascota inicial asociada al usuario recien registrado.
-- Tabla: mascota
INSERT INTO mascota (nombre, comida, sueno, felicidad, usuario_id)
VALUES (:nombre_mascota, 100, 100, 100, :usuario_id)
RETURNING id, nombre, comida, sueno, felicidad, usuario_id;

-- Busca el hash necesario para autenticar al usuario por su nombre de login.
-- Tabla: credenciales
SELECT c.usuario_id, c.usuario, c.contrasena
FROM credenciales AS c
WHERE c.usuario = :usuario;

-- Carga el perfil y el estado de la mascota para las pantallas autenticadas.
-- Tablas: usuario y mascota
SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    m.id AS mascota_id,
    m.nombre AS mascota,
    m.comida,
    m.sueno,
    m.felicidad
FROM usuario AS u
LEFT JOIN mascota AS m ON m.usuario_id = u.id
WHERE u.id = :usuario_id;

-- Guarda en una sola operacion el estado que el backend modifica:
-- nombre de mascota y sus tres estadisticas.
-- Tabla: mascota
UPDATE mascota
SET nombre = :nombre_mascota,
    comida = :comida,
    sueno = :sueno,
    felicidad = :felicidad
WHERE usuario_id = :usuario_id
RETURNING id, nombre, comida, sueno, felicidad, usuario_id;

-- Lista los productos disponibles para mostrar la tienda.
-- Tabla: producto
SELECT id, nombre, precio
FROM producto
ORDER BY id;

-- Lista las actividades disponibles.
-- Tabla: ejercicio
SELECT id, tipo, operacion
FROM ejercicio
ORDER BY id;

-- Crea el monedero del usuario al registrarlo.
-- Tabla: monedero
INSERT INTO monedero (usuario_id, saldo_plata)
VALUES (:usuario_id, 0)
RETURNING id_monedero, usuario_id, saldo_plata, ultima_actualizacion;

-- Consulta el saldo disponible del usuario.
-- Tabla: monedero
SELECT id_monedero, usuario_id, saldo_plata, ultima_actualizacion
FROM monedero
WHERE usuario_id = :usuario_id;

-- Actualiza el saldo después de una recompensa o una compra.
-- Tabla: monedero
UPDATE monedero
SET saldo_plata = :saldo_plata,
    ultima_actualizacion = CURRENT_TIMESTAMP
WHERE usuario_id = :usuario_id
RETURNING id_monedero, usuario_id, saldo_plata, ultima_actualizacion;

-- Registra un estado histórico de la mascota.
-- Tabla: progreso
INSERT INTO progreso (comida, sueno, felicidad, mascota_id)
VALUES (:comida, :sueno, :felicidad, :mascota_id)
RETURNING id, comida, sueno, felicidad, mascota_id;

-- Registra el resultado de una actividad.
-- Tablas: resultado, mascota y ejercicio
INSERT INTO resultado (puntaje, mascota_id, ejercicio_id)
VALUES (:puntaje, :mascota_id, :ejercicio_id)
RETURNING id, puntaje, mascota_id, ejercicio_id;

-- Consulta los resultados de una mascota con su actividad.
-- Tablas: resultado y ejercicio
SELECT r.id, r.puntaje, r.mascota_id, r.ejercicio_id,
       e.tipo, e.operacion
FROM resultado AS r
INNER JOIN ejercicio AS e ON e.id = r.ejercicio_id
WHERE r.mascota_id = :mascota_id
ORDER BY r.id DESC;

-- Registra la compra de un producto con el monedero del usuario.
-- Tablas: compra y producto
INSERT INTO compra (monedero_id, producto_id)
SELECT :monedero_id, p.id
FROM producto AS p
WHERE p.id = :producto_id
RETURNING id, monedero_id, producto_id;

-- Consulta el historial de compras de un usuario.
-- Tablas: compra, monedero y producto
SELECT c.id AS compra_id, c.monedero_id,
       p.id AS producto_id, p.nombre, p.precio
FROM compra AS c
INNER JOIN monedero AS m ON m.id_monedero = c.monedero_id
INNER JOIN producto AS p ON p.id = c.producto_id
WHERE m.usuario_id = :usuario_id
ORDER BY c.id DESC;
