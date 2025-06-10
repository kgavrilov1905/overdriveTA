# 🚀 Deployment Guide - Alberta Perspectives

## Quick Deploy (5 minutes total)

### 📱 **Frontend Deployment (Vercel)**

1. **Push to GitHub** (if not already done)
2. **Go to [vercel.com](https://vercel.com)**
3. **Import your GitHub repository**
4. **Deploy Settings:**
   - Framework: Next.js
   - Build Command: `npm run build`
   - Install Command: `npm install`
   - Root Directory: `frontend`

5. **Environment Variables:**
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```

### 🚂 **Backend Deployment (Railway)**

1. **Go to [railway.app](https://railway.app)**
2. **Deploy from GitHub**
3. **Select your repository**
4. **Root Directory:** `backend`
5. **Environment Variables:**
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   GOOGLE_API_KEY=your_gemini_api_key
   DEBUG=false
   ```

### 🔗 **Final Steps**

1. **Get Railway URL** (e.g., `https://your-app.railway.app`)
2. **Update Vercel Environment:**
   - Set `NEXT_PUBLIC_API_URL` to your Railway URL
3. **Redeploy Vercel** (automatic)

## 📋 **Environment Variables Needed**

### Backend (Railway):
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY` 
- `GOOGLE_API_KEY`
- `DEBUG=false`

### Frontend (Vercel):
- `NEXT_PUBLIC_API_URL`

## ✅ **Testing Production**

1. Visit your Vercel URL
2. Test a query: "What are the key findings about skills training in Alberta?"
3. Verify sources appear
4. Check mobile responsiveness

## 🎯 **URLs After Deployment**

- **Frontend:** `https://your-app.vercel.app`
- **Backend:** `https://your-app.railway.app`
- **API Docs:** `https://your-app.railway.app/docs`

---

**Time to deploy: ~5 minutes** ⚡ 