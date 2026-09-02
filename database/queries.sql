-- ============================================================
-- EDUPETS - QUERIES.SQL
-- ============================================================
-- Consultas y operaciones de la base de datos.
-- Compatible con el esquema definido en database/schema.sql
-- Motor: PostgreSQL
--
-- IMPORTANTE:
-- 1. Los valores como :usuario_id son parámetros de ejemplo.
--    En PostgreSQL puro puedes reemplazarlos por valores concretos
--    o usar parámetros desde FastAPI/psycopg.
-- 2. Las contraseñas deben almacenarse como HASH, nunca como texto
--    plano.
-- 3. Este archivo contiene QUERIES; la creación de tablas está
--    en schema.sql.
-- ============================================================


-- ============================================================
-- 1. USUARIOS
-- ============================================================

-- 1.1 Registrar un usuario
INSERT INTO usuario (nombre)
VALUES (:nombre)
RETURNING id, nombre;


-- 1.2 Obtener un usuario por ID
SELECT id, nombre
FROM usuario
WHERE id = :usuario_id;


-- 1.3 Obtener un usuario por nombre
SELECT id, nombre
FROM usuario
WHERE nombre = :nombre;


-- 1.4 Comprobar si un nombre de usuario ya existe
SELECT EXISTS (
    SELECT 1
    FROM usuario
    WHERE nombre = :nombre
) AS existe;


-- 1.5 Actualizar nombre de usuario
UPDATE usuario
SET nombre = :nuevo_nombre
WHERE id = :usuario_id
RETURNING id, nombre;


-- 1.6 Eliminar usuario
-- Las relaciones configuradas con ON DELETE CASCADE eliminarán
-- sus credenciales, mascota y datos dependientes.
DELETE FROM usuario
WHERE id = :usuario_id;


-- 1.7 Listar todos los usuarios
SELECT id, nombre
FROM usuario
ORDER BY id;


-- ============================================================
-- 2. CREDENCIALES / AUTENTICACIÓN
-- ============================================================

-- 2.1 Registrar credenciales
-- :contrasena_hash debe contener el hash generado por el backend.
INSERT INTO credenciales (usuario, contrasena, usuario_id)
VALUES (:usuario, :contrasena_hash, :usuario_id)
RETURNING id, usuario, usuario_id;


-- 2.2 Obtener credenciales para iniciar sesión
SELECT
    c.id,
    c.usuario,
    c.contrasena,
    c.usuario_id
FROM credenciales c
WHERE c.usuario = :usuario;


-- 2.3 Obtener credenciales mediante usuario_id
SELECT
    id,
    usuario,
    contrasena,
    usuario_id
FROM credenciales
WHERE usuario_id = :usuario_id;


-- 2.4 Comprobar si existen credenciales para un usuario
SELECT EXISTS (
    SELECT 1
    FROM credenciales
    WHERE usuario_id = :usuario_id
) AS existe;


-- 2.5 Actualizar contraseña
UPDATE credenciales
SET contrasena = :contrasena_hash
WHERE usuario_id = :usuario_id
RETURNING id, usuario, usuario_id;


-- 2.6 Actualizar nombre utilizado para iniciar sesión
UPDATE credenciales
SET usuario = :nuevo_usuario
WHERE usuario_id = :usuario_id
RETURNING id, usuario, usuario_id;


-- ============================================================
-- 3. REGISTRO COMPLETO DE USUARIO
-- ============================================================

-- 3.1 Crear usuario y mascota en una transacción
-- Ejecutar dentro de BEGIN ... COMMIT desde el backend.
INSERT INTO usuario (nombre)
VALUES (:nombre)
RETURNING id;


-- Después de obtener el ID:
INSERT INTO mascota (
    nombre,
    comida,
    sueno,
    felicidad,
    usuario_id
)
VALUES (
    :nombre_mascota,
    100,
    100,
    100,
    :usuario_id
)
RETURNING id;


-- 3.2 Obtener perfil completo sin contraseña
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
WHERE u.id = :usuario_id;


-- ============================================================
-- 4. MASCOTAS
-- ============================================================

-- 4.1 Crear mascota
INSERT INTO mascota (
    nombre,
    comida,
    sueno,
    felicidad,
    usuario_id
)
VALUES (
    :nombre,
    :comida,
    :sueno,
    :felicidad,
    :usuario_id
)
RETURNING *;


