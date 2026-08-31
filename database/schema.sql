-- Edupets - esquema de base de datos
-- Motor recomendado: PostgreSQL
-- Archivo: schema.sql
--
-- Este archivo crea la estructura equivalente al modelo entidad-relación
-- de Edupets y contiene consultas CRUD y consultas de relación.
--
-- NOTA:
-- El repositorio actualmente utiliza Google Sheets como almacenamiento
-- provisional. Este esquema NO cambia automáticamente el backend de FastAPI;
-- para usar PostgreSQL habrá que sustituir/crear el servicio de persistencia.

BEGIN;

-- ============================================================
-- 1. LIMPIEZA OPCIONAL
-- ============================================================
-- Descomenta estas líneas únicamente si quieres reconstruir la BD
-- desde cero y borrar los datos existentes.
--
-- DROP TABLE IF EXISTS resultado CASCADE;
-- DROP TABLE IF EXISTS examen CASCADE;
-- DROP TABLE IF EXISTS compra CASCADE;
-- DROP TABLE IF EXISTS ejercicio CASCADE;
-- DROP TABLE IF EXISTS progreso CASCADE;
-- DROP TABLE IF EXISTS producto CASCADE;
-- DROP TABLE IF EXISTS mascota CASCADE;
-- DROP TABLE IF EXISTS credenciales CASCADE;
-- DROP TABLE IF EXISTS usuario CASCADE;


-- ============================================================
-- 2. USUARIO
-- ============================================================
CREATE TABLE IF NOT EXISTS usuario (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      VARCHAR(50) NOT NULL UNIQUE
);

