# Vercel Deployment Guide

## Frontend Deployment (React)

### Option 1: Deploy Frontend Only to Vercel (Recommended)

1. **Install Vercel CLI**
```bash
npm install -g vercel
```

2. **Login to Vercel**
```bash
vercel login
```

3. **Deploy from project root**
```bash
cd c:\Users\KIIT\OneDrive\Desktop\carbon-footprint-tracker
vercel
```

4. **Set Environment Variables in Vercel Dashboard**
   - Go to: `https://vercel.com/dashboard`
   - Select your project
   - Settings → Environment Variables
   - Add: `REACT_APP_API_URL` = `https://your-backend-url.com`

---

## Backend Deployment (Python/FastAPI)

For the Python backend, you have these options:

### Option A: Deploy to Render (FREE)
1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Set **Build Command**: `pip install -r backend/requirements.txt`
5. Set **Start Command**: `cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000`
6. Deploy!

### Option B: Deploy to Railway (FREE Tier)
1. Go to https://railway.app
2. Click "New Project"
3. Deploy from GitHub
4. Select your repo
5. Add environment variables if needed
6. Deploy!

### Option C: Deploy to Heroku
1. Go to https://www.heroku.com
2. Create a Procfile in backend/:
```
web: python -m uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

## Update Frontend API URL

After deploying backend, update your frontend:

Edit `frontend/src/utils/api.js`:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

In Vercel Dashboard, add environment variable:
```
REACT_APP_API_URL=https://your-backend-url.com
```

---

## Full Deployment Checklist

- [ ] Push code to GitHub
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Render/Railway/Heroku
- [ ] Set `REACT_APP_API_URL` env var in Vercel
- [ ] Update CORS in backend `app.py` to include Vercel domain
- [ ] Test both frontend and backend

---

## Update CORS for Production

In `backend/app.py`, update the `.env` file:

```env
ALLOWED_ORIGINS=https://your-vercel-domain.vercel.app,https://your-backend-url.com,http://localhost:3001,http://localhost:8000
DATABASE_URL=your-production-database-url
```

Or directly in the code if using environment variables.
