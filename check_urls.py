#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para verificar las URLs de documentos en Firestore"""

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
print("URLs DE DOCUMENTOS EN FIRESTORE")
print("=" * 80)

docs = db.collection('documentos').limit(5).stream()

for doc in docs:
    data = doc.to_dict()
    print(f"\n📄 {data.get('nombre', 'N/A')}")
    print(f"   URL completa: {data.get('url', 'N/A')}")
    print(f"   Estado: {data.get('estado', 'N/A')}")
