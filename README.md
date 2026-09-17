# Salon AI Receptionist

A text and voice-based AI salon receptionist built with FastAPI, PostgreSQL, Groq, Faster Whisper, and Streamlit.

The receptionist allows users to:

- Register and log in.
- Ask about salon services.
- Check available appointment slots.
- Book appointments.
- Cancel appointments.
- Reschedule appointments.
- View their existing appointments.
- Interact through text or voice input.

---

## Features

- User registration and login.
- PostgreSQL database for users, services, and appointments.
- AI-powered conversation using Groq.
- Tool-based appointment booking and cancellation.
- Real-time appointment availability checking.
- Voice-to-text using Faster Whisper.
- Streamlit web interface.
- FastAPI backend API.
- Conversation history maintained during the session.

---

## Project Structure

```text
salon-ai-receptionist/
│
├── app/
│   ├── chatbot/
│   │   └── chatbot.py
│   │
│   ├── llm/
│   │   └── receptionist.py
│   │
│   ├── services/
│   │   └── auth_service.py
│   │
│   ├── voice/
│   │   └── speech_to_text.py
│   │
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── main.py
│   └── ...
│
├── ui/
│   └── streamlit_app.py
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Technologies Used

- Python 3.10
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Groq API
- Faster Whisper
- Streamlit
- Python-dotenv
- Psycopg2

---

# Setup Instructions

## 1. Clone the repository

After uploading this project to GitHub, clone it using:

```powershell
git clone https://github.com/YOUR_GITHUB_USERNAME/salon-ai-receptionist.git
```

Move into the project directory:

```powershell
cd salon-ai-receptionist
```

---

## 2. Create a Python virtual environment

Create a virtual environment using Python 3.10:

```powershell
py -3.10 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If activation is successful, PowerShell should show:

```text
(.venv)
```

---

## 3. Install dependencies

Upgrade pip if needed:

```powershell
python -m pip install --upgrade pip
```

Install project dependencies:

```powershell
pip install -r requirements.txt
```

---

# Environment Variables

Create a file named `.env` in the project root.

Example:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/salon_db
GROQ_API_KEY=your_groq_api_key
```

Replace:

- `your_password` with your PostgreSQL password.
- `your_groq_api_key` with your actual Groq API key.

Never commit `.env` to GitHub.

---

# PostgreSQL Setup

## 1. Install PostgreSQL

Install PostgreSQL and make sure the PostgreSQL server is running.

Check the installation:

```powershell
psql --version
```

Example:

```text
psql (PostgreSQL) 18.x
```

---

## 2. Create the database

Open PostgreSQL using pgAdmin or `psql`.

Create a database named:

```text
salon_db
```

Using `psql`:

```sql
CREATE DATABASE salon_db;
```

---

## 3. Configure the database connection

Make sure your `.env` contains the correct PostgreSQL connection string:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/salon_db
```

---

## 4. Test the database connection

From the project root:

```powershell
python app\test_db.py
```

Expected output:

```text
Database connection successful!
```

---

## 5. Create database tables

Run:

```powershell
python -m app.create_tables
```

This creates the required tables, such as:

- `users`
- `services`
- `appointments`

---

# Run the FastAPI Backend

Open PowerShell Terminal 1.

Go to the project directory:

```powershell
cd C:\Users\Nimap\Desktop\salon-ai-receptionist
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

The backend should run at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# Run the Streamlit UI

Open a second PowerShell Terminal.

Go to the project directory:

```powershell
cd C:\Users\Nimap\Desktop\salon-ai-receptionist
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start Streamlit:

```powershell
streamlit run ui\streamlit_app.py
```

The UI should open at:

```text
http://localhost:8501
```

---

# How to Use the Application

## 1. Register

Open the Streamlit application.

Create a new account using:

- Full name
- Email
- Phone number (optional)
- Password

---

## 2. Login

Log in using your email and password.

---

## 3. Text Chat

Type messages such as:

```text
What services do you offer?
```

```text
I want to book a haircut tomorrow at 3 PM.
```

```text
What appointments do I have?
```

```text
Cancel my appointment.
```

```text
Are there any slots available at 5 PM?
```

---

## 4. Voice Chat

In the Streamlit UI:

1. Click the microphone/audio recording widget.
2. Record your message.
3. Stop recording.
4. Faster Whisper converts your speech into text.
5. The transcribed text is sent to the FastAPI chatbot.
6. The AI receptionist processes the request.

Example voice request:

```text
I want to book a haircut tomorrow at 2 PM.
```

---

# Database Tables

## users

Stores customer account information.

Example columns:

- `id`
- `name`
- `email`
- `phone`
- `password`

---

## services

Stores salon services.

Example services:

| ID | Service | Duration | Price |
|----|---------|----------|-------|
| 1 | Haircut | 30 minutes | 300 |
| 2 | Beard Trim | 20 minutes | 200 |
| 3 | Facial | 60 minutes | 800 |
| 4 | Hair Spa | 60 minutes | 1000 |

---

## appointments

Stores customer bookings.

Example columns:

- `id`
- `user_id`
- `service_id`
- `appointment_date`
- `appointment_time`
- `status`
- `created_at`

Possible appointment statuses:

```text
booked
cancelled
```

---

# Important Commands

## Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## Start FastAPI

```powershell
uvicorn app.main:app --reload
```

## Start Streamlit

```powershell
streamlit run ui\streamlit_app.py
```

## Test database connection

```powershell
python app\test_db.py
```

## Create database tables

```powershell
python -m app.create_tables
```

## Generate requirements.txt

```powershell
pip freeze > requirements.txt
```

## Install dependencies

```powershell
pip install -r requirements.txt
```

---

# Troubleshooting

## ModuleNotFoundError: No module named 'app'

Make sure the project-root path is added before importing application modules in `ui/streamlit_app.py`.

The correct path code for the current UI location is:

```python
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

This is required because `streamlit_app.py` is inside:

```text
ui/
```

and the `app/` package is one level above it.

---

## FastAPI connection error

If Streamlit displays:

```text
Could not connect to FastAPI.
```

Make sure Uvicorn is running in another terminal:

```powershell
uvicorn app.main:app --reload
```

---

## PostgreSQL connection error

Check:

- PostgreSQL is running.
- The database `salon_db` exists.
- The username and password in `.env` are correct.
- PostgreSQL is using port `5432`.

---

## Whisper is slow

Faster Whisper runs on the CPU in this project.

The model currently uses:

```python
WhisperModel(
    "small.en",
    device="cpu",
    compute_type="int8",
)
```

The first transcription may take longer because the model needs to load.

---

# Development Workflow

Whenever you make changes:

1. Activate the virtual environment.
2. Start FastAPI.
3. Start Streamlit.
4. Test the feature.
5. Check Git changes.
6. Commit the changes.
7. Push to GitHub.

Example:

```powershell
git status
git add .
git commit -m "Update salon receptionist"
git push
```

---

# Future Improvements

Possible future features:

- Multiple salon branches.
- Staff management.
- Admin dashboard.
- Appointment reminders.
- WhatsApp integration.
- Email notifications.
- Text-to-speech responses.
- Multiple language support.
- Calendar integration.
- Payment integration.
- Docker deployment.
- Cloud deployment.
- Production authentication using JWT.
- Better appointment conflict handling.

---

# Author

Developed as an AI/ML practice project using FastAPI, PostgreSQL, Groq, Faster Whisper, and Streamlit.
