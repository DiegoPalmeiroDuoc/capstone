#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Document Processor - Procesador Automático de Documentos
Escucha Firestore, detecta nuevos documentos y los procesa automáticamente.

Flujo:
1. Detecta documento con estado "pendiente" en Firestore
2. Descarga el archivo de Firebase Storage
3. Procesa con ETL para extraer texto
4. Guarda contenido procesado en Firestore
5. Actualiza estado a "procesado"
"""

# ===== IMPORTANTE: Configurar antes de cualquier import =====
import os
import sys

# Suprimir warnings de gRPC/ALTS ANTES de importar cualquier cosa
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''
os.environ['GRPC_VERBOSITY'] = 'NONE'
os.environ['GLOG_minloglevel'] = '3'

import logging
import tempfile
import time
import warnings
from datetime import datetime
from pathlib import Path

# Suprimir warnings adicionales
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*ALTS.*')

# Importar ETL
from etl import choose_extractor, normalize_text

# Configuración de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class DocumentProcessor:
    """Procesador automático de documentos de Firebase"""
    
    def __init__(self, firebase_config_path=None):
        """
        Inicializa el procesador con configuración de Firebase.
        
        Args:
            firebase_config_path: Ruta al archivo de configuración de Firebase
        """
        self.db = None
        self.bucket = None
        self.initialize_firebase(firebase_config_path)
    
    def initialize_firebase(self, config_path=None):
        """Inicializa la conexión con Firebase"""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore, storage
            
            # Si ya está inicializado, usar la app existente
            try:
                app = firebase_admin.get_app()
                logging.info("Usando app Firebase existente")
            except ValueError:
                # No está inicializado, crear nueva app
                if config_path and os.path.exists(config_path):
                    cred = credentials.Certificate(config_path)
                else:
                    # Buscar en ubicación por defecto
                    default_path = os.path.join(
                        os.path.dirname(__file__),
                        "cliente_web",
                        "admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json"
                    )
                    if os.path.exists(default_path):
                        cred = credentials.Certificate(default_path)
                    else:
                        raise FileNotFoundError(
                            f"No se encontró archivo de credenciales Firebase. "
                            f"Busqué en: {default_path}"
                        )
                
                app = firebase_admin.initialize_app(cred, {
                    'storageBucket': 'admin-doc-ia.firebasestorage.app'
                })
                logging.info("Firebase inicializado correctamente")
            
            self.db = firestore.client()
            self.bucket = storage.bucket()
            
        except ImportError:
            logging.error("firebase_admin no está instalado. Instala con: pip install firebase-admin")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error al inicializar Firebase: {e}")
            sys.exit(1)
    
    def download_from_storage(self, storage_path, local_path):
        """
        Descarga un archivo desde Firebase Storage.
        
        Args:
            storage_path: Ruta en Firebase Storage (ej: clientes/uid/archivo.pdf)
            local_path: Ruta local donde guardar el archivo
        """
        try:
            blob = self.bucket.blob(storage_path)
            blob.download_to_filename(local_path)
            logging.info(f"Descargado: {storage_path} -> {local_path}")
            return True
        except Exception as e:
            logging.error(f"Error descargando {storage_path}: {e}")
            return False
    
    def extract_storage_path_from_url(self, url):
        """
        Extrae la ruta de Storage desde una URL de Firebase.
        
        Args:
            url: URL completa de Firebase Storage
        
        Returns:
            Ruta relativa en Storage (ej: clientes/uid/archivo.pdf)
        """
        try:
            # URLs formato: https://firebasestorage.googleapis.com/v0/b/BUCKET/o/PATH?alt=media
            if "firebasestorage.googleapis.com" in url:
                import urllib.parse
                # Extraer la parte después de /o/
                parts = url.split('/o/')
                if len(parts) > 1:
                    encoded_path = parts[1].split('?')[0]
                    # Decodificar URL encoding
                    decoded_path = urllib.parse.unquote(encoded_path)
                    return decoded_path
            
            # Si no es URL, asumir que ya es la ruta
            return url
        except Exception as e:
            logging.error(f"Error extrayendo ruta de Storage: {e}")
            return None
    
    def process_document(self, doc_id, doc_data):
        """
        Procesa un documento individual.
        
        Args:
            doc_id: ID del documento en Firestore
            doc_data: Datos del documento
        
        Returns:
            True si se procesó correctamente, False en caso contrario
        """
        try:
            nombre = doc_data.get('nombre', 'sin_nombre')
            url = doc_data.get('url')
            usuario_id = doc_data.get('usuarioId')
            
            logging.info(f"Procesando documento: {nombre} (ID: {doc_id})")
            
            # Actualizar estado a "procesando"
            self.db.collection('documentos').document(doc_id).update({
                'estado': 'procesando',
                'fechaProcesamiento': datetime.now().isoformat()
            })
            
            # Extraer ruta de Storage
            storage_path = self.extract_storage_path_from_url(url)
            if not storage_path:
                raise Exception("No se pudo extraer la ruta de Storage")
            
            # Crear directorio temporal
            with tempfile.TemporaryDirectory() as temp_dir:
                # Descargar archivo
                local_file = os.path.join(temp_dir, nombre)
                if not self.download_from_storage(storage_path, local_file):
                    raise Exception("Error al descargar el archivo")
                
                # Extraer texto usando ETL
                logging.info(f"Extrayendo texto de: {nombre}")
                contenido_extraido = choose_extractor(local_file)
                
                # Normalizar texto
                contenido_procesado = normalize_text(contenido_extraido)
                
                # Guardar contenido procesado en Firestore
                self.db.collection('documentos').document(doc_id).update({
                    'contenidoProcesado': contenido_procesado,
                    'estado': 'procesado',
                    'fechaProcesado': datetime.now().isoformat(),
                    'caracteresTotales': len(contenido_procesado)
                })
                
                logging.info(f"✅ Documento procesado exitosamente: {nombre} ({len(contenido_procesado)} caracteres)")
                return True
                
        except Exception as e:
            logging.error(f"❌ Error procesando documento {doc_id}: {e}")
            
            # Marcar como error en Firestore
            try:
                self.db.collection('documentos').document(doc_id).update({
                    'estado': 'error',
                    'errorMensaje': str(e),
                    'fechaError': datetime.now().isoformat()
                })
            except:
                pass
            
            return False
    
    def process_pending_documents(self):
        """
        Busca y procesa todos los documentos con estado 'pendiente'.
        """
        try:
            # Consultar documentos pendientes (usando filter para evitar warning)
            from google.cloud.firestore_v1.base_query import FieldFilter
            
            docs_ref = self.db.collection('documentos').where(
                filter=FieldFilter('estado', '==', 'pendiente')
            )
            docs = docs_ref.stream()
            
            processed_count = 0
            for doc in docs:
                doc_data = doc.to_dict()
                if self.process_document(doc.id, doc_data):
                    processed_count += 1
            
            if processed_count > 0:
                logging.info(f"Procesados {processed_count} documentos")
            
            return processed_count
            
        except Exception as e:
            logging.error(f"Error buscando documentos pendientes: {e}")
            return 0
    
    def listen_for_changes(self, interval=10):
        """
        Escucha cambios en Firestore y procesa nuevos documentos.
        
        Args:
            interval: Intervalo en segundos entre verificaciones
        """
        logging.info(f"🔄 Iniciando listener de documentos (intervalo: {interval}s)")
        logging.info("Presiona Ctrl+C para detener")
        
        try:
            while True:
                self.process_pending_documents()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logging.info("\n⏹️  Listener detenido por el usuario")
        except Exception as e:
            logging.error(f"Error en listener: {e}")
    
    def reprocess_document(self, doc_id):
        """
        Reprocesa un documento específico por su ID.
        
        Args:
            doc_id: ID del documento en Firestore
        """
        try:
            doc_ref = self.db.collection('documentos').document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                logging.error(f"Documento {doc_id} no encontrado")
                return False
            
            doc_data = doc.to_dict()
            return self.process_document(doc_id, doc_data)
            
        except Exception as e:
            logging.error(f"Error reprocesando documento {doc_id}: {e}")
            return False


def main():
    """Función principal del procesador"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🔄 Procesador Automático de Documentos - Intexta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Modo escucha continua (recomendado para producción)
  python document_processor.py --mode listen --interval 30

  # Procesar documentos pendientes una sola vez
  python document_processor.py --mode process-pending

  # Reprocesar un documento específico
  python document_processor.py --mode reprocess --doc-id ABC123

