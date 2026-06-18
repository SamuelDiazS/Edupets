# 🔧 Solución: Error "Internal Server Error" al Crear Cuenta

## Diagnóstico

El error `Internal Server Error` ocurre porque **las credenciales de Google Sheets no están configuradas correctamente** en el proyecto.

### Causas Posibles:

1. ❌ No existe el archivo `.env`
2. ❌ No existe el archivo `credentials/service-account.json`
3. ❌ Las variables `GOOGLE_SERVICE_ACCOUNT_FILE` o `GOOGLE_SERVICE_ACCOUNT_INFO` no están configuradas
4. ❌ La hoja de Google Sheets no está compartida con la cuenta de servicio
5. ❌ Las credenciales son inválidas o han expirado

## Cambios Realizados

### 1. ✅ Mejora en el Manejo de Errores
- **app/routers/auth.py**: Ahora captura cualquier excepción no esperada y muestra un mensaje de error descriptivo
- Los errores se muestran en la página de registro/login en lugar de retornar un "Internal Server Error" genérico

### 2. ✅ Archivo de Instrucciones
- **GOOGLE_SHEETS_SETUP.md**: Guía completa paso a paso para configurar Google Sheets

### 3. ✅ Script de Verificación
- **verify_config.py**: Script que verifica automáticamente la configuración

## Pasos para Solucionar el Problema

### Opción A: Verificación Rápida (Recomendado)

```bash
# En la raíz del proyecto
python verify_config.py
```

El script te dirá exactamente qué está faltando.

### Opción B: Configuración Manual

Sigue los pasos en **GOOGLE_SHEETS_SETUP.md**:

1. Crea una Cuenta de Servicio en Google Cloud Console
2. Descarga el archivo JSON
3. Guárdalo en `credentials/service-account.json`
4. Comparte la hoja de Google Sheets con el email de la cuenta de servicio
5. Configura el archivo `.env` con:
   ```env
   GOOGLE_SHEET_ID=1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw
   GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
   ```

### Opción C: Si Usas Vercel (Despliegue)

En lugar de usar un archivo, usa una variable de entorno:

```env
GOOGLE_SERVICE_ACCOUNT_INFO={"type":"service_account","project_id":"..."}
```

(Pega el contenido completo del JSON)

## Cómo Saber si Está Funcionando

1. Inicia el servidor: `fastapi dev app/main.py`
2. Ve a http://127.0.0.1:8000
3. Haz clic en "Registrarse"
4. Intenta crear una cuenta con:
   - Usuario: `testuser`
   - Contraseña: `password123`

### ✅ Si funciona:
- Se redirige a `/pet` automáticamente
- Ves la página con tu mascota

### ❌ Si no funciona:
- Ves un mensaje de error descriptivo
- Sigue los pasos de solución

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `app/routers/auth.py` | +30 líneas: Mejor manejo de errores en login y registro |
| `GOOGLE_SHEETS_SETUP.md` | ✨ NUEVO: Guía completa de configuración |
| `verify_config.py` | ✨ NUEVO: Script de verificación automática |

## Resumen

El proyecto está **funcionalmente completo**, solo necesita que configures las credenciales de Google Sheets. 

Una vez que lo hagas, la aplicación:
- ✅ Registrará usuarios en Google Sheets
- ✅ Autenticará el login
- ✅ Guardará la mascota y sus estadísticas
- ✅ Permitirá completar actividades
- ✅ Funcionará en Vercel

**¡Sigue el archivo GOOGLE_SHEETS_SETUP.md para completar la configuración!**
