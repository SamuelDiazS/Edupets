# Configuración de Google Sheets para Edupets

El error "Error en el servidor" al registrarse indica que **las credenciales de Google Sheets no están configuradas**.

## Pasos para Configurar Google Sheets

### 1. Crear una Cuenta de Servicio en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. En la barra de búsqueda, busca "Google Sheets API"
4. Haz clic en la API y presiona "Habilitar"
5. Ve a "IAM y administración" > "Cuentas de servicio"
6. Haz clic en "Crear una cuenta de servicio"
7. Completa el nombre (ej: `edupets-service`)
8. Haz clic en "Crear y continuar"
9. Asigna el rol "Editor" (para poder escribir en hojas)
10. Haz clic en "Continuar"

### 2. Descargar la Clave JSON

1. En la página de cuentas de servicio, haz clic en la cuenta que acabas de crear
2. Ve a la pestaña "Claves"
3. Haz clic en "Agregar clave" > "Crear clave nueva"
4. Selecciona formato JSON
5. Haz clic en "Crear"
6. Se descargará un archivo JSON automáticamente
7. **Guarda este archivo en**: `credentials/service-account.json` (en la raíz del proyecto)

### 3. Compartir la Hoja de Google Sheets

1. Abre el archivo JSON descargado
2. Copia el valor de `"client_email"` (algo como: `edupets-service@tu-proyecto.iam.gserviceaccount.com`)
3. Ve a tu Google Sheet: https://docs.google.com/spreadsheets/d/1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw/edit
4. Haz clic en "Compartir" (esquina superior derecha)
5. Pega el correo de la cuenta de servicio
6. Asigna permiso de "Editor"
7. Desmarca "Notificar"
8. Haz clic en "Compartir"

### 4. Configurar Variables de Entorno

En la raíz del proyecto, crea o edita el archivo `.env`:

```env
APP_NAME=Edupets
APP_ENV=development
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria
COOKIE_SECURE=false

GOOGLE_SHEET_ID=1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw
GOOGLE_SHEET_NAME=Hoja 1
GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
```

### 5. Estructura de Carpetas

Asegúrate de que la estructura sea:

```
Edupets/
├── app/
├── credentials/
│   └── service-account.json  ← Aquí va el archivo descargado
├── .env
├── requirements.txt
└── ...
```

### 6. Prueba de Conexión

Ejecuta el servidor:

```bash
fastapi dev app/main.py
```

Intenta crear una cuenta en http://127.0.0.1:8000/register

Si ves que funciona, ¡está todo configurado correctamente!

## Para Despliegue en Vercel

En lugar de usar `GOOGLE_SERVICE_ACCOUNT_FILE`, usa `GOOGLE_SERVICE_ACCOUNT_INFO`:

1. Abre el archivo JSON descargado
2. Copia TODO el contenido
3. En Vercel, crea una variable de entorno llamada `GOOGLE_SERVICE_ACCOUNT_INFO`
4. Pega el contenido JSON completo

**Nota**: Asegúrate de que el JSON esté formateado correctamente y en una sola línea.

## Validación de la Hoja

La hoja debe tener (o tendrá automáticamente) estos encabezados en la primera fila:

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| Usuario | Contraseña | Monedas | Felicidad | Comida | Sueño | Nombre | Progreso | Tareas |

La aplicación creará estos encabezados automáticamente si no existen.

## Solución de Problemas

### "Error en el servidor: Configura GOOGLE_SERVICE_ACCOUNT_FILE..."
- El archivo `.env` no tiene `GOOGLE_SERVICE_ACCOUNT_FILE` configurado
- El archivo `credentials/service-account.json` no existe
- Verifica las rutas

### "Error en el servidor: No tienes permisos..."
- La hoja no está compartida con la cuenta de servicio
- Repite el paso 3

### "Error en el servidor: spreadsheetId is required..."
- El `GOOGLE_SHEET_ID` en `.env` no es correcto
- Verifica que sea: `1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw`

### El servidor no inicia
- Asegúrate de tener todas las dependencias: `pip install -r requirements.txt`
- Verifica que Python 3.12+ esté instalado