-- 4.2 Obtener mascota de un usuario
SELECT
    id,
    nombre,
    comida,
    sueno,
    felicidad,
    usuario_id
FROM mascota
WHERE usuario_id = :usuario_id;


-- 4.3 Obtener mascota por ID
SELECT *
FROM mascota
WHERE id = :mascota_id;


-- 4.4 Actualizar estadísticas de la mascota
UPDATE mascota
SET
    comida = :comida,
    sueno = :sueno,
    felicidad = :felicidad
WHERE id = :mascota_id
RETURNING *;


-- 4.5 Aumentar comida
UPDATE mascota
SET comida = LEAST(100, comida + :cantidad)
WHERE id = :mascota_id
RETURNING comida;


-- 4.6 Disminuir comida
UPDATE mascota
SET comida = GREATEST(0, comida - :cantidad)
WHERE id = :mascota_id
RETURNING comida;


-- 4.7 Aumentar sueño
UPDATE mascota
SET sueno = LEAST(100, sueno + :cantidad)
WHERE id = :mascota_id
RETURNING sueno;


-- 4.8 Disminuir sueño
UPDATE mascota
SET sueno = GREATEST(0, sueno - :cantidad)
WHERE id = :mascota_id
RETURNING sueno;


-- 4.9 Aumentar felicidad
UPDATE mascota
SET felicidad = LEAST(100, felicidad + :cantidad)
WHERE id = :mascota_id
RETURNING felicidad;


-- 4.10 Disminuir felicidad
UPDATE mascota
SET felicidad = GREATEST(0, felicidad - :cantidad)
WHERE id = :mascota_id
RETURNING felicidad;


-- 4.11 Cambiar nombre de mascota
UPDATE mascota
SET nombre = :nuevo_nombre
WHERE id = :mascota_id
RETURNING id, nombre;


-- 4.12 Reiniciar estadísticas
UPDATE mascota
SET
    comida = 100,
    sueno = 100,
    felicidad = 100
WHERE id = :mascota_id
RETURNING *;


-- ============================================================
-- 5. PROGRESO
-- ============================================================

-- 5.1 Guardar una captura del estado de la mascota
INSERT INTO progreso (
    comida,
    sueno,
    felicidad,
    mascota_id
)
SELECT
    comida,
    sueno,
    felicidad,
    id
FROM mascota
WHERE id = :mascota_id
RETURNING *;


-- 5.2 Registrar un progreso con valores específicos
INSERT INTO progreso (
    comida,
    sueno,
    felicidad,
    mascota_id
)
VALUES (
    :comida,
    :sueno,
    :felicidad,
    :mascota_id
)
RETURNING *;


-- 5.3 Obtener todo el historial
SELECT
    id,
    comida,
    sueno,
    felicidad,
    mascota_id
FROM progreso
WHERE mascota_id = :mascota_id
ORDER BY id DESC;


-- 5.4 Obtener el último progreso
SELECT
    id,
    comida,
    sueno,
    felicidad,
    mascota_id
FROM progreso
WHERE mascota_id = :mascota_id
ORDER BY id DESC
LIMIT 1;


-- 5.5 Obtener el progreso promedio
SELECT
    mascota_id,
    ROUND(AVG(comida), 2) AS comida_promedio,
    ROUND(AVG(sueno), 2) AS sueno_promedio,
    ROUND(AVG(felicidad), 2) AS felicidad_promedio
FROM progreso
WHERE mascota_id = :mascota_id
GROUP BY mascota_id;


-- ============================================================
-- 6. PRODUCTOS
-- ============================================================

-- 6.1 Crear producto
INSERT INTO producto (nombre, precio)
VALUES (:nombre, :precio)
RETURNING *;


-- 6.2 Listar productos
SELECT
    id,
    nombre,
    precio
FROM producto
ORDER BY id;


-- 6.3 Obtener producto por ID
SELECT *
FROM producto
WHERE id = :producto_id;


-- 6.4 Buscar producto por nombre
SELECT *
FROM producto
WHERE nombre = :nombre;


-- 6.5 Buscar productos por coincidencia de nombre
SELECT *
FROM producto
WHERE nombre ILIKE '%' || :busqueda || '%'
ORDER BY nombre;