-- ============================================================
-- 3. CREDENCIALES
-- ============================================================
-- Relación: USUARIO 1 --- 1 CREDENCIALES
CREATE TABLE IF NOT EXISTS credenciales (
    id              INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario         VARCHAR(50) NOT NULL,
    contrasena      VARCHAR(255) NOT NULL,
    usuario_id      INTEGER NOT NULL UNIQUE,

    CONSTRAINT fk_credenciales_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_credenciales_usuario_id
    ON credenciales(usuario_id);


-- ============================================================
-- 4. MASCOTA
-- ============================================================
-- Relación: USUARIO 1 --- 1 MASCOTA
CREATE TABLE IF NOT EXISTS mascota (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      VARCHAR(30) NOT NULL DEFAULT 'Mi Mascota',
    comida      INTEGER NOT NULL DEFAULT 100,
    sueno       INTEGER NOT NULL DEFAULT 100,
    felicidad   INTEGER NOT NULL DEFAULT 100,
    usuario_id  INTEGER NOT NULL UNIQUE,

    CONSTRAINT fk_mascota_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_mascota_comida
        CHECK (comida BETWEEN 0 AND 100),

    CONSTRAINT chk_mascota_sueno
        CHECK (sueno BETWEEN 0 AND 100),

    CONSTRAINT chk_mascota_felicidad
        CHECK (felicidad BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_mascota_usuario_id
    ON mascota(usuario_id);


-- ============================================================
-- 5. PRODUCTO
-- ============================================================
CREATE TABLE IF NOT EXISTS producto (
    id       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre   VARCHAR(100) NOT NULL UNIQUE,
    precio   NUMERIC(10,2) NOT NULL,

    CONSTRAINT chk_producto_precio
        CHECK (precio >= 0)
);


-- ============================================================
-- 6. PROGRESO
-- ============================================================
-- Relación: MASCOTA 1 --- N PROGRESO
CREATE TABLE IF NOT EXISTS progreso (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    comida      INTEGER NOT NULL DEFAULT 100,
    sueno       INTEGER NOT NULL DEFAULT 100,
    felicidad   INTEGER NOT NULL DEFAULT 100,
    mascota_id  INTEGER NOT NULL,

    CONSTRAINT fk_progreso_mascota
        FOREIGN KEY (mascota_id)
        REFERENCES mascota(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_progreso_comida
        CHECK (comida BETWEEN 0 AND 100),

    CONSTRAINT chk_progreso_sueno
        CHECK (sueno BETWEEN 0 AND 100),

    CONSTRAINT chk_progreso_felicidad
        CHECK (felicidad BETWEEN 0 AND 100)
);

CREATE INDEX IF NOT EXISTS idx_progreso_mascota_id
    ON progreso(mascota_id);


-- ============================================================
-- 7. EJERCICIO
-- ============================================================
-- Relación: MASCOTA 1 --- N EJERCICIO
CREATE TABLE IF NOT EXISTS ejercicio (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo        VARCHAR(30) NOT NULL,
    operacion   VARCHAR(20) NOT NULL,
    mascota_id  INTEGER NOT NULL,

    CONSTRAINT fk_ejercicio_mascota
        FOREIGN KEY (mascota_id)
        REFERENCES mascota(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ejercicio_mascota_id
    ON ejercicio(mascota_id);


-- ============================================================
-- 8. EXAMEN
-- ============================================================
-- Relación: MASCOTA 1 --- N EXAMEN
CREATE TABLE IF NOT EXISTS examen (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      VARCHAR(100) NOT NULL,
    puntaje     INTEGER NOT NULL DEFAULT 0,
    mascota_id  INTEGER NOT NULL,

    CONSTRAINT fk_examen_mascota
        FOREIGN KEY (mascota_id)
        REFERENCES mascota(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_examen_puntaje
        CHECK (puntaje >= 0)
);

CREATE INDEX IF NOT EXISTS idx_examen_mascota_id
    ON examen(mascota_id);


-- ============================================================
-- 9. COMPRA
-- ============================================================
-- Tabla intermedia:
-- MASCOTA N --- N PRODUCTO
CREATE TABLE IF NOT EXISTS compra (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    mascota_id  INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,

    CONSTRAINT fk_compra_mascota
        FOREIGN KEY (mascota_id)
        REFERENCES mascota(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_compra_producto
        FOREIGN KEY (producto_id)
        REFERENCES producto(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_compra_mascota_id
    ON compra(mascota_id);

CREATE INDEX IF NOT EXISTS idx_compra_producto_id
    ON compra(producto_id);


-- ============================================================
-- 10. RESULTADO
-- ============================================================
-- Un resultado pertenece a una mascota y a un ejercicio.
CREATE TABLE IF NOT EXISTS resultado (
    id           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    puntaje      INTEGER NOT NULL DEFAULT 0,
    mascota_id   INTEGER NOT NULL,
    ejercicio_id INTEGER NOT NULL,

    CONSTRAINT fk_resultado_mascota
        FOREIGN KEY (mascota_id)
        REFERENCES mascota(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_resultado_ejercicio
        FOREIGN KEY (ejercicio_id)
        REFERENCES ejercicio(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_resultado_puntaje
        CHECK (puntaje >= 0)
);

CREATE INDEX IF NOT EXISTS idx_resultado_mascota_id
    ON resultado(mascota_id);

CREATE INDEX IF NOT EXISTS idx_resultado_ejercicio_id
    ON resultado(ejercicio_id);


-- ============================================================
-- 11. PRODUCTOS INICIALES DE EDU-PETS
-- ============================================================
INSERT INTO producto (nombre, precio)
VALUES
    ('Comida', 20),
    ('Juguete', 30),
    ('Vive 100', 25)
ON CONFLICT (nombre) DO NOTHING;


-- ============================================================
-- 12. EJERCICIOS BASE
-- ============================================================
-- Los ejercicios de la aplicación actual son:
-- sumas, restas, multiplicación y división.
--
-- No se insertan aquí porque pertenecen a una mascota concreta.
-- Se crean después de registrar al usuario y su mascota.


-- ============================================================
-- 13. QUERIES DE USUARIO
-- ============================================================

-- Crear usuario
-- INSERT INTO usuario (nombre)
-- VALUES ('Samuel')
-- RETURNING *;

-- Consultar usuario por nombre
-- SELECT *
-- FROM usuario
-- WHERE nombre = 'Samuel';

-- Actualizar nombre de usuario
-- UPDATE usuario
-- SET nombre = 'NuevoNombre'
-- WHERE id = 1;

-- Eliminar usuario
-- La eliminación en cascada elimina credenciales y mascota.
-- DELETE FROM usuario WHERE id = 1;


-- ============================================================
-- 14. QUERIES DE CREDENCIALES
-- ============================================================

-- Crear credenciales
-- INSERT INTO credenciales (usuario, contrasena, usuario_id)
-- VALUES ('Samuel', 'HASH_DE_LA_CONTRASENA', 1)
-- RETURNING *;

-- Buscar credenciales para iniciar sesión
-- SELECT c.id, c.usuario, c.contrasena, c.usuario_id
-- FROM credenciales c
-- WHERE c.usuario = 'Samuel';

-- Actualizar contraseña
-- UPDATE credenciales
-- SET contrasena = 'NUEVO_HASH'
-- WHERE usuario_id = 1;


-- ============================================================
-- 15. QUERIES DE MASCOTA
-- ============================================================

-- Crear mascota para un usuario
-- INSERT INTO mascota (nombre, comida, sueno, felicidad, usuario_id)
-- VALUES ('Mi Mascota', 100, 100, 100, 1)
-- RETURNING *;

-- Consultar mascota de un usuario
-- SELECT m.*
-- FROM mascota m
-- WHERE m.usuario_id = 1;

-- Actualizar estadísticas
-- UPDATE mascota
-- SET comida = 80,
--     sueno = 70,
--     felicidad = 90
-- WHERE id = 1;

-- Actualizar nombre de mascota
-- UPDATE mascota
-- SET nombre = 'Pelusa'
-- WHERE id = 1;


-- ============================================================
-- 16. QUERY COMPLETA DE USUARIO + MASCOTA
-- ============================================================
SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    m.id AS mascota_id,
    m.nombre AS mascota,
    m.comida,
    m.sueno,
    m.felicidad
FROM usuario u
LEFT JOIN mascota m
    ON m.usuario_id = u.id;


-- ============================================================
-- 17. QUERIES DE PROGRESO
-- ============================================================

-- Registrar un estado de progreso
-- INSERT INTO progreso (comida, sueno, felicidad, mascota_id)
-- VALUES (100, 100, 100, 1);

-- Obtener historial de progreso
-- SELECT *
-- FROM progreso
-- WHERE mascota_id = 1
-- ORDER BY id DESC;

-- Obtener el último progreso de una mascota
-- SELECT *
-- FROM progreso
-- WHERE mascota_id = 1
-- ORDER BY id DESC
-- LIMIT 1;


-- ============================================================
-- 18. QUERIES DE PRODUCTOS
-- ============================================================

-- Listar productos
-- SELECT *
-- FROM producto
-- ORDER BY id;

-- Buscar producto
-- SELECT *
-- FROM producto
-- WHERE id = 1;

-- Crear producto
-- INSERT INTO producto (nombre, precio)
-- VALUES ('Nuevo producto', 50)
-- RETURNING *;

-- Actualizar precio
-- UPDATE producto
-- SET precio = 35
-- WHERE id = 1;

-- Eliminar producto
-- DELETE FROM producto
-- WHERE id = 1;


-- ============================================================
-- 19. QUERIES DE COMPRA
-- ============================================================

-- Registrar compra
-- INSERT INTO compra (mascota_id, producto_id)
-- VALUES (1, 1)
-- RETURNING *;

-- Historial de compras de una mascota
-- SELECT
--     c.id AS compra_id,
--     p.id AS producto_id,
--     p.nombre,
--     p.precio
-- FROM compra c
-- INNER JOIN producto p
--     ON p.id = c.producto_id
-- WHERE c.mascota_id = 1
-- ORDER BY c.id DESC;

-- Productos comprados por todas las mascotas
-- SELECT
--     m.nombre AS mascota,
--     p.nombre AS producto,
--     p.precio
-- FROM compra c
-- INNER JOIN mascota m
--     ON m.id = c.mascota_id
-- INNER JOIN producto p
--     ON p.id = c.producto_id
-- ORDER BY c.id DESC;


-- ============================================================
-- 20. QUERIES DE EJERCICIOS
-- ============================================================

-- Crear ejercicio
-- INSERT INTO ejercicio (tipo, operacion, mascota_id)
-- VALUES ('sumas', '+', 1)
-- RETURNING *;

-- Listar ejercicios de una mascota
-- SELECT *
-- FROM ejercicio
-- WHERE mascota_id = 1
-- ORDER BY id;

-- Buscar ejercicios por tipo
-- SELECT *
-- FROM ejercicio
-- WHERE mascota_id = 1
--   AND tipo = 'multiplicacion';


-- ============================================================
-- 21. QUERIES DE RESULTADOS
-- ============================================================

-- Registrar resultado
-- INSERT INTO resultado (puntaje, mascota_id, ejercicio_id)
-- VALUES (5, 1, 1)
-- RETURNING *;

-- Resultados de una mascota
-- SELECT
--     r.id,
--     r.puntaje,
--     e.tipo,
--     e.operacion
-- FROM resultado r
-- INNER JOIN ejercicio e
--     ON e.id = r.ejercicio_id
-- WHERE r.mascota_id = 1
-- ORDER BY r.id DESC;

-- Promedio de resultados de una mascota
-- SELECT
--     mascota_id,
--     ROUND(AVG(puntaje), 2) AS promedio
-- FROM resultado
-- WHERE mascota_id = 1
-- GROUP BY mascota_id;


-- ============================================================
-- 22. QUERIES DE EXÁMENES
-- ============================================================

-- Crear examen
-- INSERT INTO examen (nombre, puntaje, mascota_id)
-- VALUES ('Examen de matemáticas', 90, 1)
-- RETURNING *;

-- Consultar exámenes de una mascota
-- SELECT *
-- FROM examen
-- WHERE mascota_id = 1
-- ORDER BY id DESC;


-- ============================================================
-- 23. CONSULTA GENERAL DEL PERFIL
-- ============================================================
-- Devuelve usuario, credenciales, mascota y estadísticas.
-- No devuelve la contraseña en aplicaciones públicas.
SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    m.id AS mascota_id,
    m.nombre AS mascota,
    m.comida,
    m.sueno,
    m.felicidad
FROM usuario u
LEFT JOIN mascota m
    ON m.usuario_id = u.id
WHERE u.id = 1;


-- ============================================================
-- 24. RESUMEN ACADÉMICO DE UNA MASCOTA
-- ============================================================
SELECT
    m.id AS mascota_id,
    m.nombre AS mascota,
    COUNT(DISTINCT e.id) AS ejercicios_realizados,
    COUNT(DISTINCT r.id) AS resultados_registrados,
    COALESCE(ROUND(AVG(r.puntaje), 2), 0) AS promedio,
    COUNT(DISTINCT ex.id) AS examenes_realizados
FROM mascota m
LEFT JOIN ejercicio e
    ON e.mascota_id = m.id
LEFT JOIN resultado r
    ON r.ejercicio_id = e.id
    AND r.mascota_id = m.id
LEFT JOIN examen ex
    ON ex.mascota_id = m.id
WHERE m.id = 1
GROUP BY m.id, m.nombre;


-- ============================================================
-- 25. DIAGRAMA LÓGICO DE RELACIONES
-- ============================================================
-- USUARIO
--   ├── 1:1 CREDENCIALES
--   └── 1:1 MASCOTA
--               ├── 1:N PROGRESO
--               ├── 1:N EJERCICIO
--               │       └── 1:N RESULTADO
--               ├── 1:N EXAMEN
--               └── N:M PRODUCTO
--                       └── COMPRA
--
-- La tabla COMPRA resuelve la relación muchos-a-muchos entre
-- MASCOTA y PRODUCTO.


-- ============================================================
-- 26. VISTA ÚTIL PARA EL BACKEND
-- ============================================================
CREATE OR REPLACE VIEW vista_perfil_edupets AS
SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    m.id AS mascota_id,
    m.nombre AS mascota,
    m.comida,
    m.sueno,
    m.felicidad
FROM usuario u
LEFT JOIN mascota m
    ON m.usuario_id = u.id;

COMMIT;
