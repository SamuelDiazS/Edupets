#!/usr/bin/env python
"""
Script de verificación para Edupets.
Comprueba si las credenciales de Google Sheets están correctamente configuradas.
"""

import json
import sys
from pathlib import Path

def check_environment():
    """Verifica si las variables de entorno están configuradas."""
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN - EDUPETS")
    print("=" * 60)
    print()
    
    # Verificar .env
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ No se encontró archivo .env")
        print("   → Crea un archivo .env basado en .env.example")
        return False
    
    print("✅ Archivo .env encontrado")
    
    # Leer .env
    env_vars = {}
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    
    # Verificar GOOGLE_SHEET_ID
    google_sheet_id = env_vars.get("GOOGLE_SHEET_ID", "").strip()
    if not google_sheet_id:
        print("❌ GOOGLE_SHEET_ID no está configurado en .env")
        return False
    
    if google_sheet_id == "1PLOtpKWiyxJLtEjQjkxQZYVtydn00eSwmpliR8aXPVw":
        print(f"✅ GOOGLE_SHEET_ID: {google_sheet_id[:20]}...")
    else:
        print(f"⚠️  GOOGLE_SHEET_ID: {google_sheet_id[:20]}...")
        print(f"   → El ID no coincide con el predeterminado")
    
    # Verificar credenciales
    service_account_file = env_vars.get("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
    service_account_info = env_vars.get("GOOGLE_SERVICE_ACCOUNT_INFO", "").strip()
    
    if not service_account_file and not service_account_info:
        print("❌ No hay credenciales de Google Sheets configuradas")
        print("   → Establece GOOGLE_SERVICE_ACCOUNT_FILE o GOOGLE_SERVICE_ACCOUNT_INFO")
        print("   → Ve a GOOGLE_SHEETS_SETUP.md para instrucciones")
        return False
    
    # Verificar archivo de credenciales
    if service_account_file:
        creds_path = Path(service_account_file)
        if not creds_path.exists():
            print(f"❌ Archivo de credenciales no encontrado: {service_account_file}")
            print("   → Descarga el archivo JSON de Google Cloud Console")
            print("   → Guárdalo en: {service_account_file}")
            return False
        
        print(f"✅ Archivo de credenciales: {service_account_file}")
        
        # Verificar que sea JSON válido
        try:
            with open(creds_path) as f:
                creds = json.load(f)
            
            if "client_email" in creds:
                print(f"   → Email de servicio: {creds['client_email'][:30]}...")
            else:
                print("❌ El archivo JSON no tiene 'client_email'")
                return False
            
        except json.JSONDecodeError:
            print("❌ El archivo de credenciales no es JSON válido")
            return False
    
    elif service_account_info:
        print("✅ GOOGLE_SERVICE_ACCOUNT_INFO configurado (para Vercel)")
        try:
            creds = json.loads(service_account_info)
            if "client_email" in creds:
                print(f"   → Email de servicio: {creds['client_email'][:30]}...")
        except json.JSONDecodeError:
            print("❌ GOOGLE_SERVICE_ACCOUNT_INFO no es JSON válido")
            return False
    
    print()
    print("=" * 60)
    print("✅ CONFIGURACIÓN VERIFICADA CORRECTAMENTE")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("1. Asegúrate de que la hoja de Google Sheets está compartida")
    print("   con el email de servicio")
    print("2. Inicia el servidor: fastapi dev app/main.py")
    print("3. Intenta crear una cuenta en: http://127.0.0.1:8000/register")
    print()
    
    return True

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1)
