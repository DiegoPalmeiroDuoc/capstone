#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para agregar campo 'estado' a documentos existentes sin este campo"""

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Inicializar Firebase
cred_path = 'cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json'
cred = credentials.Certificate(cred_path)

try:
    app = firebase_admin.get_app()
except ValueError:
    app = firebase_admin.initialize_app(cred)

db = firestore.client()

print("=" * 60)
print("MIGRACIÓN: Agregar campo 'estado' a documentos")
print("=" * 60)

# Obtener todos los documentos
docs = db.collection('documentos').stream()
updated_count = 0
skipped_count = 0

for doc in docs:
    data = doc.to_dict()
    
    # Verificar si el documento ya tiene el campo 'estado'
    if 'estado' not in data or data.get('estado') is None:
        print(f"\n📝 Actualizando: {data.get('nombre', 'N/A')}")
        
        # Actualizar el documento con estado 'pendiente'
        db.collection('documentos').document(doc.id).update({
            'estado': 'pendiente'
        })
        
        updated_count += 1
        print(f"   ✅ Estado agregado: pendiente")
    else:
        print(f"⏭️  Saltando: {data.get('nombre', 'N/A')} (ya tiene estado: {data.get('estado')})")
        skipped_count += 1

print("\n" + "=" * 60)
print(f"RESULTADOS:")
print(f"  Documentos actualizados: {updated_count}")
print(f"  Documentos sin cambios: {skipped_count}")
print("=" * 60)

if updated_count > 0:
    print("\n✅ Migración completada. Los documentos ahora están listos para ser procesados.")
    print("💡 Ejecuta 'python document_processor.py' para procesarlos.")
else:
    print("\n✅ No se requirieron cambios. Todos los documentos ya tienen el campo 'estado'.")
