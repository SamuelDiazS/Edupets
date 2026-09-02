# Documentación de la base de datos --- EduPets

## Video explicativo
- https://youtu.be/9L-wekeTEOk?si=qEA2O17OXD61GGHb

## 1. Breve resumen del proyecto

**EduPets** es una plataforma web educativa que busca hacer más
divertido el aprendizaje de matemáticas. El usuario tiene una mascota
virtual que debe cuidar mientras realiza ejercicios y actividades.

La mascota tiene necesidades como **comida, sueño y felicidad**, y el
estudiante puede realizar ejercicios, exámenes y compras dentro de la
plataforma. La idea combina educación y gamificación para motivar al
estudiante a practicar y avanzar.

------------------------------------------------------------------------
## Requisitos funcionales

Esta base de datos soporta:
- El usuario puede crear un usuario mediante una interfaz de registro.
- Sistema asíncrono que permite que múltiples usuales usen nuestra pagina.
- El sistema recibe respuestas dadas por los usuarios y responde de forma negativa o positiva.
- El sistema deberá entregar al estudiante determinada cantidad de monedas conforme complete actividades.
- El sistema debe permitir gastar las monedas en productos
- El sistema debe permitir usar los productos

---

## 2. Propósito

La base de datos tiene como propósito **guardar y organizar la
información necesaria para que EduPets funcione correctamente**.

Entre la información que maneja se encuentra:

-   Datos básicos de los usuarios.
-   Credenciales de inicio de sesión.
-   Información y estado de las mascotas.
-   Progreso de las mascotas.
-   Ejercicios y resultados.
-   Exámenes y puntajes.
-   Productos disponibles y compras realizadas.

De esta forma, la información queda organizada y relacionada entre sí,
evitando tener todos los datos almacenados en una sola tabla.

------------------------------------------------------------------------

## 3. Alcance

La base de datos está pensada para cubrir las funciones principales de
EduPets:

1.  Registrar usuarios.
2.  Manejar las credenciales de acceso.
3.  Crear y asociar una mascota con cada usuario.
4.  Guardar el estado de la mascota.
5.  Registrar el progreso.
6.  Gestionar ejercicios y sus resultados.
7.  Registrar exámenes y sus puntajes.
8.  Gestionar productos.
9.  Registrar las compras realizadas por las mascotas.

El modelo está enfocado principalmente en el funcionamiento académico y
de gamificación de EduPets.

------------------------------------------------------------------------

# 4. Entidades de la base de datos

La base de datos representada está formada por **9 entidades/tablas
principales**:

  -----------------------------------------------------------------------
  Entidad                             Función
  ----------------------------------- -----------------------------------
  **USUARIO**                         Guarda la información básica del
                                      usuario.

  **CREDENCIALES**                    Guarda los datos utilizados para
                                      iniciar sesión.

  **MASCOTA**                         Guarda la información y estado de
                                      la mascota virtual.

  **PROGRESO**                        Registra información relacionada
                                      con el avance o estado de la
                                      mascota.

  **PRODUCTO**                        Contiene los productos que pueden
                                      adquirirse.

  **COMPRA**                          Registra las compras realizadas.

  **EJERCICIO**                       Almacena los diferentes ejercicios
                                      disponibles.

  **RESULTADO**                       Guarda los resultados obtenidos en
                                      los ejercicios.

  **EXAMEN**                          Registra los exámenes realizados y
                                      sus puntajes.
  -----------------------------------------------------------------------

> **Nota:** En el diagrama se observan 10 tablas: USUARIO, CREDENCIALES,
> MASCOTA, PROGRESO, PRODUCTO, COMPRA, EJERCICIO, RESULTADO y EXAMEN. La
> última fila de la tabla anterior solo sirve como aclaración; las
> entidades reales son las nueve tablas visibles en el diagrama.

------------------------------------------------------------------------

# 5. Descripción de cada tabla

## USUARIO

Es la tabla principal para identificar a las personas que utilizan
EduPets.

**Campos:**

-   `id`: entero, clave primaria (**PK**).
-   `nombre`: texto.

Se relaciona con **CREDENCIALES** y **MASCOTA**.

------------------------------------------------------------------------

## CREDENCIALES

Almacena la información necesaria para el inicio de sesión.

**Campos:**

-   `id`: entero, clave primaria.
-   `usuario`: texto.
-   `contraseña`: texto.
-   `usuario(id)`: entero, clave foránea (**FK**) que apunta a
    `USUARIO.id`.

Su relación con USUARIO permite asociar las credenciales con el usuario
correspondiente.

------------------------------------------------------------------------

## MASCOTA

Es una de las tablas centrales del proyecto, ya que representa la
mascota virtual del usuario.

**Campos:**

-   `id`: entero, clave primaria.
-   `nombre`: texto.
-   `comida`: entero.
-   `sueño`: entero.
-   `felicidad`: entero.
-   `usuario(id)`: entero, clave foránea que apunta a `USUARIO.id`.

