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

## MONEDERO

Registra los exámenes realizados por las mascotas.

**Campos:**

-   `id_monedero`: entero, clave primaria.
-   `id_usuario`: entero, clave foranea hacia `USUARIO.id`.
-   `saldo_plata`: decimal.
-   `ultima_actualizacion`: datetime .

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

## MASCOTA → MONEDERO

**Tipo: 1:N**

Una mascota puede tener distintas transacciones y cada transaccion registra el
dinero gasto o obtenido de esa mascota.

**Relación:**\
`MASCOTA 1 ─── N MONEDERO`

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

------------------------------------------------------------------------

# Guía de desarrollo y ejecución

## Descripción del proyecto

EduPets es una aplicación web educativa para practicar matemáticas mediante una experiencia de gamificación. Cada cuenta tiene una mascota virtual con niveles de comida, sueño y felicidad que disminuyen con el tiempo. El estudiante puede completar actividades, guardar resultados, ganar monedas, comprar objetos y otras mascotas, administrar su inventario y cuidar a su compañero.

Las contraseñas se guardan como hashes bcrypt, no como texto legible. El estado persistente se carga y guarda en PostgreSQL; el navegador mantiene además una copia local de estado para la experiencia interactiva. La página de la mascota permite sincronizarla y usar los objetos disponibles.

## Tecnologías y arquitectura

- **Backend:** Python 3, FastAPI y ASGI. `app/main.py` crea la aplicación, registra las rutas, sirve los archivos estáticos y gestiona el contexto de sesión y CSRF. Las rutas se organizan en `app/routers/`; la lógica de autenticación, mascota, actividades y tienda está en `app/services/`.
- **Datos y validación:** modelos Pydantic en `app/models/`, configuración mediante `pydantic-settings` en `app/config.py` y acceso asíncrono parametrizado a PostgreSQL con `asyncpg` en `database/repository.py`.
- **Interfaz:** Jinja2 renderiza las páginas en `app/templates/`. CSS y JavaScript sin framework se encuentran en `app/static/`. `app/static/js/app.js` gestiona el tema, CSRF y estado compartido del navegador; los demás scripts controlan mascota, actividades y tienda.
- **Persistencia:** PostgreSQL, recomendado a través de Neon. El esquema y sus relaciones están en `database/schema.sql`; el repositorio hace consultas SQL parametrizadas y transacciones para operaciones que modifican varios registros.
- **Sesión y CSRF:** la sesión es un JWT firmado en una cookie `HttpOnly`; la identidad se vuelve a comprobar contra la base de datos. Las peticiones que modifican datos validan el token CSRF enviado junto con la cookie.
- **Otras carpetas:** `database/queries.sql` contiene consultas SQL auxiliares; `scripts/generate_assets.py` genera recursos gráficos; `verify_config.py` comprueba la conexión configurada. `vercel.json` conserva la configuración de despliegue existente en Vercel.

El esquema refleja el código actual: sus tablas son `usuario`, `credenciales`, `mascota`, `progreso`, `producto`, `ejercicio`, `monedero`, `compra`, `resultado` e `inventario`. `producto` y `ejercicio` son datos compartidos; las relaciones de cuenta usan cascadas para eliminar solo los registros propios. El esquema actual no define una tabla `examen`; algunas descripciones conceptuales anteriores de este README no corresponden a tablas activas.

## Requisitos previos

- Python **3.10 o posterior** y `pip`.
- Git para clonar el repositorio.
- Acceso de red a una base de datos PostgreSQL configurada. El código está preparado para Neon; también puede usarse PostgreSQL compatible.
- `psql` (cliente PostgreSQL), solo si se aplicará `schema.sql` desde una terminal. No es necesario para ejecutar la aplicación una vez preparado el esquema.
- Un navegador web moderno.

No se necesita Node.js: el frontend usa JavaScript y CSS servidos por FastAPI.

## Instalación y ejecución local

### 1. Clonar y entrar al proyecto

```sh
git clone https://github.com/SamuelDiazS/Edupets.git
cd Edupets
```

### 2. Crear y activar un entorno virtual

Linux y macOS:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

En Windows, si PowerShell bloquea la activación, puede ejecutarse la aplicación usando directamente `.venv\Scripts\python.exe` sin cambiar la política del equipo.

### 3. Instalar dependencias

Con el entorno activado, en Linux/macOS:

