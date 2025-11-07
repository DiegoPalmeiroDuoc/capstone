#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para analizar el tamaño de documentos procesados y límites del sistema
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar path de Firebase
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'cliente_web'))

try:
    from firebase_config import db
except Exception as e:
    print(f"❌ Error importando Firebase: {e}")
    sys.exit(1)

def analizar_documentos():
    """Analiza todos los documentos procesados en Firestore"""
    
    print("=" * 80)
    print("📊 ANÁLISIS DE DOCUMENTOS PROCESADOS")
    print("=" * 80)
    
    try:
        # Obtener todos los documentos procesados
        docs = db.collection('documentos').where('estado', '==', 'procesado').stream()
        
        documentos = []
        for doc in docs:
            data = doc.to_dict()
            contenido = data.get('contenidoProcesado', '')
            
            documentos.append({
                'id': doc.id,
                'nombre': data.get('nombre', 'Sin nombre'),
                'usuario': data.get('usuarioId', 'Unknown'),
                'tamaño': len(contenido),
                'palabras': len(contenido.split()) if contenido else 0,
                'lineas': contenido.count('\n') if contenido else 0
            })
        
        if not documentos:
            print("❌ No hay documentos procesados en el sistema")
            return
        
        # Ordenar por tamaño
        documentos.sort(key=lambda x: x['tamaño'], reverse=True)
        
        print(f"\n📚 Total de documentos procesados: {len(documentos)}\n")
        
        # Estadísticas generales
        total_chars = sum(d['tamaño'] for d in documentos)
        total_words = sum(d['palabras'] for d in documentos)
        
        print("📊 ESTADÍSTICAS GENERALES")
        print("-" * 80)
        print(f"Total caracteres: {total_chars:,}")
        print(f"Total palabras: {total_words:,}")
        print(f"Promedio chars/doc: {total_chars // len(documentos):,}")
        print(f"Promedio palabras/doc: {total_words // len(documentos):,}")
        
        # Documentos más grandes
        print("\n📄 TOP 10 DOCUMENTOS MÁS GRANDES")
        print("-" * 80)
        print(f"{'Nombre':<50} {'Caracteres':>15} {'Palabras':>12}")
        print("-" * 80)
        
        for doc in documentos[:10]:
            nombre = doc['nombre'][:47] + '...' if len(doc['nombre']) > 50 else doc['nombre']
            print(f"{nombre:<50} {doc['tamaño']:>15,} {doc['palabras']:>12,}")
        
        # Análisis de límites
        print("\n⚠️  ANÁLISIS DE LÍMITES")
        print("-" * 80)
        
        # Límites del sistema
        LIMITE_CONTEXTO_ACTUAL = 60000  # chars (configuración actual)
        LIMITE_DEEPSEEK_TOKENS = 64000  # tokens (aprox. 256k chars)
        CHARS_POR_TOKEN_ESTIMADO = 4
        LIMITE_DEEPSEEK_CHARS = LIMITE_DEEPSEEK_TOKENS * CHARS_POR_TOKEN_ESTIMADO
        
        print(f"🔧 Límite actual del sistema: {LIMITE_CONTEXTO_ACTUAL:,} caracteres")
        print(f"🤖 Límite de DeepSeek (estimado): ~{LIMITE_DEEPSEEK_CHARS:,} caracteres")
        print(f"   (64k tokens × ~{CHARS_POR_TOKEN_ESTIMADO} chars/token)")
        
        # Documentos que exceden el límite
        docs_exceden = [d for d in documentos if d['tamaño'] > LIMITE_CONTEXTO_ACTUAL]
        
        if docs_exceden:
            print(f"\n⚠️  {len(docs_exceden)} documentos exceden el límite actual:")
            for doc in docs_exceden[:5]:
                exceso = doc['tamaño'] - LIMITE_CONTEXTO_ACTUAL
                porcentaje = (exceso / doc['tamaño']) * 100
                print(f"   • {doc['nombre'][:60]}")
                print(f"     Tamaño: {doc['tamaño']:,} chars | Exceso: {exceso:,} chars ({porcentaje:.1f}%)")
        
        # Recomendaciones
        print("\n💡 RECOMENDACIONES")
        print("-" * 80)
        
        doc_mas_grande = documentos[0]
        
        if doc_mas_grande['tamaño'] > LIMITE_DEEPSEEK_CHARS:
            print("🔴 CRÍTICO: Documento más grande excede límite de DeepSeek")
            print(f"   Documento: {doc_mas_grande['nombre']}")
            print(f"   Tamaño: {doc_mas_grande['tamaño']:,} caracteres")
            print(f"   Acción: Implementar chunking o dividir documento")
        elif doc_mas_grande['tamaño'] > LIMITE_CONTEXTO_ACTUAL:
            print("🟡 ADVERTENCIA: Documento más grande excede límite configurado")
            print(f"   Documento: {doc_mas_grande['nombre']}")
            print(f"   Tamaño: {doc_mas_grande['tamaño']:,} caracteres")
            print(f"   Acción: ✅ Ya implementado - búsqueda inteligente activa")
        else:
            print("✅ Todos los documentos dentro de límites manejables")
        
        print("\n🔍 BÚSQUEDA INTELIGENTE (Implementada)")
        print("-" * 80)
        print("✓ Extrae secciones relevantes basándose en palabras clave")
        print("✓ Máximo 60,000 caracteres de contexto por consulta")
        print("✓ Prioriza párrafos con coincidencias de la pregunta")
        print("✓ Mantiene coherencia del contenido")
        
        # Estimación de tokens para DeepSeek
        print("\n📊 ESTIMACIÓN DE USO DE TOKENS")
        print("-" * 80)
        
        for doc in documentos[:5]:
            tokens_estimados = doc['tamaño'] // CHARS_POR_TOKEN_ESTIMADO
            print(f"{doc['nombre'][:60]}")
            print(f"  Caracteres: {doc['tamaño']:,} | Tokens estimados: ~{tokens_estimados:,}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ Error analizando documentos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analizar_documentos()
