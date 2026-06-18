# 🔧 Solución: Error "Internal Server Error" al Crear Cuenta

## 🚨 El Error Específico Que Ves

```
Error en el servidor: <HttpError 403 when requesting https://sheets.googleapis.com/v4/spreadsheets/...
Google Sheets API has not been used in project 731134327298 before or it is disabled.
Enable it by visiting https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=731134327298
```

## ✅ Solución Inmediata (2 minutos)

### Paso 1: Habilitar Google Sheets API

**Tu proyecto 731134327298 tiene la API deshabilitada. Necesitas habilitarla:**

1. **Abre este enlace** (copia y pega en tu navegador):
   ```
   https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=731134327298
   ```

2. **Haz clic en el botón azul "HABILITAR"** en la parte superior

3. **Espera 1-2 minutos** a que Google propague el cambio

4. **Vuelve a tu aplicación** e intenta registrarte de nuevo

### Paso 2: Si Aún No Funciona

Si sigue sin funcionar después de 2 minutos:

1. Actualiza la página de tu aplicación con `F5`
2. Intenta registrarte de nuevo
3. Si aún no funciona, limpia el navegador (cookies, caché):
   - En Chrome: `Ctrl + Shift + Delete`
   - En Firefox: `Ctrl + Shift + Delete`
   - En Edge: `Ctrl + Shift + Delete`

## 📋 Resumen de Toda la Configuración

Si esto no funciona, sigue **GOOGLE_SHEETS_SETUP.md** paso por paso:

1. ✅ **Habilitar Google Sheets API** (ES LO QUE ACABAS DE HACER)
2. Crear una Cuenta de Servicio en Google Cloud
3. Descargar la Clave JSON
4. Compartir la Hoja de Google Sheets
5. Configurar variables de entorno
6. Prueba de conexión
