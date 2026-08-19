import firebase_admin
from firebase_admin import credentials, firestore


def init_firebase():
    """Firebase ah initialize pannurom - once mattum run aagum"""
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_credentials.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()


def save_chat_history(db, question, answer):
    """Chat history ah Firebase la save pannurom"""
    doc_ref = db.collection("chat_history").document()
    doc_ref.set({
        "question": question,
        "answer": answer,
        "timestamp": firestore.SERVER_TIMESTAMP
    })


def get_chat_history(db):
    """Ella chat history ah retrieve pannurom"""
    docs = db.collection("chat_history").order_by("timestamp").stream()
    history = []
    for doc in docs:
        data = doc.to_dict()
        history.append(data)
    return history