-- Edupets - esquema de base de datos
-- Motor recomendado: PostgreSQL
-- Archivo: schema.sql
--
-- Este archivo crea la estructura equivalente al modelo entidad-relación
-- de Edupets.
--
-- NOTA:
-- El backend utiliza database/repository.py para acceder a este esquema
-- PostgreSQL en Neon.

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

-- ============================================================
-- CAMBIOS PARA SISTEMA DE CAMBIO DE MASCOTA
-- ============================================================

ALTER TABLE mascota
    ADD COLUMN IF NOT EXISTS especie VARCHAR(20) NOT NULL DEFAULT 'pinguino';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_mascota_especie'
    ) THEN
        ALTER TABLE mascota
            ADD CONSTRAINT chk_mascota_especie
            CHECK (especie IN ('pinguino', 'oso', 'zorro'));
    END IF;
END $$;

INSERT INTO producto (nombre, precio)
VALUES ('Oso', 100), ('Zorro', 150)
ON CONFLICT (nombre) DO NOTHING;

-- ============================================================
-- CAMBIOS PARA INVENTARIO Y USO DE PRODUCTOS
-- Ejecutar las instrucciones siguientes en Neon
-- ============================================================

CREATE TABLE IF NOT EXISTS inventario (
    usuario_id  INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    cantidad    INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT pk_inventario PRIMARY KEY (usuario_id, producto_id),
    CONSTRAINT fk_inventario_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuario(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_inventario_producto
        FOREIGN KEY (producto_id)
        REFERENCES producto(id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT chk_inventario_cantidad CHECK (cantidad > 0)
);

CREATE INDEX IF NOT EXISTS idx_inventario_producto_id
    ON inventario(producto_id);

ALTER TABLE mascota
    ADD COLUMN IF NOT EXISTS especie VARCHAR(20) NOT NULL DEFAULT 'pinguino';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_mascota_especie'
    ) THEN
        ALTER TABLE mascota
            ADD CONSTRAINT chk_mascota_especie
            CHECK (especie IN ('pinguino', 'oso', 'zorro'));
    END IF;
END $$;

-- CAMBIOS 2
-- Permite seleccionar nutria y restaura al pingüino inicial desde la tienda.
DO $$
DECLARE
    species_constraint TEXT;
BEGIN
    SELECT pg_get_constraintdef(oid)
    INTO species_constraint
    FROM pg_constraint
    WHERE conrelid = 'mascota'::regclass
      AND conname = 'chk_mascota_especie';

    IF species_constraint IS NULL
       OR species_constraint NOT LIKE '%nutria%'
       OR species_constraint LIKE '%predeterminada%' THEN
        ALTER TABLE mascota DROP CONSTRAINT IF EXISTS chk_mascota_especie;
        -- Older deployments used this value for the default penguin.
        UPDATE mascota SET especie = 'pinguino' WHERE especie = 'predeterminada';
        ALTER TABLE mascota
            ADD CONSTRAINT chk_mascota_especie
            CHECK (especie IN ('pinguino', 'oso', 'zorro', 'nutria'));
    END IF;
END $$;

-- La aplicación representa precios y saldos como monedas enteras.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'producto'::regclass
          AND conname = 'chk_producto_precio_entero'
    ) THEN
        ALTER TABLE producto
            ADD CONSTRAINT chk_producto_precio_entero
            CHECK (precio = trunc(precio));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'monedero'::regclass
          AND conname = 'chk_monedero_saldo_entero'
    ) THEN
        ALTER TABLE monedero
            ADD CONSTRAINT chk_monedero_saldo_entero
            CHECK (saldo_plata = trunc(saldo_plata));
    END IF;
END $$;

INSERT INTO producto (nombre, precio)
SELECT nuevo.nombre, nuevo.precio
FROM (VALUES ('pinguino', 0), ('nutria', 125)) AS nuevo(nombre, precio)
WHERE NOT EXISTS (
    SELECT 1
    FROM producto AS existente
    WHERE LOWER(existente.nombre) = LOWER(nuevo.nombre)
)
ON CONFLICT (nombre) DO NOTHING;
