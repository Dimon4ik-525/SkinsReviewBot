import os
import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_KEY_PATH

_db = None

def get_firestore_client() -> firestore.firestore.Client:
    """Ініціалізація та повернення синглтона клієнта Firestore."""
    global _db
    if _db is None:
        if not os.path.exists(FIREBASE_KEY_PATH):
            raise FileNotFoundError(
                f"Файл ключа Firebase не знайдено за шляхом: {FIREBASE_KEY_PATH}. "
                "Перевірте наявність файлу та змінну FIREBASE_KEY_PATH у .env"
            )
        cred = credentials.Certificate(FIREBASE_KEY_PATH)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
    return _db

# Зручний доступ як функцією, так і готовим об'єктом
get_db = get_firestore_client
db = get_firestore_client()