-- Edupets - esquema de base de datos
-- Motor recomendado: PostgreSQL
-- Archivo: schema.sql
--
-- Este archivo crea la estructura equivalente al modelo entidad-relación
-- de Edupets.
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
-- DROP TABLE IF EXISTS compra CASCADE;
-- DROP TABLE IF EXISTS monedero CASCADE;
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
CREATE TABLE IF NOT EXISTS ejercicio (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo        VARCHAR(30) NOT NULL,
    operacion   VARCHAR(20) NOT NULL
);


-- ============================================================
-- 8. MONEDERO
-- ============================================================
-- Relación: USUARIO 1 --- 1 MONEDERO
CREATE TABLE IF NOT EXISTS monedero (
    id_monedero         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id          INTEGER NOT NULL UNIQUE,
    saldo_plata         NUMERIC(10,2) NOT NULL DEFAULT 0,
    ultima_actualizacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_monedero_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_monedero_saldo
        CHECK (saldo_plata >= 0)
);

CREATE INDEX IF NOT EXISTS idx_monedero_usuario_id
    ON monedero(usuario_id);


-- ============================================================
-- 9. COMPRA
-- ============================================================
-- MONEDERO N --- N PRODUCTO
CREATE TABLE IF NOT EXISTS compra (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    monedero_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,

    CONSTRAINT fk_compra_monedero
        FOREIGN KEY (monedero_id)
        REFERENCES monedero(id_monedero)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_compra_producto
        FOREIGN KEY (producto_id)
        REFERENCES producto(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_compra_monedero_id
    ON compra(monedero_id);

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
    ('caramelos', 25)
ON CONFLICT (nombre) DO NOTHING;


-- ============================================================
-- 12. EJERCICIOS BASE
-- ============================================================
-- Los ejercicios de la aplicación actual son:
-- sumas, restas, multiplicación y división.
--
-- Se pueden insertar como actividades globales desde el backend.


-- ============================================================
-- VISTA ÚTIL PARA EL BACKEND
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
