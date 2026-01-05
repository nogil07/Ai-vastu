# Deployment Guide: Vastu AI

Vastu AI is a hybrid application with two distinct parts that run on different servers.
**This guide explains how to host them for free/cheap using Vercel (Frontend) and Render (Backend).**

## 1. Architecture Overview
*   **Frontend (Next.js)**: Hosted on **Vercel**. It serves the UI and runs in the browser.
*   **Backend (FastAPI)**: Hosted on **Render** (or Railway/Heroku). It processes the logic and returns JSON/PDFs.

---

## 2. Deploying the Backend (Render)
We deploy the backend first so we can get the API URL.

1.  **Push to GitHub**: ensure `d:\projects\ai vasu\main\vasu 1.0` is a GitHub repository.
2.  **Create Account**: Go to [render.com](https://render.com) and sign up/login.
3.  **New Web Service**:
    *   Click **New +** -> **Web Service**.
    *   Connect your GitHub repo.
4.  **Configuration**:
    *   **Root Directory**: `.` (leave empty or set to root).
    *   **Runtime**: `Python 3`.
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5.  **Environment Variables**:
    *   If you use any API keys (like Gemini), add them in the "Environment" tab.
6.  **Deploy**: Click Create. Render will give you a URL (e.g., `https://vastu-ai-backend.onrender.com`).
    *   **Copy this URL**.

---

## 3. Deploying the Frontend (Vercel)
Now we deploy the UI and tell it where the backend is.

1.  **Create Account**: Go to [vercel.com](https://vercel.com) and login with GitHub.
2.  **New Project**:
    *   Click **Add New...** -> **Project**.
    *   Select the *same* GitHub repo.
3.  **Configuration**:
    *   **Framework Preset**: Next.js (Auto-detected).
    *   **Root Directory**: Click "Edit" and select `frontend`. **(Crucial Step)**.
4.  **Environment Variables**:
    *   Add a new variable:
        *   **Name**: `NEXT_PUBLIC_API_URL`
        *   **Value**: The Render URL you copied (e.g., `https://vastu-ai-backend.onrender.com`).
        *   *Note: Do not add a trailing slash `/`.*
5.  **Deploy**: Click Deploy.
6.  **Result**: Vercel will give you a live domain (e.g., `https://vastu-ai.vercel.app`).

---

## 4. Verification
1.  Open your Vercel URL.
2.  Fill out the form and click "Generate Design".
3.  If successful, the Frontend (Vercel) will talk to the Backend (Render) and show you the results.

### Troubleshooting
*   **CORS Error**: If you see a generic network error, check the Backend logs on Render. You might need to add the Vercel domain to the `allow_origins` list in `app/main.py`.
    *   *Quick Fix*: In `app/main.py`, ensure `allow_origins=["*"]` allows everything, or add your specific Vercel domain.
