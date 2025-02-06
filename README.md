# Telepathy Test Application

A web application that lets users test their telepathic connection with friends through an interactive card-matching game.

## Features

- Google Authentication
- Real-time multiplayer gameplay
- Email invitation system
- Interactive card selection
- Score tracking
- 10-round gameplay

## Setup Instructions

### Prerequisites

- A GitHub account
- A Google Cloud account
- A Supabase account (free tier)
- A Render account (free tier)

### 1. Database Setup (Supabase)

1. Go to [Supabase](https://supabase.com) and create a new account or sign in
2. Create a new project:
   - Choose a name for your project
   - Set a secure database password
   - Choose a region closest to your users
3. Once created, go to Project Settings → Database to find your database credentials:
   - Copy the `Connection String` (with password)
   - Save this for the environment setup

### 2. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Google OAuth2 API
4. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
5. Select "Web application" and configure:
   - Name: "Telepathy Test" (or your preferred name)
   - Authorized JavaScript origins:
     - `https://your-app-name.onrender.com` (production)
     - `http://localhost:3000` (development)
   - Authorized redirect URIs:
     - `https://your-app-name.onrender.com`
     - `https://your-app-name.onrender.com/dashboard`
     - `http://localhost:3000`
     - `http://localhost:3000/dashboard`
6. Save the Client ID and Client Secret

### 3. Deployment Setup (Render)

1. Push your code to a GitHub repository

2. Backend Deployment:
   - Go to [Render](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - Name: `telepathy-test`
     - Environment: Python
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn app:app`
   - Add environment variables:
     ```
     FLASK_ENV=production
     DATABASE_URL=your_supabase_connection_string
     GOOGLE_CLIENT_ID=your_google_client_id
     GOOGLE_CLIENT_SECRET=your_google_client_secret
     SECRET_KEY=generate_random_secret_key
     ```
   - Deploy

3. Frontend Deployment:
   - Click "New +" → "Static Site"
   - Connect your GitHub repository
   - Configure the build:
     - Build Command: `npm install && npm run build`
     - Publish Directory: `build`
   - Add environment variable:
     ```
     REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
     REACT_APP_API_URL=https://your-backend-url.onrender.com
     ```
   - Deploy

### Local Development

1. Clone your repository:
```bash
git clone your-repository-url
cd telepathy-test
```

2. Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` file:
```
FLASK_ENV=development
DATABASE_URL=your_supabase_connection_string
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
SECRET_KEY=your_secret_key
```

Run the backend:
```bash
python app.py
```

3. Frontend Setup:
```bash
cd frontend
npm install
```

Create `.env` file:
```
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
REACT_APP_API_URL=http://localhost:5000
```

Run the frontend:
```bash
npm start
```

## How to Play

1. Sign in with your Google account
2. Create a new game and invite a friend via email
3. Once your friend joins, you'll be shown 8 cards with different shapes
4. First player selects a card
5. Second player tries to guess which card was selected
6. Score is updated based on correct guesses
7. Game continues for 10 rounds
8. Final score is displayed to both players

## Technologies Used

- Backend:
  - Flask
  - Flask-SocketIO
  - SQLAlchemy
  - Supabase (PostgreSQL)
  - Google OAuth

- Frontend:
  - React
  - Material-UI
  - Socket.IO Client
  - React Router

- Deployment:
  - Render (hosting)
  - Supabase (database)
  - GitHub (version control)
