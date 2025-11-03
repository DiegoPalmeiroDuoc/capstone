#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para sincronizar usuarios de Firebase Authentication con Firestore
Crea documentos en la colección 'usuarios' para todos los usuarios registrados
"""

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'

import firebase_admin
from firebase_admin import credentials, auth, firestore
from datetime import datetime

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"ℹ️  {text}")

# Inicializar Firebase
print_header("SINCRONIZAR USUARIOS: AUTHENTICATION → FIRESTORE")

cred_path = 'cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json'

try:
    cred = credentials.Certificate(cred_path)
    try:
        app = firebase_admin.get_app()
        print_success("Usando app Firebase existente")
    except ValueError:
        app = firebase_admin.initialize_app(cred)
        print_success("Firebase inicializado correctamente")
    
    db = firestore.client()
    print_success("Firestore conectado")
except Exception as e:
    print_error(f"Error inicializando Firebase: {e}")
    exit(1)

print_info("Obteniendo usuarios de Firebase Authentication...")

# Listar todos los usuarios de Authentication
page = auth.list_users()
users_count = 0
created_count = 0
updated_count = 0
skipped_count = 0

print("\n" + "=" * 80)
print("USUARIOS EN FIREBASE AUTHENTICATION")
print("=" * 80)

while page:
    for user in page.users:
        users_count += 1
        print(f"\n📧 Usuario {users_count}: {user.email}")
        print(f"   UID: {user.uid}")
        print(f"   Email verificado: {user.email_verified}")
        print(f"   Creado: {datetime.fromtimestamp(user.user_metadata.creation_timestamp / 1000)}")
        
        # Verificar si existe en Firestore
        user_ref = db.collection('usuarios').document(user.uid)
        user_doc = user_ref.get()
        
        if user_doc.exists:
            print_warning("Ya existe en Firestore - Actualizando datos...")
            
            # Actualizar solo campos que puedan haber cambiado
            update_data = {
                'email': user.email,
                'emailVerificado': user.email_verified,
                'fechaActualizacion': datetime.now().isoformat()
            }
            
            user_ref.update(update_data)
            updated_count += 1
            print_success("Actualizado")
            
        else:
            print_info("No existe en Firestore - Creando documento...")
            
            # Crear nuevo documento
            new_user_data = {
                'uid': user.uid,
                'email': user.email,
                'emailVerificado': user.email_verified,
                'rol': 'cliente',
                'fechaRegistro': datetime.fromtimestamp(user.user_metadata.creation_timestamp / 1000).isoformat(),
                'fechaCreacionFirestore': datetime.now().isoformat()
            }
            
            # Si el usuario tiene display name, agregarlo
            if user.display_name:
                new_user_data['nombre'] = user.display_name
            
            # Si el usuario tiene teléfono, agregarlo
            if user.phone_number:
                new_user_data['telefono'] = user.phone_number
            
            user_ref.set(new_user_data)
            created_count += 1
            print_success("Creado en Firestore")
    
    # Obtener siguiente página
    page = page.get_next_page()

print("\n" + "=" * 80)
print("RESUMEN DE SINCRONIZACIÓN")
print("=" * 80)

print(f"\n{Colors.BOLD}Usuarios en Authentication:{Colors.END} {users_count}")
print_success(f"Creados en Firestore: {created_count}")
print_warning(f"Actualizados: {updated_count}")
print_info(f"Ya existían: {skipped_count}")

# Verificar la colección usuarios
print("\n" + "=" * 80)
print("VERIFICACIÓN: USUARIOS EN FIRESTORE")
print("=" * 80)

usuarios_firestore = db.collection('usuarios').stream()
firestore_count = 0

for user_doc in usuarios_firestore:
    firestore_count += 1
    data = user_doc.to_dict()
    print(f"\n✅ {data.get('email', 'N/A')}")
    print(f"   UID: {user_doc.id}")
    print(f"   Rol: {data.get('rol', 'N/A')}")
    print(f"   WhatsApp: {data.get('telefono', 'Sin WhatsApp')}")
    
    # Contar documentos del usuario
    docs_count = len(list(db.collection('documentos').where('usuarioId', '==', user_doc.id).stream()))
    print(f"   Documentos: {docs_count}")

print(f"\n{Colors.BOLD}Total en Firestore:{Colors.END} {firestore_count}")

if users_count == firestore_count:
    print_success("\n✅ SINCRONIZACIÓN COMPLETA: Todos los usuarios están en Firestore")
else:
    print_warning(f"\n⚠️  Diferencia: {users_count - firestore_count} usuarios faltantes")

# Verificar documentos huérfanos (sin usuario)
print("\n" + "=" * 80)
print("VERIFICACIÓN: DOCUMENTOS SIN USUARIO")
print("=" * 80)

all_users = {user.uid for user in auth.list_users().users}
orphan_docs = []

for doc in db.collection('documentos').stream():
    data = doc.to_dict()
    usuario_id = data.get('usuarioId')
    
    if usuario_id not in all_users:
        orphan_docs.append({
            'id': doc.id,
            'nombre': data.get('nombre', 'N/A'),
            'usuarioId': usuario_id
        })

if orphan_docs:
    print_warning(f"Se encontraron {len(orphan_docs)} documentos huérfanos:")
    for doc in orphan_docs:
        print(f"\n⚠️  {doc['nombre']}")
        print(f"   ID: {doc['id']}")
        print(f"   Usuario ID (no existe): {doc['usuarioId']}")
else:
    print_success("No hay documentos huérfanos")

print("\n" + "=" * 80)
print("SINCRONIZACIÓN FINALIZADA")
print("=" * 80)

print(f"\n{Colors.BOLD}Próximos pasos:{Colors.END}")
print("1. Verifica que los usuarios puedan acceder a sus documentos")
print("2. Los nuevos registros crearán automáticamente su documento en Firestore")
print("3. Si hay documentos huérfanos, considera reasignarlos o eliminarlos")

print(f"\n{Colors.GREEN}✅ Script completado exitosamente{Colors.END}\n")
