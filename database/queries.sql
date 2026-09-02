-- Registra al usuario y devuelve su identificador para crear su mascota.
INSERT INTO usuario (nombre)
VALUES (:nombre)
RETURNING id, nombre;

-- Guarda el usuario de login y su hash después de crear el registro principal.
INSERT INTO credenciales (usuario, contrasena, usuario_id)
VALUES (:usuario, :contrasena_hash, :usuario_id)
RETURNING id, usuario, usuario_id;

-- Crea la mascota inicial asociada al usuario recien registrado.
INSERT INTO mascota (nombre, comida, sueno, felicidad, usuario_id)
VALUES (:nombre_mascota, 100, 100, 100, :usuario_id)
RETURNING id, nombre, comida, sueno, felicidad, usuario_id;

-- Busca el hash necesario para autenticar al usuario por su nombre de login.
SELECT c.usuario_id, c.usuario, c.contrasena
FROM credenciales AS c
WHERE c.usuario = :usuario;

-- Carga el perfil y el estado de la mascota para las pantallas autenticadas.
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
UPDATE mascota
SET nombre = :nombre_mascota,
    comida = :comida,
    sueno = :sueno,
    felicidad = :felicidad
WHERE usuario_id = :usuario_id
RETURNING id, nombre, comida, sueno, felicidad, usuario_id;

-- Lista los productos disponibles para mostrar la tienda.
SELECT id, nombre, precio
FROM producto
ORDER BY id;
