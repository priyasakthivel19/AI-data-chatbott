import pyrebase

# Firebase Web config (from Firebase Console > Project Settings > Your apps)
firebase_config = {
    "apiKey": "AIzaSyBZlMhS8l-6NlRITeabWPJ0At7pArDl1Ko",
    "authDomain": "ai-data-chatbot-e4e92.firebaseapp.com",
    "projectId": "ai-data-chatbot-e4e92",
    "storageBucket": "ai-data-chatbot-e4e92.firebasestorage.app",
    "messagingSenderId": "283237521213",
    "appId": "1:283237521213:web:8e7e394174ae2af48f1754",
    "databaseURL": ""  # not using Realtime Database, keep empty
}


def init_firebase_auth():
    """Initialize Pyrebase app and return the auth client (for email/password login & signup)."""
    firebase = pyrebase.initialize_app(firebase_config)
    return firebase.auth()


def sign_up(auth, email, password):
    """Create a new user account with email & password.
    Returns (success: bool, result: dict or error message string)
    """
    try:
        user = auth.create_user_with_email_and_password(email, password)
        return True, user
    except Exception as e:
        error_message = str(e)
        if "EMAIL_EXISTS" in error_message:
            return False, "This email is already registered. Please log in instead."
        elif "WEAK_PASSWORD" in error_message:
            return False, "Password should be at least 6 characters."
        elif "INVALID_EMAIL" in error_message:
            return False, "Please enter a valid email address."
        return False, "Sign up failed. Please try again."


def sign_in(auth, email, password):
    """Log in an existing user with email & password.
    Returns (success: bool, result: dict or error message string)
    """
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return True, user
    except Exception as e:
        error_message = str(e)
        if "INVALID_LOGIN_CREDENTIALS" in error_message or "INVALID_PASSWORD" in error_message or "EMAIL_NOT_FOUND" in error_message:
            return False, "Incorrect email or password."
        return False, "Login failed. Please try again."   