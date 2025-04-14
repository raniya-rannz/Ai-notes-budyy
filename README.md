# AI Notes Buddy

A simple FastAPI web app that lets users log in with Google and use AI to **summarize** or **categorize** their notes. Each note is stored in Firebase Firestore and linked to the authenticated user.

---

## 🚀 Features

- 🔐 Google OAuth2 Login
- ✍️ Note Submission for Summarization or Categorization
- 🤠 AI-Powered via Hugging Face GPT-2
- 💾 Firebase Firestore Integration (User & Note Storage)
- 📜 Note History Viewer
- 🍪 Session handled with JWT & Cookies
- 🎨 Frontend via Jinja2 + HTML/CSS

---

## ⚙️ Tech Stack

- **Backend**: FastAPI
- **Auth**: Google OAuth2
- **LLM API**: Hugging Face Inference API (GPT-2)
- **Database**: Firebase Firestore
- **Frontend**: HTML + CSS + Jinja2 Templates

---

## 📁 Project Structure

```
.
├── main.py                  # FastAPI application logic
├── functions.py             # Core utility functions (auth, db, AI)
├── templates/               # Jinja2 HTML templates
├── firebase_key.json        # Firebase admin credentials
├── .env                     # Environment variables
```

---

## 🔑 .env File

Create a `.env` file with:

```env
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
GOOGLE_AUTH_ENDPOINT=https://accounts.google.com/o/oauth2/v2/auth
GOOGLE_TOKEN_ENDPOINT=https://oauth2.googleapis.com/token
GOOGLE_USERINFO_ENDPOINT=https://www.googleapis.com/oauth2/v1/userinfo

GOOGLE_CLIENT_ID='your GOOGLE_CLIENT_ID'
GOOGLE_CLIENT_SECRET='your GOOGLE_CLIENT_SECRET'
OPENAI_API_KEY='your OPENAI_API_KEY'

SCOPES='openid email profile'

HUGGING_KEY=your_hugging_face_token
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 🤖 AI Processing (Hugging Face GPT-2)

- **Summarize**:  
  Prompt → `"Summarize this: <note>"`
- **Categorize**:  
  Prompt → `"Categorize this: <note>"`

Results are saved to Firestore with timestamp and type.

---

## 🔐 Auth Flow

1. User clicks login → redirected to Google OAuth
2. After Google consent:
   - Access token is fetched
   - User info is retrieved
   - JWT is created and stored in a cookie
   - Firestore user document is created/reused

---

## 📃 Firestore Collections

- `users`:  
  `{ id, google_id, name, email }`

- `ai_notes`:  
  `{ user, note, converted_type, result, datetime }`

---

## 📝 Sample Notes

Try these for summarization/categorization:

- "I need to submit the assignment before Monday."
- "Machine learning is transforming industries."
- "Schedule a doctor's appointment for next week."
- "Pick up laundry and clean the living room."

---

## ▶️ Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Then start the app:

```bash
uvicorn main:app --reload
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 📦 Requirements

```txt
fastapi
uvicorn
httpx
firebase-admin
python-dotenv
openai
python-jose
jinja2
```

---

## 🙌 Future Ideas

- Replace GPT-2 with more capable models
- Integrate with OpenAI or use LangChain (optional)

---

Made with ❤️ using FastAPI, Firebase & Hugging Face