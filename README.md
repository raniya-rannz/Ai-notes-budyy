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

🤖 AI Processing (Hugging Face GPT-2 or Local Ollama)
You can process notes with:

Hugging Face GPT-2 (cloud-based)

Ollama with Mistral (local, faster, private)

🛠️ Setup Ollama (Optional, for Local LLM Inference)
Ollama lets you run LLMs like Mistral locally with zero setup. If you prefer not to rely on cloud APIs, follow these steps:

1. Install Ollama
Visit https://ollama.com and download/install for your OS.

2. Pull the Mistral Model
Once installed, open a terminal and run:

cmd: ollama pull mistral

3. Start the Ollama Service

Make sure Ollama is running. Usually it starts automatically in the background. If needed,

cmd: ollama run mistral
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


🔑 Firebase Admin SDK (firebase_key.json)
To enable Firebase Firestore integration, you need to provide Firebase Admin credentials. Follow these steps:

1. Go to Firebase Console
Open https://console.firebase.google.com

Select your project or create a new one.

2. Generate Admin SDK Key
Go to Project Settings > Service Accounts

Click Generate new private key

Download the .json file

3. Save the Key
Place the file in your project root and rename it: firebase_key.json

4. Add to .gitignore

cmd: echo "firebase_key.json" >> .gitignore



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

🐳 Docker Support
🔧 Dockerfile
Dockerfile
 # Dockerfile

FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
🧱 docker-compose.yml
yaml
 version: "3.9"

services:
  fastapi-app:
    build: .
    container_name: ai-notes-buddy
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - ./firebase_key.json:/app/firebase_key.json
      - ./.env:/app/.env
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GOOGLE_REDIRECT_URI=${GOOGLE_REDIRECT_URI}
      - GOOGLE_AUTH_ENDPOINT=${GOOGLE_AUTH_ENDPOINT}
      - GOOGLE_TOKEN_ENDPOINT=${GOOGLE_TOKEN_ENDPOINT}
      - GOOGLE_USERINFO_ENDPOINT=${GOOGLE_USERINFO_ENDPOINT}
      - SCOPES=${SCOPES}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGING_KEY=${HUGGING_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=${ALGORITHM}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
    restart: unless-stopped

▶️ Run the App with Docker
bash
 docker-compose up --build
Visit: http://localhost:8000

To stop:

bash
 docker-compose down


## 🙌 Future Ideas

- Replace GPT-2 with more capable models
- Integrate with OpenAI or use LangChain (optional)

---

Made with ❤️ using FastAPI, Firebase & Hugging Face