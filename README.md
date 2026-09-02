# Edupets

Edupets es una aplicación web educativa de matemáticas con FastAPI, Jinja2, JWT en cookies, Google Sheets como almacenamiento provisional y una mascota virtual que evoluciona con las actividades.

## Características

- Registro e inicio de sesión con hash de contraseñas y JWT.
- Cookies `HttpOnly`, token CSRF de doble envío y validaciones básicas.
- Mascota con felicidad, comida y sueño que bajan con el tiempo.
- Sin escritura constante a Google Sheets: el navegador guarda cambios temporales y sincroniza al salir, cerrar pestaña o cerrar sesión.
- Actividades de sumas, restas, multiplicación y división con tres vidas por nivel.
- Objetivos plegables, progreso, recompensas y tienda.
- Diseño responsive inspirado en Duolingo.
- Configuración lista para Vercel.

## Estructura

```text
app/
  main.py
  config.py
  dependencies.py
  routers/
  services/
  models/
  static/
  templates/
  utils/
requirements.txt
vercel.json
.env.example
```

## Google Sheets

Hoja usada por defecto:

```text
https://docs.google.com/spreadsheets/d/1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw/edit
```

Columnas principales:

```text
A Usuario
B Contraseña
C Monedas
D Felicidad
E Comida
F Sueño
G Nombre
```

La app también usa `H Progreso` e `I Tareas` para guardar niveles y objetivos como JSON. Si la primera fila está vacía, la aplicación escribe estos encabezados automáticamente.

## Credenciales de Google

1. Entra a [Google Cloud Console](https://console.cloud.google.com/).
2. Crea o selecciona un proyecto.
3. Activa **Google Sheets API** en APIs y servicios.
4. Ve a **IAM y administración > Cuentas de servicio**.
5. Crea una cuenta de servicio y descarga una clave JSON.
6. Copia el correo de la cuenta de servicio, por ejemplo:

```text
edupets-service@tu-proyecto.iam.gserviceaccount.com
```

7. Abre la hoja de cálculo, pulsa **Compartir** y agrega ese correo con permiso de editor.

## Configuración local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Coloca la clave descargada en:

```text
credentials/service-account.json
```

Luego ajusta `.env`:

```text
SECRET_KEY=un-valor-largo-y-aleatorio
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
COOKIE_SECURE=false
```

Ejecuta:

```bash
fastapi dev app/main.py
```

La app queda disponible en:

```text
http://127.0.0.1:8000
```

## Despliegue en Vercel

1. Sube el proyecto a un repositorio.
2. Importa el repositorio en Vercel.
3. Configura estas variables de entorno:

```text
APP_ENV=production
SECRET_KEY=un-valor-largo-y-aleatorio
COOKIE_SECURE=true
GOOGLE_SHEET_ID=1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw
GOOGLE_SHEET_NAME=Hoja 1
GOOGLE_SERVICE_ACCOUNT_INFO=<contenido completo del JSON de la cuenta de servicio>
```

Para `GOOGLE_SERVICE_ACCOUNT_INFO`, pega el JSON completo de la clave como una sola variable. Vercel conserva el contenido y la app lo parsea al iniciar.

## Notas de producción

- Cambia siempre `SECRET_KEY`.
- Mantén la clave JSON fuera del repositorio.
- Usa `COOKIE_SECURE=true` solo con HTTPS.
- Google Sheets sirve como base provisional; para alto tráfico conviene migrar a PostgreSQL, MySQL o Firestore.
