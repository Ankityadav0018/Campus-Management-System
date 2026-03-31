# ✅ Railway Deployment - Complete Checklist

**Last Updated:** March 31, 2026  
**Status:** ✅ READY FOR DEPLOYMENT

---

## 🔍 Pre-Deployment Verification

### Configuration Files Check
- [x] **Dockerfile** - ✅ Updated with dynamic PORT support
  - Uses `${PORT:-8000}` for Railway environment variable
  - Non-root user for security
  - Static files collected in build
  
- [x] **railway.yaml** - ✅ Present and configured
  - Web service configuration
  - PostgreSQL database defined
  - Health check configured
  
- [x] **settings.py** - ✅ Production-ready
  - Environment variable support via `decouple`
  - Database URL support
  - Security headers configured
  
- [x] **settings_railway.py** - ✅ Present
  - Railway-specific database configuration
  - Console logging (handles ephemeral filesystem)
  - Redis caching support

- [x] **requirements.txt** - ✅ All dependencies included
  - Django 4.2.0
  - Gunicorn for WSGI server
  - psycopg2-binary for PostgreSQL
  - WhiteNoise for static files
  - dj-database-url for DATABASE_URL parsing
  - django-redis for caching

- [x] **build.sh** - ✅ Build script present
  - Installs dependencies
  - Collects static files
  - Runs migrations

- [x] **.env.railway** - ✅ Environment template present

---

## 🚨 Critical Configuration Items

### Must Set in Railway Dashboard

#### 1. **Environment Variables**
```
DEBUG=False                                    ✅ REQUIRED - No debug in production
SECRET_KEY=<generate-strong-key>              ✅ REQUIRED - Use Django generator
ALLOWED_HOSTS=*.railway.app,yourdomain.com    ✅ REQUIRED - Restrict hosts
DJANGO_SETTINGS_MODULE=campus_project.settings ✅ REQUIRED - Use base settings
PORT=8000                                      ✅ OPTIONAL - Railway sets this
PYTHONUNBUFFERED=1                            ✅ REQUIRED - For proper logging
```

#### 2. **Database Configuration**
- [ ] PostgreSQL service created in Railway
- [ ] `DATABASE_URL` auto-populated by Railway
- [ ] Database credentials verified

#### 3. **Security Settings**
- [ ] `SECRET_KEY` generated and set (min 50 characters)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured for your domain
- [ ] HTTPS enabled (automatic on Railway)

---

## 📋 Step-by-Step Deployment Guide

### **Step 1: Prepare Repository** ✅ DONE
```bash
cd "/Users/ankityadav/Downloads/pep projects/project2"
git add -A
git commit -m "fix: Update Dockerfile with dynamic PORT support for Railway"
git push origin main
```

### **Step 2: Create Railway Account** (2 min)
- [ ] Go to https://railway.app
- [ ] Click "Start a New Project"
- [ ] Sign up with GitHub account
- [ ] Authorize Railway to access GitHub repositories

### **Step 3: Create New Project** (1 min)
1. [ ] Click "New Project"
2. [ ] Select "Deploy from GitHub repo"
3. [ ] Search for: `Campus-Management-System`
4. [ ] Select your repository
5. [ ] Choose branch: `main`
6. [ ] Click "Deploy"

### **Step 4: Configure Build & Deployment** (2 min)
In Railway Dashboard → Service Settings:
- [ ] **Build Command:** `bash build.sh`
- [ ] **Start Command:** `gunicorn campus_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120`
- [ ] **Dockerfile:** Select `Dockerfile`

### **Step 5: Add PostgreSQL Database** (2 min)
1. [ ] Click "+ Add Service"
2. [ ] Select "Database"
3. [ ] Choose "PostgreSQL"
4. [ ] Railway auto-creates database
5. [ ] `DATABASE_URL` automatically set in environment

### **Step 6: Set Environment Variables** (3 min)
In Railway Dashboard → Environment Variables:

