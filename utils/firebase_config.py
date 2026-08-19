import firebase_admin
from firebase_admin import credentials, firestore
import os
import json


def init_firebase():
    """Initialize Firebase - reads credentials from a local file or an environment variable"""
    if not firebase_admin._apps:
        firebase_creds_env = os.getenv("FIREBASE_CREDENTIALS")

        if firebase_creds_env:
            # On Render - read from environment variable
            cred_dict = json.loads(firebase_creds_env)
            cred = credentials.Certificate(cred_dict)
        else:
            # Local - read from file
            cred = credentials.Certificate("firebase_credentials.json")

        firebase_admin.initialize_app(cred)
    return firestore.client()


def save_chat_history(db, user_id, question, answer):
    """Save chat history to Firestore, scoped under the logged-in user's ID.

    Firestore structure: users/{user_id}/chat_history/{document_id}
    This keeps each user's chat history isolated from every other user.
    """
    doc_ref = (
        db.collection("users")
        .document(user_id)
        .collection("chat_history")
        .document()
    )
    doc_ref.set({
        "question": question,
        "answer": answer,
        "timestamp": firestore.SERVER_TIMESTAMP
    })


def get_chat_history(db, user_id):
    """Retrieve chat history for a specific user only (not other users' data)."""
    docs = (
        db.collection("users")
        .document(user_id)
        .collection("chat_history")
        .order_by("timestamp")
        .stream()
    )
    history = []
    for doc in docs:
        data = doc.to_dict()
        history.append(data)
    return history