-- 6.6 Actualizar producto
UPDATE producto
SET
    nombre = :nombre,
    precio = :precio
WHERE id = :producto_id
RETURNING *;


-- 6.7 Actualizar solamente el precio
UPDATE producto
SET precio = :precio
WHERE id = :producto_id
RETURNING *;


-- 6.8 Eliminar producto
-- Fallará si existen compras asociadas porque la FK usa RESTRICT.
DELETE FROM producto
WHERE id = :producto_id;


-- ============================================================
-- 7. COMPRAS
-- ============================================================

-- 7.1 Registrar una compra
INSERT INTO compra (
    mascota_id,
    producto_id
)
VALUES (
    :mascota_id,
    :producto_id
)
RETURNING *;


-- 7.2 Obtener compras de una mascota
SELECT
    c.id AS compra_id,
    p.id AS producto_id,
    p.nombre AS producto,
    p.precio
FROM compra c
INNER JOIN producto p
    ON p.id = c.producto_id
WHERE c.mascota_id = :mascota_id
ORDER BY c.id DESC;


-- 7.3 Obtener una compra
SELECT
    c.id AS compra_id,
    c.mascota_id,
    c.producto_id,
    p.nombre AS producto,
    p.precio
FROM compra c
INNER JOIN producto p
    ON p.id = c.producto_id
WHERE c.id = :compra_id;


-- 7.4 Contar compras de una mascota
SELECT COUNT(*) AS total_compras
FROM compra
WHERE mascota_id = :mascota_id;


-- 7.5 Calcular cuánto ha gastado una mascota
SELECT
    COALESCE(SUM(p.precio), 0) AS total_gastado
FROM compra c
INNER JOIN producto p
    ON p.id = c.producto_id
WHERE c.mascota_id = :mascota_id;


-- 7.6 Productos más comprados
SELECT
    p.id,
    p.nombre,
    p.precio,
    COUNT(c.id) AS cantidad_compras
FROM producto p
LEFT JOIN compra c
    ON c.producto_id = p.id
GROUP BY p.id, p.nombre, p.precio
ORDER BY cantidad_compras DESC, p.nombre;


-- 7.7 Historial general de compras
SELECT
    c.id AS compra_id,
    m.nombre AS mascota,
    p.nombre AS producto,
    p.precio
FROM compra c
INNER JOIN mascota m
    ON m.id = c.mascota_id
INNER JOIN producto p
    ON p.id = c.producto_id
ORDER BY c.id DESC;


-- ============================================================
-- 8. EJERCICIOS
-- ============================================================

-- 8.1 Crear ejercicio
INSERT INTO ejercicio (
    tipo,
    operacion,
    mascota_id
)
VALUES (
    :tipo,
    :operacion,
    :mascota_id
)
RETURNING *;


-- 8.2 Obtener ejercicio por ID
SELECT *
FROM ejercicio
WHERE id = :ejercicio_id;


-- 8.3 Listar ejercicios de una mascota
SELECT
    id,
    tipo,
    operacion,
    mascota_id
FROM ejercicio
WHERE mascota_id = :mascota_id
ORDER BY id;


-- 8.4 Filtrar ejercicios por tipo
SELECT *
FROM ejercicio
WHERE mascota_id = :mascota_id
  AND tipo = :tipo
ORDER BY id;


-- 8.5 Obtener ejercicios y sus resultados
SELECT
    e.id AS ejercicio_id,
    e.tipo,
    e.operacion,
    r.id AS resultado_id,
    r.puntaje
FROM ejercicio e
LEFT JOIN resultado r
    ON r.ejercicio_id = e.id
   AND r.mascota_id = e.mascota_id
WHERE e.mascota_id = :mascota_id
ORDER BY e.id DESC;


-- ============================================================
-- 9. RESULTADOS
-- ============================================================

-- 9.1 Registrar resultado
INSERT INTO resultado (
    puntaje,
    mascota_id,
    ejercicio_id
)
VALUES (
    :puntaje,
    :mascota_id,
    :ejercicio_id
)
RETURNING *;


-- 9.2 Obtener resultado por ID
SELECT *
FROM resultado
WHERE id = :resultado_id;


