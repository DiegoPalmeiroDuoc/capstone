import os
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Obtiene la ruta base del proyecto (donde está manage.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta completa al JSON
cred_path = os.path.join(BASE_DIR, "admin-doc-ia-firebase-adminsdk-fbsvc-82d2fcac61.json")

# Inicializa Firebase
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'admin-doc-ia.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()

