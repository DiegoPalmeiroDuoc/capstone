#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para verificar el estado de los documentos en Firestore"""

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

# Obtener documentos
print("=" * 60)
print("ESTADO DE DOCUMENTOS EN FIRESTORE")
print("=" * 60)

docs = db.collection('documentos').limit(10).stream()
doc_count = 0

for doc in docs:
    doc_count += 1
    data = doc.to_dict()
    print(f"\n📄 Documento {doc_count}: {doc.id}")
    print(f"   Nombre: {data.get('nombre', 'N/A')}")
    print(f"   Estado: {data.get('estado', 'N/A')}")
    print(f"   Usuario: {data.get('usuarioId', 'N/A')}")
    print(f"   Fecha subida: {data.get('fechaSubida', 'N/A')}")
    if data.get('estado') == 'procesado':
        print(f"   Caracteres: {data.get('caracteresTotales', 0)}")
    if data.get('estado') == 'error':
        print(f"   Error: {data.get('errorMensaje', 'N/A')}")

if doc_count == 0:
    print("\n⚠️  No se encontraron documentos en Firestore")
else:
    print(f"\n{'=' * 60}")
    print(f"Total de documentos: {doc_count}")
    print("=" * 60)

# Contar por estado
from google.cloud.firestore_v1.base_query import FieldFilter

estados = ['pendiente', 'procesando', 'procesado', 'error']
print("\nRESUMEN POR ESTADO:")
for estado in estados:
    count = len(list(db.collection('documentos').where(
        filter=FieldFilter('estado', '==', estado)
    ).stream()))
    print(f"  {estado.upper()}: {count}")
