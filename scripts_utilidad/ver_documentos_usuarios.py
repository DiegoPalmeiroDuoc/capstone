#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para ver todos los documentos y sus usuarios asociados"""

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'

import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase
cred_path = 'cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json'
cred = credentials.Certificate(cred_path)

try:
    app = firebase_admin.get_app()
except ValueError:
    app = firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 80)
print("TODOS LOS DOCUMENTOS Y SUS USUARIOS")
print("=" * 80)

# Obtener todos los usuarios para referencia
usuarios = {}
for user_doc in db.collection('usuarios').stream():
    user_data = user_doc.to_dict()
    usuarios[user_doc.id] = {
        'email': user_data.get('email', 'N/A'),
        'telefono': user_data.get('telefono', 'Sin WhatsApp')
    }

print(f"\n📋 USUARIOS REGISTRADOS ({len(usuarios)}):")
for uid, info in usuarios.items():
    print(f"  • {info['email']}")
    print(f"    UID: {uid}")
    print(f"    WhatsApp: {info['telefono']}\n")

print("=" * 80)
print("📄 DOCUMENTOS EN FIRESTORE:")
print("=" * 80)

docs = db.collection('documentos').stream()
doc_count = 0

for doc in docs:
    doc_count += 1
    data = doc.to_dict()
    usuario_id = data.get('usuarioId', 'N/A')
    
    # Buscar info del usuario
    if usuario_id in usuarios:
        usuario_info = usuarios[usuario_id]
        usuario_email = usuario_info['email']
        usuario_telefono = usuario_info['telefono']
    else:
        usuario_email = "USUARIO NO ENCONTRADO"
        usuario_telefono = "N/A"
    
    print(f"\n📄 Documento: {data.get('nombre', 'N/A')}")
    print(f"   ID: {doc.id}")
    print(f"   Estado: {data.get('estado', 'N/A')}")
    print(f"   Usuario ID: {usuario_id}")
    print(f"   Usuario Email: {usuario_email}")
    print(f"   Usuario WhatsApp: {usuario_telefono}")
    
    if data.get('estado') == 'procesado':
        print(f"   Caracteres procesados: {len(data.get('contenidoProcesado', ''))}")
    elif data.get('estado') == 'error':
        print(f"   Error: {data.get('errorMensaje', 'N/A')}")

print("\n" + "=" * 80)
print(f"Total de documentos: {doc_count}")
print("=" * 80)

# Análisis de vinculación
print("\n📊 ANÁLISIS DE VINCULACIÓN:")
for uid, info in usuarios.items():
    docs_usuario = db.collection('documentos').where('usuarioId', '==', uid).stream()
    count = sum(1 for _ in docs_usuario)
    
    if info['telefono'] != 'Sin WhatsApp':
        if count > 0:
            print(f"✅ {info['email']} - WhatsApp: {info['telefono']} - Documentos: {count}")
        else:
            print(f"⚠️  {info['email']} - WhatsApp: {info['telefono']} - ❌ SIN DOCUMENTOS")
    else:
        if count > 0:
            print(f"⚠️  {info['email']} - ❌ Sin WhatsApp - Documentos: {count} (NO ACCESIBLES VÍA CHATBOT)")
        else:
            print(f"   {info['email']} - Sin WhatsApp - Sin documentos")

print("\n" + "=" * 80)
