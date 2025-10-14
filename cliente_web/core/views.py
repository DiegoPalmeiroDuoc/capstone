from django.http import JsonResponse
from django.shortcuts import render
from firebase_config import db

# Create your views here.

def index(request):
    return render(request, 'index.html')

def login_view(request):
    return render(request, 'login.html')

def dashboard_view(request):
    return render(request, 'dashboard.html')

def perfil_view(request):
    return render(request, 'perfil.html')

def home(request):
    return render(request,'home.html')

def api_list_docs(request):
    # Ejemplo: devolver documentos de un usuario (UID pasado por parámetro)
    uid = request.GET.get('uid')
    docs_ref = db.collection('documentos').where('usuarioId', '==', uid)
    docs = [doc.to_dict() for doc in docs_ref.stream()]
    return JsonResponse(docs, safe=False)

