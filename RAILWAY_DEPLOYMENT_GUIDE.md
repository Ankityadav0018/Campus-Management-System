# 🚀 Railway Deployment Guide

**Status:** ✅ Project is NOW Railway-Compatible
**Date:** March 31, 2026

---

## 📋 What Was Done to Make It Railway-Compatible

### 1. **Created railway.yaml**
   - Defines Railway service configuration
   - Supports Docker deployment
   - Includes PostgreSQL database service
   - Persistent storage volumes configured
   - Health check endpoint configured

### 2. **Created settings_railway.py**
   - Railway-specific Django settings
   - DATABASE_URL support for PostgreSQL
   - Console-only logging (no file I/O)
   - Redis caching support via RAILWAY_REDIS_URL
   - Railway environment detection

### 3. **Updated requirements.txt**
   - All production dependencies included
   - Compatible with Railway environment
   - Includes django-redis for caching

### 4. **Dockerfile Already Configured**
   - Multi-stage build for optimization
   - Python 3.11 slim image
   - Non-root user for security
   - Gunicorn WSGI server

---

## 🎯 Step-by-Step Railway Deployment

### **Step 1: Push to GitHub**
Make sure all code is pushed:
```bash
cd "/Users/ankityadav/Downloads/pep projects/project2"
git add -A
git commit -m "feat: Add Railway deployment configuration"
git push origin main
```

### **Step 2: Create Railway Account**
1. Go to https://railway.app
2. Sign up (recommended: GitHub login)
3. Create new project

### **Step 3: Create Web Service**
1. Click "New" → "Project"
2. Select "Deploy from GitHub"
3. Choose your repository
4. Select branch: `main`
5. Railway will auto-detect Dockerfile

### **Step 4: Add PostgreSQL Database**
1. Click "Add" → "Database"
2. Select "PostgreSQL"
3. Railway automatically creates database
4. Connection string added as `DATABASE_URL` environment variable

### **Step 5: Configure Environment Variables**
In Railway dashboard, add:

```
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=*.railway.app
DJANGO_SETTINGS_MODULE=campus_project.settings_railway
PORT=8000
PYTHONUNBUFFERED=1
```

**Generate Strong SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### **Step 6: Deploy**
1. Click "Deploy"
2. Wait for build (5-15 minutes first time)
3. Once deployed, you get a URL like: `https://campus-management-prod.up.railway.app`

---

## ✅ Deployment Checklist

Before deploying:
- [ ] All code committed and pushed to GitHub
- [ ] `railway.yaml` present in root directory
- [ ] `settings_railway.py` created
- [ ] `Dockerfile` present
- [ ] `requirements.txt` updated
- [ ] `.env.example` file exists

After deployment:
- [ ] Web service shows "Active" status in Railway dashboard
- [ ] PostgreSQL database is provisioned
- [ ] No build errors in deployment logs
- [ ] Access app at provided Railway URL
- [ ] Admin panel loads at `/admin`

---

## 📊 Environment Variables Setup

### Required Variables:
```
DEBUG=False
SECRET_KEY=<generate-new>
ALLOWED_HOSTS=*.railway.app
DJANGO_SETTINGS_MODULE=campus_project.settings_railway
PORT=8000
PYTHONUNBUFFERED=1
```

### Optional Variables:
```
# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CORS settings
CORS_ALLOWED_ORIGINS=https://your-domain.railway.app

# Redis caching (if Redis service added)
RAILWAY_REDIS_URL=redis://...
```

---

## 🔍 Monitoring Deployment

### View Logs:
```bash
# Via Railway Dashboard:
# 1. Click on your service
# 2. Go to "Logs" tab
# 3. Real-time logs visible

# Via Railway CLI:
railway logs
```

### Common Issues & Solutions:

#### **Issue: Build fails with dependency error**
- ✅ **Solution:** Check `requirements.txt` has all packages
- ✅ Verify Python version in Dockerfile
- ✅ Rebuild: Railway dashboard → "Redeploy"

#### **Issue: "ModuleNotFoundError"**
- ✅ **Solution:** Ensure module is in an `__init__.py` package
- ✅ Check settings_railway.py is in correct location
- ✅ Verify DJANGO_SETTINGS_MODULE environment variable

#### **Issue: Database connection error**
- ✅ **Solution:** Verify DATABASE_URL is set
- ✅ Check PostgreSQL service is created
- ✅ Ensure database credentials are correct

#### **Issue: Static files not loading**
- ✅ **Solution:** Already handled by WhiteNoise
- ✅ Check STATIC_URL and STATIC_ROOT in settings
- ✅ Verify build step: `python manage.py collectstatic --noinput`

