# Import required libraries

from pydantic import BaseModel
from firebase_admin import credentials, firestore, initialize_app
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from dotenv import load_dotenv
import openai
import os
import requests
import firebase_admin

from jose import jwt
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# Load environment variables for JWT
SECRET_KEY=os.getenv('SECRET_KEY')
ALGORITHM=os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES')


# Initialize Firebase using the service account key
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to decode a JWT token
def decode_token(token):
    decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return decoded_data

# Function to summarize a note using Hugging Face API
def summarize_note(note):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn" 
    # "/models/gpt2"

    hugging_token=os.getenv('HUGGING_KEY')
    
    headers = {
    "Authorization": f"Bearer {hugging_token}"
    }

    payload = {
        "inputs": (
            f"Summarize the following paragraph in 1-2 lines:\n\n{note}"        )
    }  
    try:  
        response = requests.post(API_URL, headers=headers, json=payload)
        result_note=response.json()[0]['summary_text']

        return result_note
    except:
        # If error occurs, return default message
        result_note="Error occured. No results are generated"
        return result_note

# Function to categorize a note into topics using Hugging Face
def categorize_note(note):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn" 
    hugging_token=os.getenv('HUGGING_KEY')
    headers = {
    "Authorization": f"Bearer {hugging_token}"
    }

    payload = {
    "inputs": f"categorize this to different sections like Work, Health, Personal, etc. : '{note}' "
        }

    try:  
        response = requests.post(API_URL, headers=headers, json=payload)
        result_note=response.json()[0]['summary_text']

        return result_note
    except:
        # If error occurs, return default message
        result_note="Error occured. No results are generated"
        return result_note


# Function to check if user exists; if not, add them to Firebase
def user_save_db(user_info):
    users_ref = db.collection("users")
    query = users_ref.where("email", "==", user_info["email"]).get()
    if query:
        # User already exists, return reference
        user_get=query[0].reference
        return user_get
    else:
        # Create new user document
        db_user=db.collection("users").document()
        db_user.set({
            "google_id":user_info['id'],
            "name": user_info['name'],
            "email": user_info['email']
        })

        user_get=db_user
        return user_get

# Function to save summarized or categorized note into Firestore
def save_note_db(user_id,category,note,result):
    db_note=db.collection("ai_notes").document()
    db_note.set({
        "user": db.collection("users").document(user_id),
        "note": note,
        "converted_type": category,
        "result":result,
        "datetime": datetime.now()
    })

    return db_note.id

# Function to get all notes of a logged-in user
def history_loginned(email):
    users_ref = db.collection("users")
    query = users_ref.where("email", "==", email).get()
    if not query:
            return [] # No user found

    user_doc = query[0]
    user_ref = db.collection("users").document(user_doc.id)

    # Now fetch all notes that belong to this user
    notes_query = db.collection("ai_notes").where("user", "==", user_ref).get()
    # .order_by("datetime", direction=firestore.Query.DESCENDING).get()

    # Return list of notes with IDs
    notes = [{**n.to_dict(), "id": n.id} for n in notes_query]
    
    return notes


# Function to get a single note by ID
def single_note(note_id):
    notes_query = db.collection("ai_notes").document(note_id).get()
    if notes_query:
        return {**notes_query.to_dict(), "id": notes_query.id}
    
    return {}