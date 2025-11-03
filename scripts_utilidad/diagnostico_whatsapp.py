#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico Completo - Integración WhatsApp + Documentos
Verifica toda la cadena: Upload → ETL → Storage → Firestore → WhatsApp
"""

import os
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GLOG_minloglevel'] = '3'

import sys
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
import json

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
print_header("INICIALIZANDO FIREBASE")
cred_path = 'cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json'

try:
    cred = credentials.Certificate(cred_path)
    try:
        app = firebase_admin.get_app()
        print_success("Usando app Firebase existente")
    except ValueError:
        app = firebase_admin.initialize_app(cred, {
            'storageBucket': 'admin-doc-ia.firebasestorage.app'
        })
        print_success("Firebase inicializado correctamente")
    
    db = firestore.client()
    bucket = storage.bucket()
    print_success(f"Firestore y Storage conectados")
    print_info(f"Bucket: {bucket.name}")
except Exception as e:
    print_error(f"Error inicializando Firebase: {e}")
    sys.exit(1)

# =====================================================================
# 1. VERIFICAR USUARIOS CON TELÉFONOS
# =====================================================================
print_header("1. VERIFICAR USUARIOS CON WHATSAPP VINCULADO")

usuarios_ref = db.collection('usuarios').stream()
usuarios_con_telefono = []
usuarios_sin_telefono = []

for user_doc in usuarios_ref:
    user_data = user_doc.to_dict()
    email = user_data.get('email', 'N/A')
    telefono = user_data.get('telefono', None)
    
    if telefono:
        usuarios_con_telefono.append({
            'uid': user_doc.id,
            'email': email,
            'telefono': telefono
        })
        print_success(f"Usuario: {email}")
        print_info(f"   UID: {user_doc.id}")
        print_info(f"   WhatsApp: {telefono}")
    else:
        usuarios_sin_telefono.append({
            'uid': user_doc.id,
            'email': email
        })

print(f"\n{Colors.BOLD}Resumen:{Colors.END}")
print_info(f"Usuarios con WhatsApp: {len(usuarios_con_telefono)}")
if usuarios_sin_telefono:
    print_warning(f"Usuarios sin WhatsApp: {len(usuarios_sin_telefono)}")
    for u in usuarios_sin_telefono:
        print(f"     - {u['email']}")

if not usuarios_con_telefono:
    print_error("No hay usuarios con WhatsApp vinculado")
    print_info("Solución: Vincula tu número en localhost:8000/perfil")
    sys.exit(1)

# =====================================================================
# 2. VERIFICAR DOCUMENTOS POR USUARIO
# =====================================================================
print_header("2. VERIFICAR DOCUMENTOS PROCESADOS POR USUARIO")

for usuario in usuarios_con_telefono:
    print(f"\n{Colors.BOLD}Usuario: {usuario['email']} ({usuario['telefono']}){Colors.END}")
    
    # Obtener documentos del usuario
    docs_ref = db.collection('documentos').where('usuarioId', '==', usuario['uid']).stream()
    
    total = 0
    procesados = 0
    pendientes = 0
    errores = 0
    documentos_procesados = []
    
    for doc in docs_ref:
        total += 1
        data = doc.to_dict()
        estado = data.get('estado', 'N/A')
        nombre = data.get('nombre', 'N/A')
        
        if estado == 'procesado':
            procesados += 1
            contenido_len = len(data.get('contenidoProcesado', ''))
            documentos_procesados.append({
                'id': doc.id,
                'nombre': nombre,
                'caracteres': contenido_len,
                'fecha': data.get('fechaProcesado', 'N/A')
            })
            print_success(f"{nombre}")
            print_info(f"   Estado: {estado}")
            print_info(f"   Caracteres: {contenido_len:,}")
            print_info(f"   Fecha procesado: {data.get('fechaProcesado', 'N/A')}")
        elif estado == 'pendiente':
            pendientes += 1
            print_warning(f"{nombre} - PENDIENTE de procesar")
        elif estado == 'error':
            errores += 1
            print_error(f"{nombre} - ERROR: {data.get('errorMensaje', 'N/A')}")
        else:
            print_warning(f"{nombre} - Estado desconocido: {estado}")
    
    print(f"\n{Colors.BOLD}Resumen documentos:{Colors.END}")
    print_info(f"Total: {total}")
    print_success(f"Procesados: {procesados}")
    if pendientes > 0:
        print_warning(f"Pendientes: {pendientes}")
    if errores > 0:
        print_error(f"Errores: {errores}")
    
    # Simular búsqueda del chatbot
    if procesados > 0:
        print(f"\n{Colors.BOLD}Simulación búsqueda WhatsApp:{Colors.END}")
        print_info(f"Teléfono: {usuario['telefono']}")
        print_info(f"UID encontrado: {usuario['uid']}")
        print_success(f"Documentos disponibles: {procesados}")
        
        # Mostrar preview del contenido
        for doc in documentos_procesados[:2]:  # Primeros 2 documentos
            contenido_sample = db.collection('documentos').document(doc['id']).get().to_dict().get('contenidoProcesado', '')[:200]
            print_info(f"\n   📄 {doc['nombre']}")
            print_info(f"   Preview: {contenido_sample}...")
    else:
        print_error("Este usuario NO tiene documentos procesados disponibles para WhatsApp")

# =====================================================================
# 3. VERIFICAR CONFIGURACIÓN DEL CHATBOT
# =====================================================================
print_header("3. VERIFICAR CONFIGURACIÓN CHATBOT")

# Verificar que intexta_chatbot.py existe
chatbot_path = 'intexta_chatbot.py'
if os.path.exists(chatbot_path):
    print_success(f"Archivo chatbot encontrado: {chatbot_path}")
    
    # Leer y verificar configuración
    with open(chatbot_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # Verificar imports críticos
        if 'from firebase_config import db' in content:
            print_success("Import de Firebase configurado")
        else:
            print_error("Falta import de firebase_config")
        
        # Verificar filtro de documentos procesados
        if "data.get('estado') == 'procesado'" in content:
            print_success("Filtro de documentos procesados OK")
        else:
            print_warning("El chatbot podría no estar filtrando documentos procesados")
        
        # Verificar búsqueda por teléfono
        if "usuarios_autenticados" in content:
            print_success("Sistema de autenticación por teléfono implementado")
        else:
            print_error("Falta autenticación por teléfono")
        
        # Verificar API DeepSeek
        if "DEEPSEEK_API_KEY" in content:
            print_success("API DeepSeek configurada")
        else:
            print_error("Falta configuración API DeepSeek")
else:
    print_error(f"No se encontró {chatbot_path}")

# =====================================================================
# 4. VERIFICAR FIREBASE CONFIG
# =====================================================================
print_header("4. VERIFICAR FIREBASE_CONFIG.PY")

firebase_config_path = 'cliente_web/firebase_config.py'
if os.path.exists(firebase_config_path):
    print_success(f"Archivo encontrado: {firebase_config_path}")
    
    with open(firebase_config_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        if 'firebase_admin' in content:
            print_success("firebase_admin importado")
        else:
            print_error("Falta import firebase_admin")
        
        if 'firestore.client()' in content:
            print_success("Cliente Firestore inicializado")
        else:
            print_error("Falta inicialización de Firestore")
else:
    print_error(f"No se encontró {firebase_config_path}")

# =====================================================================
# 5. TEST DE CONEXIÓN SIMULADA
# =====================================================================
print_header("5. TEST DE CONEXIÓN SIMULADA (WhatsApp → Firestore)")

if usuarios_con_telefono:
    test_user = usuarios_con_telefono[0]
    test_phone = test_user['telefono']
    
    print_info(f"Simulando mensaje de WhatsApp desde: {test_phone}")
    
    # Paso 1: Buscar usuario por teléfono
    print_info("Paso 1: Buscar usuario por teléfono...")
    users_ref = db.collection('usuarios').where('telefono', '==', test_phone).stream()
    users = list(users_ref)
    
    if users:
        found_uid = users[0].id
        print_success(f"Usuario encontrado: {found_uid}")
        
        # Paso 2: Obtener documentos
        print_info("Paso 2: Obtener documentos del usuario...")
        docs_ref = db.collection('documentos').where('usuarioId', '==', found_uid).stream()
        
        documentos_procesados = []
        for doc in docs_ref:
            data = doc.to_dict()
            if data.get('estado') == 'procesado' and data.get('contenidoProcesado'):
                documentos_procesados.append({
                    'nombre': data.get('nombre'),
                    'contenido': data.get('contenidoProcesado')[:500]  # Primeros 500 chars
                })
        
        if documentos_procesados:
            print_success(f"Se encontraron {len(documentos_procesados)} documentos procesados")
            print_info("\nContenido disponible para la IA:")
            for doc in documentos_procesados:
                print(f"\n   📄 {doc['nombre']}")
                print(f"   {doc['contenido'][:200]}...")
        else:
            print_error("No se encontraron documentos procesados")
            print_info("El chatbot responderá: 'No tienes documentos procesados disponibles'")
    else:
        print_error(f"No se encontró usuario con teléfono: {test_phone}")
        print_info("El chatbot responderá con mensaje de autenticación")

# =====================================================================
# 6. CHECKLIST DE PROBLEMAS COMUNES
# =====================================================================
print_header("6. CHECKLIST DE PROBLEMAS COMUNES")

issues = []

# Check 1: Usuarios sin teléfono
if usuarios_sin_telefono:
    issues.append(f"{len(usuarios_sin_telefono)} usuario(s) sin WhatsApp vinculado")

# Check 2: Documentos pendientes
all_docs = db.collection('documentos').stream()
pending_count = sum(1 for d in all_docs if d.to_dict().get('estado') == 'pendiente')
if pending_count > 0:
    issues.append(f"{pending_count} documento(s) pendiente(s) de procesar")

# Check 3: Documentos sin contenido procesado
all_docs = db.collection('documentos').stream()
no_content = 0
for doc in all_docs:
    data = doc.to_dict()
    if data.get('estado') == 'procesado' and not data.get('contenidoProcesado'):
        no_content += 1

if no_content > 0:
    issues.append(f"{no_content} documento(s) marcado como procesado pero sin contenido")

if issues:
    print_warning("Problemas detectados:")
    for issue in issues:
        print(f"   • {issue}")
else:
    print_success("No se detectaron problemas comunes")

# =====================================================================
# 7. GUÍA DE SOLUCIONES
# =====================================================================
print_header("7. GUÍA DE SOLUCIONES")

print(f"{Colors.BOLD}Si el chatbot no reconoce documentos:{Colors.END}\n")

print("1. Verificar que el usuario vinculó su WhatsApp:")
print("   → Ir a localhost:8000/perfil")
print("   → Ingresar número con código de país (ej: +56912345678)")
print("   → Guardar")

print("\n2. Verificar que los documentos están procesados:")
print("   → Ejecutar: python check_documents.py")
print("   → Si hay pendientes: python document_processor.py --mode process-pending")

print("\n3. Verificar que el chatbot está corriendo:")
print("   → Terminal 1: python intexta_chatbot.py")
print("   → Terminal 2: ngrok http 5000")
print("   → Configurar webhook en Twilio con URL de ngrok")

print("\n4. Verificar logs del chatbot:")
print("   → Revisar terminal donde corre intexta_chatbot.py")
print("   → Buscar mensajes como 'Usuario autenticado' o 'X documentos encontrados'")

print("\n5. Probar flujo completo:")
print("   → Enviar mensaje al número de Twilio desde WhatsApp")
print("   → Verificar que llegue al webhook (log en ngrok)")
print("   → Verificar respuesta del chatbot")

# =====================================================================
# RESUMEN FINAL
# =====================================================================
print_header("RESUMEN DEL DIAGNÓSTICO")

print(f"{Colors.BOLD}Estado del Sistema:{Colors.END}\n")
print(f"Usuarios registrados: {len(usuarios_con_telefono) + len(usuarios_sin_telefono)}")
print(f"Usuarios con WhatsApp: {len(usuarios_con_telefono)}")

total_docs = 0
total_procesados = 0
for usuario in usuarios_con_telefono:
    docs = db.collection('documentos').where('usuarioId', '==', usuario['uid']).stream()
    for doc in docs:
        total_docs += 1
        if doc.to_dict().get('estado') == 'procesado':
            total_procesados += 1

print(f"Total documentos: {total_docs}")
print(f"Documentos procesados: {total_procesados}")

if total_procesados > 0 and len(usuarios_con_telefono) > 0:
    print_success("\n✅ El sistema está configurado correctamente")
    print_info("Si el chatbot no responde, verifica que esté corriendo con ngrok")
else:
    print_error("\n❌ Configuración incompleta")
    if len(usuarios_con_telefono) == 0:
        print_info("→ Vincula tu WhatsApp en /perfil")
    if total_procesados == 0:
        print_info("→ Procesa documentos con: python document_processor.py --mode process-pending")

print(f"\n{Colors.BOLD}{'=' * 80}{Colors.END}\n")
