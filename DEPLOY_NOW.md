# 🚀 DEPLOY NOW - Alberta Perspectives

## ✅ **READY TO DEPLOY!**

Everything is configured and ready. Follow these steps:

---

## 🚂 **Step 1: Deploy Backend to Railway (2 minutes)**

1. **Go to:** https://railway.app
2. **Click:** "Start a New Project"
3. **Select:** "Deploy from GitHub repo"
4. **Choose:** Your GitHub repository
5. **Settings:**
   - Root Directory: `backend`
   - Framework: Python
6. **Environment Variables:**
   ```
   SUPABASE_URL=https://aaegatfojqyfronbkpgn.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhZWdhdGZvanF5ZnJvbmJrcGduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MTQxMDcsImV4cCI6MjA0OTQ5MDEwN30.kqQHLvpkZOPy9rrj7uAX8k8oEqSI3mQCAGhyUJBWoUE
   GOOGLE_API_KEY=[Your Gemini API Key]
   DEBUG=false
   ```

7. **Copy the Railway URL** (e.g., `https://alberta-perspectives-backend.railway.app`)

---

## 📱 **Step 2: Deploy Frontend to Vercel (2 minutes)**

1. **Go to:** https://vercel.com
2. **Click:** "New Project"
3. **Import:** Your GitHub repository
4. **Settings:**
   - Framework: Next.js
   - Root Directory: `frontend`
5. **Environment Variable:**
   ```
   NEXT_PUBLIC_API_URL=[Your Railway URL from Step 1]
   ```

6. **Deploy!**

---

## 🧪 **Step 3: Test Production (30 seconds)**

1. **Visit your Vercel URL**
2. **Ask:** "What are the key findings about skills training in Alberta?"
3. **Verify:** You get an AI response with sources

---

## 🎯 **That's it!**

Your RAG application is now **LIVE** and deployed! 

### **Production URLs:**
- **Frontend:** `https://[your-app].vercel.app`
- **Backend:** `https://[your-app].railway.app`
- **API Docs:** `https://[your-app].railway.app/docs`

### **Time to deploy:** ~5 minutes total ⚡

---

## 🔧 **Environment Variables Reference**

### Backend Environment (Railway):
```
SUPABASE_URL=https://aaegatfojqyfronbkpgn.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFhZWdhdGZvanF5ZnJvbmJrcGduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzM5MTQxMDcsImV4cCI6MjA0OTQ5MDEwN30.kqQHLvpkZOPy9rrj7uAX8k8oEqSI3mQCAGhyUJBWoUE
GOOGLE_API_KEY=[Your Gemini API Key]
DEBUG=false
```

### Frontend Environment (Vercel):
```
NEXT_PUBLIC_API_URL=[Your Railway Backend URL]
```

**GO DEPLOY!** 🚀 