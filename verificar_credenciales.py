#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar que las credenciales estén configuradas correctamente
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 60)
print("🔍 VERIFICACIÓN DE CREDENCIALES")
print("=" * 60)

# Verificar DeepSeek API
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
if deepseek_key:
    print(f"✅ DEEPSEEK_API_KEY: {deepseek_key[:15]}...{deepseek_key[-10:]}")
else:
    print("❌ DEEPSEEK_API_KEY: NO CONFIGURADA")

# Verificar Twilio
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

if twilio_sid and twilio_sid != "TU_ACCOUNT_SID_AQUI":
    print(f"✅ TWILIO_ACCOUNT_SID: {twilio_sid[:10]}...{twilio_sid[-5:]}")
else:
    print("⚠️  TWILIO_ACCOUNT_SID: Usando valor de ejemplo (configurar para producción)")

if twilio_token and twilio_token != "TU_AUTH_TOKEN_AQUI":
    print(f"✅ TWILIO_AUTH_TOKEN: {twilio_token[:10]}...{twilio_token[-5:]}")
else:
    print("⚠️  TWILIO_AUTH_TOKEN: Usando valor de ejemplo (configurar para producción)")

if twilio_number:
    print(f"✅ TWILIO_WHATSAPP_NUMBER: {twilio_number}")
else:
    print("❌ TWILIO_WHATSAPP_NUMBER: NO CONFIGURADA")

# Verificar Django
django_secret = os.getenv("DJANGO_SECRET_KEY")
if django_secret and django_secret != "django-insecure-tu-secret-key-muy-segura-aqui":
    print(f"✅ DJANGO_SECRET_KEY: Configurada")
else:
    print("⚠️  DJANGO_SECRET_KEY: Usando valor de ejemplo")

debug = os.getenv("DEBUG")
print(f"{'✅' if debug else '⚠️ '} DEBUG: {debug}")

allowed_hosts = os.getenv("ALLOWED_HOSTS")
print(f"{'✅' if allowed_hosts else '⚠️ '} ALLOWED_HOSTS: {allowed_hosts}")

# Verificar Firebase
firebase_project = os.getenv("FIREBASE_PROJECT_ID")
if firebase_project:
    print(f"✅ FIREBASE_PROJECT_ID: {firebase_project}")
else:
    print("❌ FIREBASE_PROJECT_ID: NO CONFIGURADA")

print("=" * 60)
print("\n📋 Resumen:")
print("=" * 60)

# Contar credenciales configuradas
configured = 0
total = 0

# Esenciales
essential = {
    "DEEPSEEK_API_KEY": deepseek_key,
    "FIREBASE_PROJECT_ID": firebase_project
}

for key, value in essential.items():
    total += 1
    if value and value not in ["TU_ACCOUNT_SID_AQUI", "TU_AUTH_TOKEN_AQUI", "django-insecure-tu-secret-key-muy-segura-aqui"]:
        configured += 1
        print(f"✅ {key}")
    else:
        print(f"❌ {key}")

# Opcionales
optional = {
    "TWILIO_ACCOUNT_SID": twilio_sid,
    "TWILIO_AUTH_TOKEN": twilio_token
}

print("\nOpcionales (para WhatsApp en producción):")
for key, value in optional.items():
    if value and value not in ["TU_ACCOUNT_SID_AQUI", "TU_AUTH_TOKEN_AQUI"]:
        print(f"✅ {key}")
    else:
        print(f"⚠️  {key} (sandbox ok)")

print("=" * 60)
if configured == total:
    print("🎉 ¡Todas las credenciales esenciales están configuradas!")
else:
    print(f"⚠️  {configured}/{total} credenciales esenciales configuradas")
print("=" * 60)