-- 9.3 Obtener resultados de una mascota
SELECT
    r.id,
    r.puntaje,
    r.mascota_id,
    r.ejercicio_id,
    e.tipo,
    e.operacion
FROM resultado r
INNER JOIN ejercicio e
    ON e.id = r.ejercicio_id
WHERE r.mascota_id = :mascota_id
ORDER BY r.id DESC;


-- 9.4 Obtener resultados de un ejercicio
SELECT
    r.id,
    r.puntaje,
    r.mascota_id,
    r.ejercicio_id
FROM resultado r
WHERE r.ejercicio_id = :ejercicio_id
ORDER BY r.id DESC;


-- 9.5 Promedio de resultados
SELECT
    mascota_id,
    ROUND(AVG(puntaje), 2) AS promedio
FROM resultado
WHERE mascota_id = :mascota_id
GROUP BY mascota_id;


-- 9.6 Mejor puntaje
SELECT
    MAX(puntaje) AS mejor_puntaje
FROM resultado
WHERE mascota_id = :mascota_id;


-- 9.7 Cantidad de ejercicios realizados
SELECT
    COUNT(*) AS ejercicios_realizados
FROM resultado
WHERE mascota_id = :mascota_id;


-- 9.8 Estadísticas por tipo de ejercicio
SELECT
    e.tipo,
    COUNT(r.id) AS cantidad,
    ROUND(AVG(r.puntaje), 2) AS promedio,
    MAX(r.puntaje) AS mejor_puntaje
FROM ejercicio e
LEFT JOIN resultado r
    ON r.ejercicio_id = e.id
WHERE e.mascota_id = :mascota_id
GROUP BY e.tipo
ORDER BY e.tipo;


-- ============================================================
-- 10. EXÁMENES
-- ============================================================

-- 10.1 Crear examen
INSERT INTO examen (
    nombre,
    puntaje,
    mascota_id
)
VALUES (
    :nombre,
    :puntaje,
    :mascota_id
)
RETURNING *;


-- 10.2 Obtener examen por ID
SELECT *
FROM examen
WHERE id = :examen_id;


-- 10.3 Listar exámenes de una mascota
SELECT
    id,
    nombre,
    puntaje,
    mascota_id
FROM examen
WHERE mascota_id = :mascota_id
ORDER BY id DESC;


-- 10.4 Actualizar puntaje de un examen
UPDATE examen
SET puntaje = :puntaje
WHERE id = :examen_id
RETURNING *;


-- 10.5 Eliminar examen
DELETE FROM examen
WHERE id = :examen_id;


-- 10.6 Promedio de exámenes
SELECT
    mascota_id,
    ROUND(AVG(puntaje), 2) AS promedio
FROM examen
WHERE mascota_id = :mascota_id
GROUP BY mascota_id;


-- ============================================================
-- 11. CONSULTAS GENERALES DEL PERFIL
-- ============================================================

-- 11.1 Perfil completo
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
WHERE u.id = :usuario_id;


-- 11.2 Perfil + cantidad de compras
SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    m.id AS mascota_id,
    m.nombre AS mascota,
    m.comida,
    m.sueno,
    m.felicidad,
    COUNT(DISTINCT c.id) AS compras
FROM usuario u
LEFT JOIN mascota m
    ON m.usuario_id = u.id
LEFT JOIN compra c
    ON c.mascota_id = m.id
WHERE u.id = :usuario_id
GROUP BY
    u.id,
    u.nombre,
    m.id,
    m.nombre,
    m.comida,
    m.sueno,
    m.felicidad;


-- 11.3 Perfil + estadísticas académicas
SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    m.id AS mascota_id,
    m.nombre AS mascota,
    m.comida,
    m.sueno,
    m.felicidad,
    COUNT(DISTINCT r.id) AS resultados,
    COALESCE(ROUND(AVG(DISTINCT r.puntaje), 2), 0) AS promedio_ejercicios,
    COUNT(DISTINCT ex.id) AS examenes,
    COALESCE(ROUND(AVG(DISTINCT ex.puntaje), 2), 0) AS promedio_examenes
FROM usuario u
LEFT JOIN mascota m
    ON m.usuario_id = u.id
LEFT JOIN resultado r
    ON r.mascota_id = m.id
LEFT JOIN examen ex
    ON ex.mascota_id = m.id