**Required Variables:**
```
DEBUG=False
SECRET_KEY=django-insecure-generated-key-here-50-chars-min
ALLOWED_HOSTS=*.railway.app,your-domain.com
DJANGO_SETTINGS_MODULE=campus_project.settings
PORT=8000
PYTHONUNBUFFERED=1
```

**Optional Variables:**
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
CORS_ALLOWED_ORIGINS=https://your-domain.railway.app
```

### **Step 7: Deploy Application** (5-15 min)
1. [ ] Click "Deploy" button
2. [ ] Watch build logs in Dashboard
3. [ ] Wait for "Deployment Successful" message
4. [ ] Application will be live at provided URL

### **Step 8: Post-Deployment Verification** (5 min)
1. [ ] Access app at provided Railway URL
2. [ ] Check homepage loads (`/`)
3. [ ] Check admin panel loads (`/admin`)
4. [ ] Verify static files load (CSS/JS)
5. [ ] Check logs for errors (Logs tab)

---

## 🔐 Security Configuration

### Before Going Live - CRITICAL

| Item | Action | Priority |
|------|--------|----------|
| **SECRET_KEY** | Generate new strong key | 🔴 CRITICAL |
| **DEBUG** | Set to `False` | 🔴 CRITICAL |
| **ALLOWED_HOSTS** | Set to your domain | 🔴 CRITICAL |
| **Database Password** | Use strong password | 🔴 CRITICAL |
| **HTTPS** | Enabled automatically | ✅ Auto |
| **HSTS Headers** | Enabled in settings | ✅ Configured |

### Generate Strong SECRET_KEY
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Security Headers (Already Configured)
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 📊 Deployment Flow Diagram

```
1. GitHub Push
       ↓
2. Railway Detects Change
       ↓
3. Build Process Starts
   - Install requirements.txt
   - Run build.sh
   - Collect static files
   - Run migrations
       ↓
4. Docker Image Created
       ↓
5. Container Deployed
       ↓
6. Gunicorn Starts with PORT
       ↓
7. PostgreSQL Connected
       ↓
8. Application LIVE ✅
```

---

## 🧪 Testing After Deployment

### Immediate Tests (After Deploy)
- [ ] Access homepage: `https://your-app.railway.app/`
- [ ] Homepage loads without errors
- [ ] Static files load (CSS, JS present)
- [ ] Check browser console for errors

### Admin Panel Tests
- [ ] Admin panel loads: `https://your-app.railway.app/admin`
- [ ] Login page displays
- [ ] Create superuser (via Railway Shell)

### Feature Tests
- [ ] User registration page loads: `/users/register`
- [ ] Attendance module loads: `/attendance/`
- [ ] Food ordering page loads: `/food/`
- [ ] Resources page loads: `/resources/`

### Database Tests
- [ ] Migrations ran successfully (check logs)
- [ ] Database connection working (no errors in logs)
- [ ] Can access admin panel (indicates DB is connected)

### Performance Tests
- [ ] Page load times are acceptable
- [ ] No 500 errors in logs
- [ ] Static files served quickly

---

## 🆘 Troubleshooting Common Issues

### Issue: Build Fails with "Command not found"
**Cause:** Dockerfile not found or path incorrect
**Solution:**
- [ ] Verify Dockerfile exists in root directory
- [ ] Check build command points to correct file
- [ ] Redeploy from Railway dashboard

### Issue: "ModuleNotFoundError: No module named 'django'"
**Cause:** Dependencies not installed
**Solution:**
- [ ] Check requirements.txt is present
- [ ] Verify build command is: `bash build.sh`
- [ ] Rebuild service

### Issue: Database Connection Error
**Cause:** DATABASE_URL not set or PostgreSQL not created
**Solution:**
- [ ] Create PostgreSQL service in Railway
- [ ] Verify DATABASE_URL appears in environment variables
- [ ] Check database service is "Running" status
- [ ] View logs for connection details

