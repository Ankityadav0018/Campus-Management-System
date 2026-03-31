# 🚀 Render Deployment Guide

**Status:** ✅ Project is NOW Render-Compatible
**Date:** March 31, 2026

---

## 📋 What Was Done to Make It Render-Compatible

### 1. **Created render.yaml**
   - Defines web service configuration for Render
   - Automatically creates PostgreSQL database
   - Sets environment variables
   - Configures build and start commands

### 2. **Created build.sh**
   - Build script for Render deployment
   - Installs dependencies
   - Collects static files
   - Runs database migrations

### 3. **Created settings_render.py**
   - Render-specific Django settings
   - Handles DATABASE_URL from Render
   - Console-only logging (no file I/O on ephemeral filesystem)
   - Proper security settings

### 4. **Updated requirements.txt**
   - Added `django-redis>=5.4.0` for caching
   - Already includes `dj-database-url` for DB URL parsing
   - All production dependencies included

### 5. **Updated settings.py**
   - Support for `DATABASE_URL` environment variable
   - dj-database-url integration
   - Render detection via `RENDER` environment variable
   - Ephemeral filesystem handling

---

## 🎯 Step-by-Step Render Deployment

### **Step 1: Push to GitHub**
Make sure all code is pushed to GitHub:
```bash
cd "/Users/ankityadav/Downloads/pep projects/project2"
git add -A
git commit -m "feat: Add Render deployment configuration"
git push origin main
```

### **Step 2: Create Render Account**
1. Go to https://render.com
2. Sign up with GitHub account
3. Grant permissions

### **Step 3: Connect Repository**
1. Click "New +" → "Web Service"
2. Select your GitHub repository
3. Choose branch (main)

### **Step 4: Configure Service**
In Render dashboard, set these values:

**Service Settings:**
- **Name:** `campus-management` (or any name)
- **Runtime:** `Python 3.11`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn campus_project.wsgi:application --bind 0.0.0.0:$PORT`

**Environment Variables:**
```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-render-app.onrender.com
DJANGO_SETTINGS_MODULE=campus_project.settings
RENDER=True
```

### **Step 5: Add PostgreSQL Database**
1. Click "New +" → "PostgreSQL"
2. Name: `campus-db`
3. Plan: Free
4. Create database
5. Copy connection string

### **Step 6: Link Database to Web Service**
In web service settings:
- Find "Environment" section
- Add environment variable:
  - **Key:** `DATABASE_URL`
  - **Value:** Paste the PostgreSQL connection string from the database service

### **Step 7: Deploy**
1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes first time)
3. Once deployed, you'll get a URL like: `https://campus-management.onrender.com`

---

## ✅ Deployment Checklist

Before deploying:
- [ ] All code committed and pushed to GitHub
- [ ] `render.yaml` present in root directory
- [ ] `build.sh` present and executable
- [ ] `settings_render.py` created
- [ ] `requirements.txt` updated with all dependencies
- [ ] `.env.example` file exists (for reference)

After deployment:
- [ ] Web service shows "Live" status
- [ ] Database is connected
- [ ] No build errors in logs
- [ ] Access app at provided URL
- [ ] Admin panel loads at `/admin`

---

## 📊 Environment Variables Needed

Set these in Render dashboard:

```
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=your-domain.onrender.com
DJANGO_SETTINGS_MODULE=campus_project.settings
RENDER=True
DATABASE_URL=<auto-populated-by-render>
```

### Generate Strong SECRET_KEY:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 🔍 Monitoring Deployment

### View Logs:
```bash
# Render shows logs in dashboard in real-time
# Or use Render CLI:
render logs campus-management
```

### Common Issues & Solutions:

#### **Issue: Build fails with "pip command not found"**
- ✅ **Solution:** Use `./build.sh` as build command

#### **Issue: Static files not loading**
- ✅ **Solution:** Run `python manage.py collectstatic --noinput`
- Already included in `build.sh`