Los valores de comida, sueño y felicidad representan el estado de la
mascota.

------------------------------------------------------------------------

## PROGRESO

Guarda información relacionada con el progreso de la mascota.

**Campos:**

-   `id`: entero, clave primaria.
-   `comida`: entero.
-   `sueño`: entero.
-   `felicidad`: entero.
-   `mascota(id)`: entero, clave foránea que apunta a `MASCOTA.id`.

Esta tabla puede utilizarse para conservar registros del estado de la
mascota a medida que el usuario avanza.

------------------------------------------------------------------------

## PRODUCTO

Contiene los productos que pueden ser utilizados o comprados dentro del
sistema.

**Campos:**

-   `id`: entero, clave primaria.
-   `nombre`: texto.
-   `precio`: decimal/float.

------------------------------------------------------------------------

## COMPRA

Registra las compras realizadas y conecta a una mascota con un producto.

**Campos:**

-   `id`: entero, clave primaria.
-   `mascota(id)`: clave foránea hacia `MASCOTA.id`.
-   `producto(id)`: clave foránea hacia `PRODUCTO.id`.

Por lo tanto, funciona como una tabla que conecta **MASCOTA** y
**PRODUCTO**.

------------------------------------------------------------------------

## EJERCICIO

Almacena los ejercicios matemáticos disponibles.

**Campos:**

-   `id`: entero, clave primaria.
-   `tipo`: texto.
-   `operacion`: texto.

El campo `tipo` permite diferenciar tipos de ejercicios y `operacion`
almacena la operación matemática correspondiente.

------------------------------------------------------------------------

## RESULTADO

Guarda los resultados obtenidos al realizar ejercicios.

**Campos:**

-   `id`: entero, clave primaria.
-   `puntaje`: entero.
-   `mascota(id)`: clave foránea hacia `MASCOTA.id`.
-   `ejercicio(id)`: clave foránea hacia `EJERCICIO.id`.

Esto permite saber qué puntaje obtuvo una mascota en un ejercicio
determinado.

------------------------------------------------------------------------

## EXAMEN

Registra los exámenes realizados por las mascotas.

**Campos:**

-   `id`: entero, clave primaria.
-   `nombre`: texto.
-   `puntaje`: entero.
-   `mascota(id)`: clave foránea hacia `MASCOTA.id`.

------------------------------------------------------------------------

# 6. Relaciones entre las tablas

El diagrama utiliza relaciones de tipo **uno a uno (1:1)** y **uno a
muchos (1:N)**.

## USUARIO → CREDENCIALES

**Tipo: 1:1**

Un usuario tiene asociadas sus credenciales de acceso. La tabla
CREDENCIALES utiliza `usuario(id)` como clave foránea hacia USUARIO.

**Relación:**\
`USUARIO 1 ─── 1 CREDENCIALES`

------------------------------------------------------------------------

## USUARIO → MASCOTA

**Tipo: 1:1**

Cada usuario tiene asociada una mascota virtual. La tabla MASCOTA guarda
`usuario(id)` como clave foránea.

**Relación:**\
`USUARIO 1 ─── 1 MASCOTA`

------------------------------------------------------------------------

## MASCOTA → PROGRESO

**Tipo: 1:N**

Una mascota puede tener varios registros de progreso. Cada registro de
PROGRESO pertenece a una mascota mediante `mascota(id)`.

**Relación:**\
`MASCOTA 1 ─── N PROGRESO`

------------------------------------------------------------------------

## MASCOTA → COMPRA

**Tipo: 1:N**

Una mascota puede realizar varias compras. Cada compra está asociada a
una mascota mediante `mascota(id)`.

**Relación:**\
`MASCOTA 1 ─── N COMPRA`

------------------------------------------------------------------------

## PRODUCTO → COMPRA

**Tipo: 1:N**

Un producto puede aparecer en varias compras. Cada compra identifica el
producto mediante `producto(id)`.

**Relación:**\
`PRODUCTO 1 ─── N COMPRA`

Por esta razón, **COMPRA funciona como una tabla intermedia entre
MASCOTA y PRODUCTO**.

------------------------------------------------------------------------

## MASCOTA → EJERCICIO

**Tipo: 1:N**

El diagrama representa que una mascota realiza ejercicios. Una mascota
puede realizar varios ejercicios a lo largo de su uso de la plataforma.

**Relación conceptual:**\
`MASCOTA 1 ─── N EJERCICIO`

En el esquema mostrado, esta relación está representada en el diagrama,
aunque la tabla EJERCICIO no muestra una FK `mascota(id)`.

------------------------------------------------------------------------

## EJERCICIO → RESULTADO

**Tipo: 1:N**

Un ejercicio puede generar múltiples resultados de diferentes intentos o
mascotas. Cada resultado identifica el ejercicio mediante
`ejercicio(id)`.

**Relación:**\
`EJERCICIO 1 ─── N RESULTADO`