### Issue: Static Files Not Loading (404 errors)
**Cause:** Static files not collected
**Solution:**
- [ ] Check build.sh includes `python manage.py collectstatic --noinput`
- [ ] Verify STATIC_ROOT is set correctly
- [ ] Check WhiteNoise middleware is enabled
- [ ] Rebuild and redeploy

### Issue: Application Crashes After Deploy
**Cause:** Environment variables not set
**Solution:**
- [ ] Check all required variables are set
- [ ] Verify SECRET_KEY is set correctly
- [ ] Check ALLOWED_HOSTS includes railway URL
- [ ] View logs for detailed error message

### Issue: "Port already in use" Error
**Cause:** Gunicorn using hardcoded port
**Solution:**
- [ ] Already fixed - Dockerfile uses `${PORT:-8000}`
- [ ] No action needed if using updated Dockerfile

---

## 📈 Monitoring After Deployment

### Railway Dashboard Monitoring
- [ ] Service Status - Check shows "Running"
- [ ] Logs - View real-time application logs
- [ ] Metrics - Monitor CPU, memory, network
- [ ] Deployments - See deployment history

### Check Logs Command
```bash
# Via Railway CLI
railway logs

# Via Dashboard
# Click service → Logs tab → Stream live logs
```

### Health Check URL
```
GET https://your-app.railway.app/admin
→ If loads, app is healthy
```

---

## 🔄 Continuous Deployment

### Auto-Deploy Setup
- [ ] Repository connected to Railway
- [ ] Main branch connected
- [ ] Auto-deploy enabled (Railway default)

### Deploy New Changes
1. [ ] Make code changes locally
2. [ ] Commit to Git: `git commit -m "message"`
3. [ ] Push to GitHub: `git push origin main`
4. [ ] Railway automatically starts deployment
5. [ ] Watch deployment progress in dashboard
6. [ ] App redeployment completes in 2-5 minutes

---

## 🛠️ Useful Railway Commands

### Via Railway CLI
```bash
# View logs
railway logs

# Set environment variable
railway variables set DEBUG=False

# View all variables
railway variables list

# Run shell command
railway shell

# Execute Python command
railway shell python manage.py createsuperuser

# Get database backup
railway db backup
```

### Via Dashboard
- View logs: Service → Logs
- Set variables: Service → Variables
- View metrics: Service → Metrics
- SSH into container: Service → Shell

---

## 📊 Production Checklist

### Before Launch
- [x] Dockerfile supports dynamic PORT
- [x] Settings configured for production
- [x] Database URL support added
- [x] Static files configuration correct
- [x] Logging configured for console
- [ ] SECRET_KEY generated and set
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS configured
- [ ] Email configured (if needed)
- [ ] Backups configured
- [ ] Monitoring alerts set up

### Day 1 After Launch
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Test all user flows
- [ ] Verify backups working
- [ ] Document any issues

### Weekly Tasks
- [ ] Review logs for errors
- [ ] Check database size
- [ ] Monitor performance
- [ ] Update dependencies if needed
- [ ] Test backup restoration

---

## 📞 Support & Resources

| Resource | Link |
|----------|------|
| Railway Documentation | https://docs.railway.app |
| Django Deployment | https://docs.djangoproject.com/en/4.2/howto/deployment/ |
| PostgreSQL Docs | https://www.postgresql.org/docs/ |
| Gunicorn Docs | https://docs.gunicorn.org/ |
| Railway Support | https://railway.app/support |

---

## ✅ Final Deployment Summary

**Project Status:** ✅ **100% Ready for Railway Deployment**

**Key Achievements:**
- ✅ Dockerfile updated with dynamic PORT support
- ✅ PostgreSQL database support
- ✅ Environment variable configuration
- ✅ Static files optimized with WhiteNoise
- ✅ Security headers configured
- ✅ Build script ready
- ✅ All documentation complete

**Estimated Time to Deploy:** 10-15 minutes
**Estimated Monthly Cost:** ~$5-10 (Railway free tier + PostgreSQL)

**Next Action:** Follow Step-by-Step Deployment Guide above

---

**Last Verified:** March 31, 2026  
**Ready for Production:** ✅ YES