```sh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Windows PowerShell, sustituye `python` por `py` en esos dos comandos.

### 4. Configurar el entorno

La aplicación lee un archivo `.env` en la raíz del repositorio. No hay un `.env.example` disponible en el árbol actual; crea `.env` localmente y no lo publiques. Como mínimo configura una URL válida de PostgreSQL:

```dotenv
DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/BASE?sslmode=require
```

Configura `SECRET_KEY` con un valor aleatorio privado, especialmente fuera del entorno local. Puede generarse con Python:

```sh
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

El proyecto reconoce las variables ya declaradas en `app/config.py`:

| Variable | Uso |
| --- | --- |
| `DATABASE_URL` | Obligatoria para conectar con PostgreSQL/Neon. |
| `SECRET_KEY` | Firma de los JWT; el valor predeterminado es solo para desarrollo y debe reemplazarse. |
| `JWT_ALGORITHM` | Algoritmo de firma; predeterminado `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración del JWT y cookie, predeterminada a siete días. |
| `COOKIE_NAME` | Nombre de la cookie de sesión. |
| `COOKIE_SECURE` | Activa el atributo `Secure`; déjalo `false` en HTTP local y usa `true` bajo HTTPS. |
| `CSRF_COOKIE_NAME` | Nombre de la cookie CSRF. |
| `APP_NAME` | Nombre de la aplicación en FastAPI; predeterminado `Edupets`. |
| `APP_ENV` | Entorno, predeterminado `development`; actualmente no activa lógica adicional. |

Las variables no indicadas conservan los valores predeterminados de `app/config.py`. En Vercel, configura las mismas variables desde la configuración de entorno del proyecto; no incluyas credenciales en el repositorio ni cambies `vercel.json` para esta tarea.

### 5. Preparar la base de datos

1. Crea una base de datos PostgreSQL en Neon (o prepara una instancia PostgreSQL accesible) y copia su cadena de conexión en `DATABASE_URL`. En Neon utiliza la URL PostgreSQL ofrecida por el panel y conserva los parámetros SSL requeridos.
2. Si el esquema aún no existe, ejecuta el archivo desde una terminal con `psql` y una variable de entorno temporal configurada con tu URL:

Linux/macOS:

```sh
export DATABASE_URL='postgresql://USUARIO:CONTRASENA@HOST/BASE?sslmode=require'
psql "$DATABASE_URL" -f database/schema.sql
```

Windows PowerShell:

```powershell
$env:DATABASE_URL = 'postgresql://USUARIO:CONTRASENA@HOST/BASE?sslmode=require'
psql $env:DATABASE_URL -f database/schema.sql
```

Reemplaza los marcadores localmente; no uses una cadena de ejemplo como credencial. El cliente `psql` no carga automáticamente el archivo `.env`. También se puede ejecutar el contenido de `database/schema.sql` desde un editor SQL de Neon que admita el script completo.

`schema.sql` crea las tablas, claves, restricciones, índices, vista y datos iniciales definidos por el proyecto. En instalaciones existentes, ejecutar SQL nuevo no cambia automáticamente la base remota: aplica el archivo o la migración correspondiente de forma explícita. Para esta mejora se añadió el marcador `-- CAMBIOS 2`, pero no se requieren instrucciones DDL ni una migración nueva, porque las claves foráneas actuales ya eliminan en cascada los datos asociados a una cuenta.

Comprueba la URL usando el verificador incluido (lee `.env` desde la raíz):

```sh
python verify_config.py
```

### 6. Arrancar y abrir EduPets

Desde la raíz y con el entorno virtual activado:

```sh
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

En Windows se puede usar `py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`. Abre <http://127.0.0.1:8000> en el navegador. Para detener el servidor, pulsa `Ctrl+C` en la terminal.

### Errores habituales

- **Falta `DATABASE_URL` o falla la conexión:** confirma que `.env` está en la raíz, que la URL no contiene marcadores y que la base permite conexiones desde tu red. Neon requiere la conexión SSL indicada por su panel.
- **No se encuentra una tabla o columna:** aplica `database/schema.sql` a la base configurada y verifica que la aplicación usa la misma base.
- **`uvicorn` o un módulo no encontrado:** activa el entorno virtual e instala de nuevo con `python -m pip install -r requirements.txt`.
- **El puerto 8000 está ocupado:** cambia `--port 8000` por otro puerto disponible y usa esa dirección al abrir el navegador.
- **Falla `verify_config.py`:** ejecútalo desde la raíz del repositorio; verifica que `.env` tenga una línea `DATABASE_URL=...` y una URL PostgreSQL válida.

## Base de datos y eliminación de cuentas