WHERE u.id = :usuario_id
GROUP BY
    u.id,
    u.nombre,
    m.id,
    m.nombre,
    m.comida,
    m.sueno,
    m.felicidad;


-- ============================================================
-- 12. CONSULTAS PARA EL LOGIN
-- ============================================================

-- 12.1 Obtener los datos necesarios para validar login
-- El backend debe comparar la contraseña proporcionada con
-- el hash almacenado.
SELECT
    u.id AS usuario_id,
    u.nombre,
    c.usuario,
    c.contrasena,
    m.id AS mascota_id
FROM credenciales c
INNER JOIN usuario u
    ON u.id = c.usuario_id
LEFT JOIN mascota m
    ON m.usuario_id = u.id
WHERE c.usuario = :usuario;


-- ============================================================
-- 13. OPERACIONES RELACIONADAS CON LA LÓGICA DE EDUPETS
-- ============================================================

-- 13.1 Completar ejercicio y aumentar comida de la mascota
-- Ejemplo: aumentar 40 puntos después de completar
-- correctamente el ejercicio de multiplicación.
BEGIN;

INSERT INTO resultado (
    puntaje,
    mascota_id,
    ejercicio_id
)
VALUES (
    :puntaje,
    :mascota_id,
    :ejercicio_id
);

UPDATE mascota
SET comida = LEAST(100, comida + 40)
WHERE id = :mascota_id;

COMMIT;


-- 13.2 Guardar el estado después de una actividad
BEGIN;

UPDATE mascota
SET
    comida = :comida,
    sueno = :sueno,
    felicidad = :felicidad
WHERE id = :mascota_id;

INSERT INTO progreso (
    comida,
    sueno,
    felicidad,
    mascota_id
)
SELECT
    comida,
    sueno,
    felicidad,
    id
FROM mascota
WHERE id = :mascota_id;

COMMIT;


-- 13.3 Alimentar mascota y guardar progreso
BEGIN;

UPDATE mascota
SET comida = LEAST(100, comida + :cantidad)
WHERE id = :mascota_id;

INSERT INTO progreso (
    comida,
    sueno,
    felicidad,
    mascota_id
)
SELECT
    comida,
    sueno,
    felicidad,
    id
FROM mascota
WHERE id = :mascota_id;

COMMIT;


-- 13.4 Dormir y guardar progreso
BEGIN;

UPDATE mascota
SET sueno = LEAST(100, sueno + :cantidad)
WHERE id = :mascota_id;

INSERT INTO progreso (
    comida,
    sueno,
    felicidad,
    mascota_id
)
SELECT
    comida,
    sueno,
    felicidad,
    id
FROM mascota
WHERE id = :mascota_id;

COMMIT;


-- 13.5 Aumentar felicidad y guardar progreso
BEGIN;

UPDATE mascota
SET felicidad = LEAST(100, felicidad + :cantidad)
WHERE id = :mascota_id;

INSERT INTO progreso (
    comida,
    sueno,
    felicidad,
    mascota_id
)
SELECT
    comida,
    sueno,
    felicidad,
    id
FROM mascota
WHERE id = :mascota_id;

COMMIT;


-- ============================================================
-- 14. DASHBOARD / ESTADÍSTICAS
-- ============================================================

-- 14.1 Resumen de una mascota
SELECT
    m.id,
    m.nombre,
    m.comida,
    m.sueno,
    m.felicidad,
    COUNT(DISTINCT r.id) AS ejercicios,
    COUNT(DISTINCT ex.id) AS examenes,
    COUNT(DISTINCT c.id) AS compras
FROM mascota m
LEFT JOIN resultado r
    ON r.mascota_id = m.id
LEFT JOIN examen ex
    ON ex.mascota_id = m.id
LEFT JOIN compra c
    ON c.mascota_id = m.id
WHERE m.id = :mascota_id
GROUP BY
    m.id,
    m.nombre,
    m.comida,
    m.sueno,
    m.felicidad;


-- 14.2 Estadísticas generales de una mascota
SELECT
    m.id AS mascota_id,
    m.nombre AS mascota,
    COALESCE(r.promedio_resultados, 0) AS promedio_resultados,
    COALESCE(r.mejor_resultado, 0) AS mejor_resultado,
    COALESCE(r.total_resultados, 0) AS total_resultados,
    COALESCE(ex.promedio_examenes, 0) AS promedio_examenes,
    COALESCE(ex.total_examenes, 0) AS total_examenes
