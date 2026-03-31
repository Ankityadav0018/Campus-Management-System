# ⚡ Render Quick Start (5 Minutes)

## ✅ Your Project is Render-Ready!

All necessary files have been created:
- ✅ `render.yaml` - Render configuration
- ✅ `build.sh` - Build script
- ✅ `settings_render.py` - Render-specific settings
- ✅ `requirements.txt` - Updated dependencies
- ✅ `.env.render` - Environment variable template

---

## 🚀 Deploy in 5 Steps

### **Step 1: Push to GitHub** (1 min)
```bash
cd "/Users/ankityadav/Downloads/pep projects/project2"
git add -A
git commit -m "feat: Add Render deployment configuration"
git push origin main
```

### **Step 2: Create Render Account** (1 min)
- Go to https://render.com
- Sign up with GitHub
- Grant repository access

### **Step 3: Create Web Service** (1 min)
1. Click "New +" → "Web Service"
2. Select your GitHub repository
3. Select `main` branch
4. Click "Create Web Service"

### **Step 4: Configure Environment** (1 min)
In Render dashboard, add these variables:

```
DEBUG=False
SECRET_KEY=<generate-new-key>
ALLOWED_HOSTS=your-app-name.onrender.com
RENDER=True
```

**Generate SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### **Step 5: Create Database** (1 min)
1. Click "New +" → "PostgreSQL"
2. Name: `campus-db`
3. Create database
4. Copy connection string
5. Add to web service as `DATABASE_URL` environment variable

---

## 📊 What Happens Next

1. **Build starts** (3-5 min)
   - Dependencies installed
   - Static files collected
   - Database migrations run

2. **Service deploys** 
   - Your app goes live
   - You get a URL: `https://your-app-name.onrender.com`

3. **Ready to use**
   - Access app at provided URL
   - Admin panel at `/admin`
   - Create superuser via Render Shell

---

## 🎛️ After Deployment

### Create Admin Account:
```bash
# Via Render Dashboard → Shell
python manage.py createsuperuser
```

### Access Your App:
```
https://your-app-name.onrender.com
Admin: https://your-app-name.onrender.com/admin
```

### Test Features:
- User registration: `/users/register`
- Attendance: `/attendance/`
- Food ordering: `/food/`
- Admin panel: `/admin`

---

## ⚠️ Important Notes

1. **Free Plan Limitations:**
   - Web service spins down after 15 min of inactivity
   - Database limited to 256 MB
   - Upgrade to paid plan for production

2. **Data Persistence:**
   - Database: ✅ Persistent (PostgreSQL)
   - Media files: ✅ Persistent (persistent disk)
   - Logs: ❌ Not persistent (console only)
   - Temp files: ❌ Deleted on restart

3. **Static Files:**
   - Automatically served by WhiteNoise
   - No CDN needed for development

---

## 🔗 Links

- Your App: `https://your-app-name.onrender.com`
- Admin: `https://your-app-name.onrender.com/admin`
- Render Dashboard: https://dashboard.render.com
- Logs: View in Render dashboard (real-time)

---

## 📞 Troubleshooting

**Build failing?**
- Check Render logs in dashboard
- Ensure `build.sh` is executable
- Verify `requirements.txt` has all packages

**Database connection error?**
- Check `DATABASE_URL` is set
- Verify PostgreSQL service is running
- Make sure database is linked to web service

**Static files not loading?**
- Rebuild service in Render dashboard
- Check STATIC_URL and STATIC_ROOT in settings

**App sleeping?**
- Upgrade to paid plan to prevent inactivity shutdown
- Free plan sleeps after 15 min of inactivity

---

**That's it! Your app should be live in about 10-15 minutes! 🎉**

For detailed info, see `RENDER_DEPLOYMENT_GUIDE.md`