#### **Issue: Database connection error**
- ✅ **Solution:** Verify `DATABASE_URL` environment variable
- ✅ Check PostgreSQL service is running
- ✅ Make sure database is linked in web service

#### **Issue: "ModuleNotFoundError" for imports**
- ✅ **Solution:** Check `requirements.txt` has all packages
- ✅ Rebuild service: Render dashboard → Manual deploy

#### **Issue: Migrations fail**
- ✅ **Solution:** Check database connection
- ✅ Run manually: Render dashboard → Shell → `python manage.py migrate`

---

## 🎛️ Scaling & Performance

### Database:
- **Free Plan:** 256 MB storage, limited connections
- **Recommended for production:** Upgrade to Standard or Pro

### Web Service:
- **Free Plan:** 0.5 CPU, 512 MB RAM, sleeps after 15 min inactivity
- **Recommended for production:** Upgrade to paid plan

### Enable Redis Caching (Optional):
```bash
# In Render dashboard:
# 1. Create Redis service
# 2. Get connection string
# 3. Add to web service:
#    REDIS_URL=<redis-connection-string>
#    USE_REDIS=True
```

---

## 🔐 Security Notes

### Before Going Live:
1. ✅ Change `SECRET_KEY` to a strong random value
2. ✅ Set `DEBUG=False`
3. ✅ Set correct `ALLOWED_HOSTS`
4. ✅ Use HTTPS (Render provides free SSL)
5. ✅ Set strong database password

### After Deployment:
1. ✅ Create superuser:
   ```bash
   # Via Render Shell
   python manage.py createsuperuser
   ```

2. ✅ Test admin panel:
   ```
   https://your-app.onrender.com/admin
   ```

3. ✅ Test all features

---

## 📊 Project Structure for Render

```
project2/
├── render.yaml              ✅ Render config
├── build.sh                 ✅ Build script
├── requirements.txt         ✅ Dependencies
├── Procfile                 (Heroku - optional)
├── manage.py               ✅ Django management
├── campus_project/
│   ├── settings.py         ✅ Updated for Render
│   ├── settings_render.py  ✅ Render-specific settings
│   ├── wsgi.py            ✅ WSGI application
│   └── urls.py            ✅ URL routing
├── apps/                   ✅ All apps configured
├── templates/              ✅ HTML templates
├── static/                 ✅ Static files
└── media/                  ✅ Media files
```

---

## 🚀 Quick Deploy Command

If using Render CLI:
```bash
# Install Render CLI
npm install -g @render-com/cli

# Login
render login

# Deploy
render deploy --repo Ankityadav0018/Campus-Management-System
```

---

## 📞 Helpful Resources

- **Render Docs:** https://render.com/docs
- **Django Deployment:** https://docs.djangoproject.com/en/4.2/howto/deployment/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Gunicorn:** https://docs.gunicorn.org/

---

## ✨ Features Supported on Render

✅ Full Django application
✅ PostgreSQL database (included free)
✅ Static file serving (via WhiteNoise)
✅ Media file uploads (stores in persistent disk)
✅ Email sending (via SMTP)
✅ Scheduled tasks (via cron jobs)
✅ SSL/HTTPS (automatic)
✅ Custom domain support
✅ Environment variables
✅ Logs streaming

---

## 📈 Next Steps After Deployment

1. **Create Admin Account**
   ```bash
   render shell
   python manage.py createsuperuser
   ```

2. **Add Test Data**
   - Use admin panel at `/admin`
   - Create users, students, courses

3. **Test Features**
   - User registration
   - Attendance tracking
   - Face recognition
   - Food ordering

4. **Monitor Performance**
   - Check Render dashboard logs
   - Monitor database usage
   - Watch for errors

5. **Scale When Needed**
   - Upgrade to paid plans
   - Add Redis for caching
   - Use CDN for static files

---

**Your project is now ready for Render deployment! 🎉**

For issues or questions, refer to Render's documentation or check the logs in your Render dashboard.