Los datos operativos se almacenan en PostgreSQL mediante `asyncpg`; `database/repository.py` relaciona al usuario con credenciales, mascota, monedero e inventario, y los resultados/progresos pertenecen a la mascota. El campo de contraseña contiene el hash bcrypt. Las tablas `producto` y `ejercicio` son compartidas y no se eliminan al borrar una cuenta.

La ruta de borrado obtiene el nombre de usuario de la sesión autenticada y ejecuta una sola sentencia parametrizada `DELETE` dentro de una transacción. Las FK `ON DELETE CASCADE` eliminan credenciales, mascota, monedero, compras, inventario, progreso y resultados relacionados. PostgreSQL revierte la sentencia completa si una restricción u operación falla. No se acepta un identificador de cuenta desde el navegador y no se añade esquema nuevo para esta funcionalidad.

El final de `database/schema.sql` conserva todas sus definiciones previas y añade el comentario SQL exacto `-- CAMBIOS 2` seguido de una nota; no hay SQL adicional que aplicar para la eliminación de cuentas.

## Créditos y bibliotecas utilizadas

Las dependencias de terceros declaradas en `requirements.txt` y los paquetes de terceros importados por el código son:

| Biblioteca | Función | Documentación oficial | Licencia upstream |
| --- | --- | --- | --- |
| FastAPI | Rutas HTTP, dependencias y aplicación ASGI. | [fastapi.tiangolo.com](https://fastapi.tiangolo.com/) | MIT |
| Uvicorn | Servidor ASGI utilizado para ejecutar localmente la aplicación. | [uvicorn.org](https://www.uvicorn.org/) | BSD-3-Clause |
| asyncpg | Cliente PostgreSQL asíncrono y pool de conexiones. | [Documentación asyncpg](https://magicstack.github.io/asyncpg/current/) | Apache-2.0 |
| Loguru | Registro de eventos y errores del repositorio y dependencias. | [loguru.readthedocs.io](https://loguru.readthedocs.io/) | MIT |
| Jinja2 | Renderizado de plantillas HTML. | [jinja.palletsprojects.com](https://jinja.palletsprojects.com/) | BSD-3-Clause |
| Pydantic | Modelos y validación de datos. | [docs.pydantic.dev](https://docs.pydantic.dev/) | MIT |
| pydantic-settings | Carga de configuración desde variables de entorno y `.env`. | [docs.pydantic.dev/latest/concepts/pydantic_settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | MIT |
| python-jose | Creación y validación de JWT de sesión. | [python-jose.readthedocs.io](https://python-jose.readthedocs.io/) | MIT |
| cryptography | Backend criptográfico solicitado por el extra `python-jose[cryptography]`. | [cryptography.io](https://cryptography.io/en/latest/) | Apache-2.0 / BSD-3-Clause |
| Passlib | Contexto de hash y verificación bcrypt de contraseñas. | [passlib.readthedocs.io](https://passlib.readthedocs.io/) | BSD-3-Clause |
| bcrypt | Algoritmo/backend de hash usado por Passlib. | [bcrypt.readthedocs.io](https://bcrypt.readthedocs.io/) | Apache-2.0 |
| python-multipart | Lectura de formularios enviados al backend. | [Documentación python-multipart](https://andrew-d.github.io/python-multipart/) | Apache-2.0 |
| Starlette | Infraestructura ASGI usada internamente por FastAPI, incluida la integración de plantillas y archivos estáticos. | [www.starlette.io](https://www.starlette.io/) | BSD-3-Clause |

Las restricciones de versión están en `requirements.txt`; `pydantic` y `uvicorn` se declaran explícitamente porque el código los importa o necesita para la ejecución local. FastAPI instala Starlette y las demás dependencias transitivas automáticamente. Los módulos de Python como `asyncio`, `logging`, `secrets`, `pathlib` y `json` pertenecen a la biblioteca estándar y no requieren instalación aparte.

**Tecnologías y servicios, no bibliotecas:** Python, HTML, CSS y JavaScript; PostgreSQL como motor de base de datos; Neon como servicio PostgreSQL administrado ([documentación](https://neon.tech/docs)); Vercel como plataforma de despliegue configurada en `vercel.json` ([documentación](https://vercel.com/docs)); y YouTube para el video tutorial.

**Autoría del proyecto:** se conserva el reconocimiento al repositorio [SamuelDiazS/Edupets](https://github.com/SamuelDiazS/Edupets). Los créditos anteriores de este README se mantienen sin sustituirlos.