#### **Issue: Admin panel 500 error**
- ✅ **Solution:** Check logs for detailed error
- ✅ Run migrations: Railway Shell → `python manage.py migrate`
- ✅ Create superuser: Railway Shell → `python manage.py createsuperuser`

#### **Issue: Media files not persisting**
- ✅ **Solution:** Railway provides persistent disk at `/var/lib/railway`
- ✅ Update MEDIA_ROOT to use persistent path
- ✅ Or use external storage like AWS S3

---

## 🎛️ Scaling & Performance

### Current Setup:
- **Free Plan:** Limited resources (good for testing)
- **Pro Plan:** Better performance, custom domains, more storage

### Database:
- **PostgreSQL:** Automatically managed by Railway
- **Connection pooling:** Handled by Django settings

### Caching:
- **Default:** In-memory cache
- **Recommended:** Add Redis service for production

### Static Files:
- **WhiteNoise:** Serves static files from application
- **CDN:** Can add later for global distribution

---

## 🔐 Security Notes

### Before Going Live:
1. ✅ Change `SECRET_KEY` to strong random value
2. ✅ Set `DEBUG=False`
3. ✅ Set correct `ALLOWED_HOSTS`
4. ✅ Use HTTPS (Railway provides automatic SSL)
5. ✅ Set strong database password

### After Deployment:
1. ✅ Create superuser via Railway Shell:
   ```bash
   python manage.py createsuperuser
   ```

2. ✅ Test admin panel:
   ```
   https://your-app.railway.app/admin
   ```

3. ✅ Test all features
4. ✅ Monitor logs for errors

---

## 📊 Project Structure for Railway

```
project2/
├── railway.yaml                    ✅ Railway config
├── Dockerfile                      ✅ Container config
├── build.sh                        ✅ Build script
├── requirements.txt                ✅ Dependencies
├── manage.py                       ✅ Django management
├── campus_project/
│   ├── settings.py                ✅ Base settings
│   ├── settings_railway.py        ✅ Railway settings
│   ├── wsgi.py                    ✅ WSGI application
│   └── urls.py                    ✅ URL routing
├── apps/                          ✅ All apps configured
├── templates/                     ✅ HTML templates
├── static/                        ✅ Static files
└── media/                         ✅ Media files
```

---

## 🚀 Quick Deploy with Railway CLI

If you prefer command-line deployment:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Deploy
railway up

# View logs
railway logs

# Set environment variables
railway variables set DEBUG=False
railway variables set SECRET_KEY=your-key-here
```

---

## 📞 Helpful Resources

- **Railway Docs:** https://docs.railway.app
- **Django Deployment:** https://docs.djangoproject.com/en/4.2/howto/deployment/
- **PostgreSQL:** https://www.postgresql.org/docs/
- **Docker:** https://docs.docker.com/
- **Gunicorn:** https://docs.gunicorn.org/

---

## ✨ Features Supported on Railway

✅ Full Django application
✅ PostgreSQL database (auto-provisioned)
✅ Static file serving (via WhiteNoise)
✅ Media file uploads (persistent disk)
✅ Email sending (via SMTP)
✅ Environment variables
✅ SSL/HTTPS (automatic)
✅ Custom domain support
✅ Real-time logs
✅ Automatic deployments from GitHub
✅ Redis caching (add as service)

---

## 📈 After Deployment

### 1. Create Admin Account:
```bash
# Via Railway Shell
python manage.py createsuperuser
```

### 2. Run Migrations (if needed):
```bash
# Via Railway Shell
python manage.py migrate
```

### 3. Create Test Data:
- Use admin panel at `/admin`
- Add users, students, courses, food items

### 4. Test Features:
- User registration: `/users/register`
- Attendance: `/attendance/`
- Food ordering: `/food/`
- Admin panel: `/admin`

### 5. Monitor Performance:
- Check Railway dashboard logs
- Monitor database usage
- Watch for errors or performance issues

---

## 🔄 Continuous Deployment

Railway automatically deploys on GitHub push:
1. Push code to GitHub main branch
2. Railway detects the push
3. Automatic build starts
4. Service redeploys with new code
5. Zero downtime deployment

---

## 💡 Tips & Tricks

### Viewing Environment Variables:
```bash
railway variables list
```

### Running One-Off Commands:
```bash
railway shell
python manage.py createsuperuser
# or
python manage.py shell
```

### Downloading Database Backup:
```bash
railway db backup
```

### Custom Domain:
1. Railway Dashboard → Settings
2. Add custom domain
3. Update DNS records
4. SSL certificate auto-provisioned

---

**Your project is now ready for Railway deployment! 🎉**

For detailed issues or questions, refer to Railway's documentation or check the logs in your Railway dashboard.