Modos disponibles:
  listen          - Escucha cambios continuamente (requiere Ctrl+C para detener)
  process-pending - Procesa documentos pendientes una vez y termina
  reprocess       - Fuerza reprocesamiento de un documento específico

Para más información: docs/DOCUMENT_PROCESSOR.md
        """
    )
    parser.add_argument(
        '--mode',
        choices=['listen', 'process-pending', 'reprocess'],
        default='listen',
        help='Modo de operación (default: listen)'
    )
    parser.add_argument(
        '--doc-id',
        help='ID del documento a reprocesar (solo para mode=reprocess)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Intervalo en segundos para el modo listen (default: 10)'
    )
    parser.add_argument(
        '--firebase-config',
        help='Ruta al archivo de configuración de Firebase (opcional)'
    )
    
    args = parser.parse_args()
    
    # Inicializar procesador
    processor = DocumentProcessor(args.firebase_config)
    
    # Ejecutar según modo
    if args.mode == 'listen':
        processor.listen_for_changes(interval=args.interval)
    
    elif args.mode == 'process-pending':
        count = processor.process_pending_documents()
        logging.info(f"Procesamiento completado: {count} documentos")
    
    elif args.mode == 'reprocess':
        if not args.doc_id:
            logging.error("Se requiere --doc-id para el modo reprocess")
            sys.exit(1)
        
        success = processor.reprocess_document(args.doc_id)
        if success:
            logging.info("Documento reprocesado exitosamente")
        else:
            logging.error("Error reprocesando documento")
            sys.exit(1)


if __name__ == "__main__":
    main()
