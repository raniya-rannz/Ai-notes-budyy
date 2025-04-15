# Import necessary modules

import os
from fastapi import FastAPI,Request, Depends, HTTPException,Form,Header
from fastapi.responses import RedirectResponse,HTMLResponse
from dotenv import load_dotenv
import httpx
import urllib.parse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import openai
import functions as fun # Custom utility functions
from fastapi import Query
from fastapi.responses import JSONResponse

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app instance
app = FastAPI()

# Load Google OAuth2 and OpenAI credentials from environment
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_ENDPOINT = os.getenv("GOOGLE_AUTH_ENDPOINT")
GOOGLE_TOKEN_ENDPOINT = os.getenv("GOOGLE_TOKEN_ENDPOINT")
GOOGLE_USERINFO_ENDPOINT = os.getenv("GOOGLE_USERINFO_ENDPOINT")
SCOPES = os.getenv("SCOPES")

# Set template directory for rendering HTML files
templates = Jinja2Templates(directory="templates")

# Home route: Renders the home page with a welcome message
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request,"message":"Welcome to Google Login with FastAPI"})


# Login route: Redirects user to Google's OAuth 2.0 consent screen
@app.get("/login")
def login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "response_type": "code",
        "scope": SCOPES,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "access_type": "offline",
        "prompt": "consent",
    }
    # Construct the full URL for Google login
    url = f"{GOOGLE_AUTH_ENDPOINT}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)



# Callback route: Handles the response from Google after user login
@app.get("/auth/callback")
async def auth_callback(request: Request):
    # Get authorization code from the URL
    code = request.query_params.get("code")
    if not code:
        return {"error": "Missing code"}


    # Exchange authorization code for access token
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": 'http://localhost:8000/auth/callback',
        "grant_type": "authorization_code",
    }

     # Use httpx to make async POST request to get tokens
    client=httpx.AsyncClient()
    # async with httpx.AsyncClient() as client:
    token_res = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
    token_res.raise_for_status()
    token_data = token_res.json()

    # Extract access token
    access_token = token_data["access_token"]

    # Get user profile info using access token
    userinfo_res = await client.get(
        GOOGLE_USERINFO_ENDPOINT,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    userinfo_res.raise_for_status()
    user_info = userinfo_res.json()

    # Save user to database
    user_get=fun.user_save_db(user_info)

    # Create JWT token for session management
    jwt_token=fun.create_access_token(data={"email":user_info['email'],"user_id":user_get.id})

    # Redirect to options page with token and email
    url_r=f"http://localhost:8000/options?token={jwt_token}&email={user_info['email']}"
    response = RedirectResponse(url_r, status_code=302)
    response.set_cookie(key="email", value=user_info['email'])
    response.set_cookie(key="token",value=jwt_token)

    return response


# Route to show options after login (summarize, categorize, history)
@app.get("/options", response_class=HTMLResponse)
async def show_options_form(request: Request):
    token = request.cookies.get("token")
    email = request.cookies.get("email")
    if email:

        return templates.TemplateResponse("options.html", {"request": request, "token": token, "email": email})
    return RedirectResponse('/')


# Route to show history of notes for logged in user
@app.get("/history", response_class=HTMLResponse)
async def show_options_form(request: Request):
    email = request.cookies.get("email")
    history=fun.history_loginned(email)
    if email:
        return templates.TemplateResponse("history.html",{'request':request,"notes":history,'email':email})    
    return RedirectResponse('/')


# Route to handle option form submission (which action was selected)
@app.post("/submit", response_class=HTMLResponse)
async def form_post(request: Request,
                     action: str = Form(...),
                     ):
    
    email = request.cookies.get("email")
    token = request.cookies.get("token")
    if email:

        if action == "summarize":
            return templates.TemplateResponse("ai_note.html", {"request": request,'email':email,"category":action})
        if action=="categorize":
            return templates.TemplateResponse("ai_note.html", {"request": request,'email':email,"category":action})
        elif action=="history":
            url_r=f"http://localhost:8000/history?email={email}"
            response = RedirectResponse(url_r, status_code=302)
            response.set_cookie(key="email", value=email)
            response.set_cookie(key="token",value=token)

            return response

    return RedirectResponse('/')


# Route to process a note using AI (summarize or categorize)
@app.post("/convert", response_class=HTMLResponse)
async def conert_ai(request: Request,
                     category: str = Form(...),
                     note: str = Form(...),
                     ):
    

    token = request.cookies.get("token")
    email = request.cookies.get("email")
    if email:
        note_get=note

        # Decode token to get user ID
        user_decode=fun.decode_token(token)
        user_get=user_decode['user_id']

        if category == "summarize":
            result=fun.summarize_note(note_get)
            
            result_db_save=fun.save_note_db(user_get,"Summarized",note_get,result)
            
            # Redirect to note display page
            url_r=f"http://localhost:8000/note?note_id={result_db_save}"
            response = RedirectResponse(url_r, status_code=302)
            response.set_cookie(key="email", value=email)
            response.set_cookie(key="token",value=token)

            return response

        elif category == "categorize":
            result=fun.categorize_note(note_get)

            result_db_save=fun.save_note_db(user_get,"Categorized",note_get,result)

            url_r=f"http://localhost:8000/note?note_id={result_db_save}"
            response = RedirectResponse(url_r, status_code=302)
            response.set_cookie(key="email", value=email)
            response.set_cookie(key="token",value=token)

            return response

    return RedirectResponse('/')


# Route to show a single note's details
@app.get("/note", response_class=HTMLResponse)
async def show_options_form(request: Request):
    email = request.cookies.get("email")
    if email:
        note_id = request.query_params.get("note_id")
        data=fun.single_note(note_id)

        return templates.TemplateResponse("single_details.html", {"request": request,'note':data})
    return RedirectResponse('/')


# Route to handle user logout
@app.get("/logout")
def logout(request: Request):
    email = request.cookies.get("email")
    if email:
        response = RedirectResponse(url="/")
        response.delete_cookie("email")
        return response
    
    return RedirectResponse('/')