------------------------------------------------------------------------

## MASCOTA → RESULTADO

**Tipo: 1:N**

Una mascota puede tener múltiples resultados. Cada resultado identifica
a la mascota mediante `mascota(id)`.

**Relación:**\
`MASCOTA 1 ─── N RESULTADO`

------------------------------------------------------------------------

## MASCOTA → EXAMEN

**Tipo: 1:N**

Una mascota puede realizar varios exámenes y cada examen registra el
puntaje obtenido por esa mascota.

**Relación:**\
`MASCOTA 1 ─── N EXAMEN`

------------------------------------------------------------------------

# 7. ¿Cómo funciona la base de datos en conjunto?

La estructura puede entenderse de la siguiente manera:

**USUARIO** es el punto de partida. El usuario tiene sus
**CREDENCIALES** para ingresar y una **MASCOTA** asociada.

La mascota tiene sus valores de **comida, sueño y felicidad**, y puede
generar registros de **PROGRESO**.

Durante el uso de EduPets, la mascota puede realizar **EJERCICIOS** y
obtener **RESULTADOS**. También puede realizar **EXÁMENES**, donde se
guarda el puntaje obtenido.

Por otra parte, existen **PRODUCTOS** que pueden ser adquiridos. Cada
**COMPRA** conecta el producto comprado con la mascota que lo adquirió.

En forma resumida:

``` text
USUARIO
 ├── CREDENCIALES
 └── MASCOTA
      ├── PROGRESO
      ├── COMPRA ─── PRODUCTO
      ├── RESULTADO ─── EJERCICIO
      └── EXAMEN
```

------------------------------------------------------------------------

# 8. Optimizaciones de la base de datos

Algunas decisiones que ayudan a mantener organizada la base de datos
son:

-   **Uso de claves primarias:** cada tabla tiene un `id` que identifica
    de forma única cada registro.
-   **Uso de claves foráneas:** permiten conectar las tablas y mantener
    relaciones entre los datos.
-   **Separación por entidades:** los usuarios, mascotas, productos,
    ejercicios y resultados están separados en tablas diferentes.
-   **Tabla COMPRA como relación:** evita guardar directamente todos los
    datos del producto dentro de la mascota.
-   **Tipos de datos adecuados:** se utilizan enteros para
    identificadores, puntajes y estados, textos para nombres y
    operaciones, y valores decimales para los precios.
-   **Organización de la información:** dividir los datos en diferentes
    tablas evita concentrar toda la información en una sola estructura.

Como mejoras adicionales para una versión más completa, se podrían
agregar índices en las claves foráneas y restricciones `CHECK` para
evitar valores inválidos, por ejemplo, niveles de comida, sueño o
felicidad fuera del rango permitido.

------------------------------------------------------------------------

# 9. Limitaciones de la base de datos

Aunque la estructura cubre las funciones principales de EduPets, todavía
tiene algunas limitaciones:

-   **No se registran fechas:** no se puede saber exactamente cuándo se
    realizó un ejercicio, examen, compra o registro de progreso.
-   **La tabla COMPRA no tiene cantidad:** no permite registrar
    fácilmente varias unidades de un mismo producto dentro de una
    compra.
-   **Faltan datos de los ejercicios:** la tabla EJERCICIO contiene el
    tipo y la operación, pero podría necesitar información adicional
    como respuesta correcta, dificultad o recompensa.
-   **No hay información detallada de los exámenes:** podría ser útil
    almacenar fecha, duración, cantidad de preguntas o nivel.
-   **Seguridad de credenciales:** la contraseña no debería almacenarse
    directamente como texto; en una aplicación real debería utilizarse
    un sistema de hash seguro.
-   **Pocas restricciones:** sería recomendable controlar mediante
    restricciones que los valores de comida, sueño y felicidad estén
    dentro de los rangos permitidos.
-   **Relación MASCOTA--EJERCICIO:** el diagrama muestra la relación
    conceptual, pero la tabla EJERCICIO no tiene una clave foránea hacia
    MASCOTA. Los resultados son los que permiten relacionar directamente
    una mascota con un ejercicio.

------------------------------------------------------------------------

# 10. Conclusión

La base de datos de **EduPets** está diseñada para organizar las
principales funciones de la plataforma: usuarios, mascotas virtuales,
progreso, ejercicios, resultados, exámenes, productos y compras.

Su estructura basada en **claves primarias y foráneas** permite conectar
la información y mantenerla organizada. Aunque el modelo cubre las
necesidades principales del proyecto, todavía puede mejorarse agregando
información histórica, restricciones, índices, más detalles sobre
ejercicios y exámenes y mejores medidas de seguridad para las
credenciales.

En general, la base de datos sirve como la estructura que permite que
EduPets no sea solamente una página educativa, sino una plataforma capaz
de **guardar el progreso y las acciones de cada usuario dentro de la
experiencia de la mascota virtual**.