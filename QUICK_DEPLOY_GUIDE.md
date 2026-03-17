# ⚡ QUICK DEPLOYMENT GUIDE (5 Minutes)

## 🟢 What's Ready Now
✅ Docker setup complete
✅ Environment template created
✅ Production settings configured
✅ All dependencies updated
✅ Documentation complete

---

## 🚀 FASTEST DEPLOYMENT (Choose One)

### **Method 1: Docker (Recommended for Beginners)**

```bash
# Step 1: Configure environment
cd "/Users/ankityadav/Downloads/pep projects/project2"
cp .env.example .env

# Edit .env and set:
# - SECRET_KEY (generate new one)
# - DB_PASSWORD (set strong password)
# - ALLOWED_HOSTS (your domain)
nano .env

# Step 2: Start services
docker-compose up -d

# Step 3: Initialize database
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# Step 4: Done! Access at http://localhost:8000
```

**Verify:**
```bash
# Check running services
docker-compose ps

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

---

### **Method 2: Heroku (Fastest Cloud Deployment)**

**Prerequisites:** Install Heroku CLI

```bash
# Step 1: Login to Heroku
heroku login

# Step 2: Create app
heroku create your-app-name

# Step 3: Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"

# Step 4: Deploy
git push heroku main

# Step 5: Run migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser

# Step 6: Open app
heroku open
```

---

### **Method 3: Traditional Server (Ubuntu/DigitalOcean)**

```bash
# Step 1: SSH into server
ssh root@your-server-ip

# Step 2: Install dependencies
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv postgresql nginx supervisor

# Step 3: Clone and setup
cd /home
git clone https://github.com/your-repo.git
cd project2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Step 4: Configure .env
nano .env
# Set database and other variables

# Step 5: Setup database
sudo -u postgres createdb campus_db
sudo -u postgres createuser dbuser
# Run migrations
python manage.py migrate

# Step 6: Collect static files
python manage.py collectstatic --noinput

# Step 7: Configure Gunicorn (see DEPLOYMENT_CHECKLIST.md)
# Configure Nginx (see DEPLOYMENT_CHECKLIST.md)

# Step 8: Start services
sudo systemctl restart supervisor
sudo systemctl restart nginx
```

---

## 🔑 Critical Before Deploying

| Item | Action | Command |
|------|--------|---------|
| **SECRET_KEY** | Generate new one | `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'` |
| **DEBUG** | Set to False | In `.env`: `DEBUG=False` |
| **Database** | Use PostgreSQL | `DB_ENGINE=postgresql` in `.env` |
| **ALLOWED_HOSTS** | Set domain(s) | In `.env`: `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com` |
| **SSL/HTTPS** | Enable certificate | Use Let's Encrypt (free) |

---

## ✅ Deployment Checklist (Final)

- [ ] `.env` file created and configured
- [ ] `DEBUG=False`
- [ ] New `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` set correctly
- [ ] Database configured (PostgreSQL for production)
- [ ] `python manage.py check --deploy` passes
- [ ] SSL certificate installed (for HTTPS)
- [ ] Email configured
- [ ] Backups automated
- [ ] Monitoring setup

---

## 🧪 Test Your Deployment

After deploying, test these:

```bash
# Test 1: Access main page
curl https://your-domain.com

# Test 2: Check admin panel
curl https://your-domain.com/admin

# Test 3: Verify static files
curl https://your-domain.com/static/style.css

# Test 4: Check database
curl https://your-domain.com/api/health  # If you have health check

# Test 5: View logs
tail -f logs/django.log
```

---

## 🆘 Troubleshooting

### Problem: Static files not loading
```bash
# Solution: Collect static files
python manage.py collectstatic --clear --noinput
```

### Problem: Database connection error
```bash
# Solution: Verify credentials
python manage.py dbshell

# Check env variables
echo $DB_NAME $DB_USER $DB_HOST
```

### Problem: Face recognition not working
```bash
# Solution: Verify OpenCV installation
python -c "import cv2; print(cv2.__version__)"

# Reinstall if needed
pip install --upgrade opencv-python pillow
```

### Problem: Port already in use (Docker)
```bash
# Solution: Use different port
docker-compose -f docker-compose.yml up -d -e PORT=9000

# Or check what's using port 8000
lsof -i :8000
```

---

## 📊 Deployment Comparison

| Platform | Setup Time | Cost | Ease | Best For |
|----------|-----------|------|------|----------|
| **Docker** | 5-10 min | Flexible | Easy | Beginners |
| **Heroku** | 5-15 min | $7-50/mo | Very Easy | Quick launch |
| **AWS EC2** | 20-30 min | $5-50/mo | Moderate | Full control |
| **DigitalOcean** | 15-25 min | $4-12/mo | Easy | Best value |

---

## 📞 Need Help?

1. **Check DEPLOYMENT_CHECKLIST.md** - Detailed step-by-step guide
2. **Check DEPLOYMENT_SUMMARY.md** - Overall status and requirements
3. **Django Docs** - https://docs.djangoproject.com/en/4.2/howto/deployment/

---

## 🎯 Production Settings Summary

**Updated in `settings.py`:**
- ✅ Environment variable support
- ✅ PostgreSQL support
- ✅ Redis caching option
- ✅ Security headers
- ✅ WhiteNoise static files
- ✅ Email configuration
- ✅ CORS support

**In `requirements.txt`:**
- ✅ `gunicorn` - Production server
- ✅ `psycopg2-binary` - PostgreSQL driver
- ✅ `python-decouple` - Environment management
- ✅ `whitenoise` - Static file serving
- ✅ `django-cors-headers` - CORS support

---

**Ready to deploy? Choose Docker or Heroku and follow the steps above!**

Last Updated: March 17, 2026
