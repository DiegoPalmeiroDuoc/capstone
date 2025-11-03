#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para transferir documentos entre usuarios
Útil cuando un usuario tiene WhatsApp pero sus documentos están en otra cuenta
"""

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'

import firebase_admin
from firebase_admin import credentials, firestore
import sys

# Inicializar Firebase
cred_path = 'cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json'
cred = credentials.Certificate(cred_path)

try:
    app = firebase_admin.get_app()
except ValueError:
    app = firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 80)
print("TRANSFERIR DOCUMENTOS ENTRE USUARIOS")
print("=" * 80)

# Mostrar usuarios
print("\n📋 USUARIOS DISPONIBLES:")
usuarios = {}
for user_doc in db.collection('usuarios').stream():
    user_data = user_doc.to_dict()
    usuarios[user_doc.id] = {
        'email': user_data.get('email', 'N/A'),
        'telefono': user_data.get('telefono', 'Sin WhatsApp')
    }
    print(f"{user_doc.id}: {user_data.get('email')} - WhatsApp: {user_data.get('telefono', 'Sin WhatsApp')}")

# Caso común: Transferir de gionara.espinosa@gmail.com a gi.espinosa@duocuc.cl
origen_uid = "BODa19voUWT8DxvflAOErlhr3ro2"  # gionara.espinosa@gmail.com
destino_uid = "NlsLIaYnDRXReBE23i2zVcYmikB2"  # gi.espinosa@duocuc.cl

print(f"\n🔄 TRANSFERENCIA AUTOMÁTICA:")
print(f"Desde: {usuarios.get(origen_uid, {}).get('email', 'N/A')} (sin WhatsApp)")
print(f"Hacia: {usuarios.get(destino_uid, {}).get('email', 'N/A')} (con WhatsApp: +56930104972)")

input("\n⚠️  Presiona ENTER para continuar o Ctrl+C para cancelar...")

# Obtener documentos del usuario origen
docs_ref = db.collection('documentos').where('usuarioId', '==', origen_uid).stream()
transferidos = 0

for doc in docs_ref:
    data = doc.to_dict()
    nombre = data.get('nombre', 'N/A')
    
    print(f"\n📄 Transfiriendo: {nombre}")
    
    # Actualizar el usuarioId
    db.collection('documentos').document(doc.id).update({
        'usuarioId': destino_uid
    })
    
    transferidos += 1
    print(f"   ✅ Documento ahora pertenece a {usuarios[destino_uid]['email']}")

print(f"\n{'=' * 80}")
print(f"Total de documentos transferidos: {transferidos}")
print("=" * 80)

if transferidos > 0:
    print("\n✅ Transferencia completada!")
    print(f"El usuario {usuarios[destino_uid]['email']} ahora tiene {transferidos} documento(s)")
    print(f"Puede acceder a ellos vía WhatsApp: {usuarios[destino_uid]['telefono']}")
    
    print("\n🔍 Verificación:")
    docs_nuevos = db.collection('documentos').where('usuarioId', '==', destino_uid).stream()
    for doc in docs_nuevos:
        data = doc.to_dict()
        print(f"  • {data.get('nombre')} - Estado: {data.get('estado')}")
else:
    print("\n⚠️  No se encontraron documentos para transferir")
