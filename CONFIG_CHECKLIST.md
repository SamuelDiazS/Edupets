# 📋 Checklist de Configuración - Edupets

Usa este checklist para asegurarte de que todo está configurado correctamente.

## 🔴 PASO CRÍTICO - Habilitar Google Sheets API

- [ ] Haz clic en: https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=731134327298
- [ ] Haz clic en "HABILITAR"
- [ ] Espera 1-2 minutos
- [ ] Recarga la página de tu aplicación

**⚠️ Este paso es OBLIGATORIO**

---

## 📁 Carpeta `credentials`

- [ ] Existe la carpeta `credentials/` en la raíz del proyecto
- [ ] El archivo `service-account.json` está en `credentials/service-account.json`
- [ ] El archivo contiene JSON válido (no está corrupto)

### Comando para Verificar:
```bash
# En Windows PowerShell
Test-Path ".\credentials\service-account.json"
```

Debería retornar: `True`

---

## 📝 Archivo `.env`

- [ ] Existe el archivo `.env` en la raíz del proyecto
- [ ] Contiene estas variables:
  ```env
  GOOGLE_SHEET_ID=1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw
  GOOGLE_SERVICE_ACCOUNT_FILE=./credentials/service-account.json
  ```

### Comando para Verificar:
```bash
# En Windows PowerShell
Get-Content .\.env | Select-String "GOOGLE"
```

Debería mostrar las dos líneas anteriores.

---

## 🔐 JSON de Credenciales

- [ ] El JSON contiene estos campos:
  - `"type": "service_account"`
  - `"project_id": "..."`
  - `"private_key_id": "..."`
  - `"private_key": "..."`
  - `"client_email": "..."`

### Comando para Verificar:
```bash
# En Windows PowerShell
$json = Get-Content .\credentials\service-account.json | ConvertFrom-Json
$json.client_email
```

Debería mostrar algo como: `edupets-service@tu-proyecto.iam.gserviceaccount.com`

---

## 📊 Google Sheet Compartida

- [ ] La Google Sheet está compartida con el email de la cuenta de servicio
- [ ] El email tiene permiso de "Editor"

### Cómo Verificar:
1. Ve a: https://docs.google.com/spreadsheets/d/1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw/edit
2. Haz clic en "Compartir" (esquina superior derecha)
3. Verifica que ves el email de la cuenta de servicio en la lista
4. Verifica que tiene permiso de "Editor"

---

## ✅ Prueba de Funcionamiento

1. Inicia el servidor:
   ```bash
   fastapi dev app/main.py
   ```

2. Ve a: http://127.0.0.1:8000/register

3. Intenta crear una cuenta con:
   - Usuario: `testuser`
   - Contraseña: `password123`

4. Verifica que:
   - ✅ No hay error (o el error es descriptivo)
   - ✅ Se redirige a `/pet` (página con mascota)
   - ✅ En Google Sheet aparece la nueva fila con el usuario

---

## 🔧 Script de Verificación

Corre este comando para verificar automáticamente:

```bash
python verify_config.py
```

Debería mostrar:
- ✅ Archivo .env existe
- ✅ GOOGLE_SHEET_ID configurado
- ✅ Archivo credentials encontrado
- ✅ JSON es válido
- ✅ client_email extraído correctamente

---

## 📱 Próximos Pasos

Una vez todo funcione:

1. ✅ Prueba login y logout
2. ✅ Prueba cambiar nombre de mascota
3. ✅ Prueba completar una actividad
4. ✅ Verifica que los datos se guardan en Google Sheet
5. ✅ (Opcional) Despliega en Vercel

---

## ❓ ¿Aún Hay Problemas?

1. Lee **ERROR_SOLUTION.md** para diagnóstico completo
2. Revisa **GOOGLE_SHEETS_SETUP.md** paso a paso
3. Ejecuta `python verify_config.py` para ver qué falta
