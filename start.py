#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de inicio rápido para Intexta
Verifica configuración y arranca todos los servicios
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_file(filepath, description):
    """Verifica si un archivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NO ENCONTRADO: {filepath}")
        return False

def check_python_version():
    """Verifica versión de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (Se requiere 3.9+)")
        return False

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    required = [
        'django',
        'firebase_admin',
        'flask',
        'twilio',
        'requests',
        'pdfplumber',
        'pandas'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} NO INSTALADO")
            missing.append(package)
    
    return len(missing) == 0

def main():
    print_header("INTEXTA - Verificación de Configuración")
    
    # Verificar Python
    print("🐍 Verificando Python...")
    if not check_python_version():
        print("\n⚠️  Actualiza Python a la versión 3.9 o superior")
        sys.exit(1)
    
    # Verificar archivos importantes
    print("\n📁 Verificando archivos...")
    files_ok = True
    
    files_ok &= check_file("requirements.txt", "Dependencias")
    files_ok &= check_file("etl.py", "ETL")
    files_ok &= check_file("document_processor.py", "Procesador")
    files_ok &= check_file("intexta_chatbot.py", "Chatbot")
    files_ok &= check_file("cliente_web/manage.py", "Django manage.py")
    files_ok &= check_file(
        "cliente_web/admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json",
        "Credenciales Firebase"
    )
    
    if not files_ok:
        print("\n⚠️  Algunos archivos están faltando")
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    if not check_dependencies():
        print("\n⚠️  Instala las dependencias con: pip install -r requirements.txt")
        response = input("\n¿Deseas instalar ahora? (s/n): ")
        if response.lower() == 's':
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        else:
            sys.exit(1)
    
    # Menú de opciones
    print_header("¿Qué deseas iniciar?")
    print("1. Aplicación Web Django")
    print("2. Procesador de Documentos (modo escucha)")
    print("3. Chatbot de WhatsApp")
    print("4. Procesar documentos pendientes (una vez)")
    print("5. Iniciar TODO (Web + Procesador + Chatbot)")
    print("6. Verificar estado de Firebase")
    print("0. Salir")
    
    choice = input("\nSelecciona una opción (0-6): ")
    
    if choice == "1":
        print_header("Iniciando Aplicación Web Django")
        os.chdir("cliente_web")
        subprocess.run([sys.executable, "manage.py", "runserver"])
    
    elif choice == "2":
        print_header("Iniciando Procesador de Documentos")
        subprocess.run([sys.executable, "document_processor.py", "--mode", "listen"])
    
    elif choice == "3":
        print_header("Iniciando Chatbot de WhatsApp")
        subprocess.run([sys.executable, "intexta_chatbot.py"])
    
    elif choice == "4":
        print_header("Procesando Documentos Pendientes")
        subprocess.run([sys.executable, "document_processor.py", "--mode", "process-pending"])
    
    elif choice == "5":
        print_header("Iniciando TODOS los servicios")
        print("\n⚠️  NOTA: Se abrirán 3 terminales separadas")
        print("Presiona Ctrl+C en cada una para detenerlas\n")
        
        # En Windows, usar 'start' para abrir nuevas ventanas
        if sys.platform == "win32":
            subprocess.Popen(["start", "cmd", "/k", f"{sys.executable} cliente_web/manage.py runserver"], shell=True)
            time.sleep(2)
            subprocess.Popen(["start", "cmd", "/k", f"{sys.executable} document_processor.py --mode listen"], shell=True)
            time.sleep(2)
            subprocess.Popen(["start", "cmd", "/k", f"{sys.executable} intexta_chatbot.py"], shell=True)
        else:
            # Para Linux/Mac, usar gnome-terminal o xterm
            subprocess.Popen(["gnome-terminal", "--", sys.executable, "cliente_web/manage.py", "runserver"])
            subprocess.Popen(["gnome-terminal", "--", sys.executable, "document_processor.py", "--mode", "listen"])
            subprocess.Popen(["gnome-terminal", "--", sys.executable, "intexta_chatbot.py"])
        
        print("✅ Servicios iniciados en ventanas separadas")
    
    elif choice == "6":
        print_header("Verificando Firebase")
        try:
            sys.path.insert(0, 'cliente_web')
            from firebase_config import db, bucket
            
            print("✅ Conexión a Firestore establecida")
            print("✅ Conexión a Storage establecida")
            
            # Contar documentos
            docs_ref = db.collection('documentos')
            docs_count = len(list(docs_ref.limit(100).stream()))
            print(f"\n📄 Documentos en Firestore: {docs_count}")
            
        except Exception as e:
            print(f"❌ Error conectando a Firebase: {e}")
    
    elif choice == "0":
        print("\n👋 ¡Hasta luego!")
        sys.exit(0)
    
    else:
        print("\n❌ Opción inválida")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Detenido por el usuario")
        sys.exit(0)
