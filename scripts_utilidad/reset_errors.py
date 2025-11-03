#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para restablecer documentos con error a pendiente"""

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

print("=" * 60)
print("RESTABLECER DOCUMENTOS CON ERROR A PENDIENTE")
print("=" * 60)

# Obtener documentos con error
from google.cloud.firestore_v1.base_query import FieldFilter

docs = db.collection('documentos').where(
    filter=FieldFilter('estado', '==', 'error')
).stream()

reset_count = 0

for doc in docs:
    data = doc.to_dict()
    print(f"\n🔄 Restableciendo: {data.get('nombre', 'N/A')}")
    
    # Actualizar a pendiente y limpiar campos de error
    update_data = {
        'estado': 'pendiente'
    }
    
    # Eliminar campos de error si existen
    if 'errorMensaje' in data:
        update_data['errorMensaje'] = firestore.DELETE_FIELD
    if 'fechaError' in data:
        update_data['fechaError'] = firestore.DELETE_FIELD
    
    db.collection('documentos').document(doc.id).update(update_data)
    reset_count += 1
    print(f"   ✅ Estado cambiado a: pendiente")

print("\n" + "=" * 60)
print(f"Documentos restablecidos: {reset_count}")
print("=" * 60)

if reset_count > 0:
    print("\n✅ Documentos listos para ser procesados nuevamente.")