FROM mascota m
LEFT JOIN (
    SELECT
        mascota_id,
        ROUND(AVG(puntaje), 2) AS promedio_resultados,
        MAX(puntaje) AS mejor_resultado,
        COUNT(*) AS total_resultados
    FROM resultado
    GROUP BY mascota_id
) r
    ON r.mascota_id = m.id
LEFT JOIN (
    SELECT
        mascota_id,
        ROUND(AVG(puntaje), 2) AS promedio_examenes,
        COUNT(*) AS total_examenes
    FROM examen
    GROUP BY mascota_id
) ex
    ON ex.mascota_id = m.id
WHERE m.id = :mascota_id;


-- ============================================================
-- 15. CONSULTAS DE VALIDACIÓN DE RELACIONES
-- ============================================================

-- 15.1 Usuarios sin mascota
SELECT
    u.id,
    u.nombre
FROM usuario u
LEFT JOIN mascota m
    ON m.usuario_id = u.id
WHERE m.id IS NULL;


-- 15.2 Mascotas sin ejercicios
SELECT
    m.id,
    m.nombre
FROM mascota m
LEFT JOIN ejercicio e
    ON e.mascota_id = m.id
WHERE e.id IS NULL;


-- 15.3 Mascotas sin compras
SELECT
    m.id,
    m.nombre
FROM mascota m
LEFT JOIN compra c
    ON c.mascota_id = m.id
WHERE c.id IS NULL;


-- 15.4 Ejercicios sin resultados
SELECT
    e.id,
    e.tipo,
    e.operacion,
    e.mascota_id
FROM ejercicio e
LEFT JOIN resultado r
    ON r.ejercicio_id = e.id
WHERE r.id IS NULL;


-- ============================================================
-- 16. ELIMINACIONES
-- ============================================================

-- 16.1 Eliminar un resultado
DELETE FROM resultado
WHERE id = :resultado_id;


-- 16.2 Eliminar un ejercicio
-- Sus resultados se eliminan por ON DELETE CASCADE.
DELETE FROM ejercicio
WHERE id = :ejercicio_id;


-- 16.3 Eliminar una compra
DELETE FROM compra
WHERE id = :compra_id;


-- 16.4 Eliminar progreso
DELETE FROM progreso
WHERE id = :progreso_id;


-- 16.5 Eliminar mascota
-- Sus datos relacionados se eliminan por ON DELETE CASCADE.
DELETE FROM mascota
WHERE id = :mascota_id;


-- ============================================================
-- 17. VISTA CREADA EN schema.sql
-- ============================================================

-- Consultar la vista general
SELECT *
FROM vista_perfil_edupets
ORDER BY usuario_id;


-- ============================================================
-- 18. QUERIES DE ADMINISTRACIÓN / COMPROBACIÓN
-- ============================================================

-- 18.1 Cantidad de usuarios
SELECT COUNT(*) AS total_usuarios
FROM usuario;


-- 18.2 Cantidad de mascotas
SELECT COUNT(*) AS total_mascotas
FROM mascota;


-- 18.3 Cantidad de productos
SELECT COUNT(*) AS total_productos
FROM producto;


-- 18.4 Cantidad de ejercicios
SELECT COUNT(*) AS total_ejercicios
FROM ejercicio;


-- 18.5 Cantidad de resultados
SELECT COUNT(*) AS total_resultados
FROM resultado;


-- 18.6 Cantidad de exámenes
SELECT COUNT(*) AS total_examenes
FROM examen;


-- 18.7 Cantidad de compras
SELECT COUNT(*) AS total_compras
FROM compra;


-- ============================================================
-- 19. CONSULTA FINAL PARA CARGAR EL PERFIL DE LA MASCOTA
-- ============================================================
-- Esta es una de las consultas principales que puede utilizar
-- el backend al iniciar la aplicación.

SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    m.id AS mascota_id,
    m.nombre AS mascota,
    m.comida,
    m.sueno,
    m.felicidad
FROM usuario u
INNER JOIN mascota m
    ON m.usuario_id = u.id
WHERE u.id = :usuario_id;


-- ============================================================
-- FIN DE QUERIES.SQL
-- ============================================================
