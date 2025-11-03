from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from firebase_config import db
from firebase_admin import firestore
import json
import subprocess
import os

# Create your views here.

def index(request):
    return render(request, 'index.html')

def login_view(request):
    return render(request, 'login.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def perfil_view(request):
    return render(request, 'perfil.html')

def debug_logs_view(request):
    return render(request, 'debug_logs.html')

def home(request):
    return render(request,'home.html')

# ==================== API ENDPOINTS ====================

def api_list_docs(request):
    """Lista documentos de un usuario"""
    try:
        uid = request.GET.get('uid')
        if not uid:
            return JsonResponse({'error': 'UID requerido'}, status=400)
        
        docs_ref = db.collection('documentos').where('usuarioId', '==', uid)
        docs = [doc.to_dict() for doc in docs_ref.stream()]
        return JsonResponse(docs, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_process_document(request):
    """Marca un documento para ser procesado"""
    try:
        data = json.loads(request.body)
        doc_id = data.get('doc_id')
        
        if not doc_id:
            return JsonResponse({'error': 'doc_id requerido'}, status=400)
        
        # Actualizar estado a pendiente
        db.collection('documentos').document(doc_id).update({
            'estado': 'pendiente'
        })
        
        return JsonResponse({
            'success': True,
            'message': 'Documento marcado para procesamiento',
            'doc_id': doc_id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_document_status(request):
    """Obtiene el estado de procesamiento de documentos de un usuario"""
    try:
        uid = request.GET.get('uid')
        if not uid:
            return JsonResponse({'error': 'UID requerido'}, status=400)
        
        docs_ref = db.collection('documentos').where('usuarioId', '==', uid)
        docs = docs_ref.stream()
        
        stats = {
            'total': 0,
            'pendiente': 0,
            'procesando': 0,
            'procesado': 0,
            'error': 0,
            'documentos': []
        }
        
        for doc in docs:
            data = doc.to_dict()
            estado = data.get('estado', 'pendiente')
            
            stats['total'] += 1
            stats[estado] = stats.get(estado, 0) + 1
            
            stats['documentos'].append({
                'id': doc.id,
                'nombre': data.get('nombre'),
                'estado': estado,
                'descripcion': data.get('descripcion', ''),
                'fechaSubida': data.get('fechaSubida', ''),
                'fechaProcesado': data.get('fechaProcesado', ''),
                'caracteresTotales': data.get('caracteresTotales', 0),
                'errorMensaje': data.get('errorMensaje', '')
            })
        
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_trigger_processor(request):
    """Dispara manualmente el procesador de documentos"""
    try:
        # Ejecutar el procesador en modo process-pending
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        processor_path = os.path.join(project_root, 'document_processor.py')
        
        if not os.path.exists(processor_path):
            return JsonResponse({
                'error': 'Procesador no encontrado',
                'path': processor_path
            }, status=500)
        
        # Ejecutar en background
        result = subprocess.Popen(
            ['python', processor_path, '--mode', 'process-pending'],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Procesador iniciado',
            'pid': result.pid
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_phone(request):
    """Actualiza el número de teléfono de un usuario para WhatsApp"""
    try:
        data = json.loads(request.body)
        uid = data.get('uid')
        telefono = data.get('telefono')
        
        if not uid or not telefono:
            return JsonResponse({'error': 'UID y teléfono requeridos'}, status=400)
        
        # Crear o actualizar usuario en Firestore
        db.collection('usuarios').document(uid).set({
            'telefono': telefono,
            'uid': uid,
            'fechaActualizacion': firestore.SERVER_TIMESTAMP
        }, merge=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Teléfono actualizado correctamente'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_search_documents(request):
    """Busca en el contenido procesado de los documentos"""
    try:
        uid = request.GET.get('uid')
        query = request.GET.get('query', '').lower()
        
        if not uid:
            return JsonResponse({'error': 'UID requerido'}, status=400)
        
        if not query:
            return JsonResponse({'error': 'Query requerido'}, status=400)
        
        # Obtener documentos procesados del usuario
        docs_ref = db.collection('documentos')\
            .where('usuarioId', '==', uid)\
            .where('estado', '==', 'procesado')
        
        docs = docs_ref.stream()
        
        resultados = []
        for doc in docs:
            data = doc.to_dict()
            contenido = data.get('contenidoProcesado', '').lower()
            
            # Buscar query en el contenido
            if query in contenido:
                # Extraer contexto alrededor de la coincidencia
                idx = contenido.find(query)
                start = max(0, idx - 100)
                end = min(len(contenido), idx + len(query) + 100)
                snippet = contenido[start:end]
                
                resultados.append({
                    'doc_id': doc.id,
                    'nombre': data.get('nombre'),
                    'snippet': '...' + snippet + '...',
                    'descripcion': data.get('descripcion', '')
                })
        
        return JsonResponse({
            'query': query,
            'total': len(resultados),
            'resultados': resultados
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

