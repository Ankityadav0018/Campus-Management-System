# 🚀 Deployment Checklist & Guide

**Generated:** March 17, 2026  
**Project:** Campus Management System with AI Face Recognition

---

## ✅ Pre-Deployment Verification

### 1. **Environment Setup**
- [ ] Create `.env` file (copy from `.env.example`)
- [ ] Set `DEBUG=False` in production
- [ ] Generate a strong `SECRET_KEY` using:
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
- [ ] Set correct `ALLOWED_HOSTS` for your domain
- [ ] Configure database credentials

### 2. **Dependencies**
- [ ] Run `pip install -r requirements.txt`
- [ ] Verify all packages are installed:
  ```bash
  pip freeze > installed-packages.txt
  ```

### 3. **Database Setup**
- [ ] Set up PostgreSQL (recommended for production)
- [ ] Update `DB_ENGINE=postgresql` in `.env`
- [ ] Run migrations:
  ```bash
  python manage.py migrate
  ```
- [ ] Create superuser:
  ```bash
  python manage.py createsuperuser
  ```

### 4. **Static Files**
- [ ] Collect static files:
  ```bash
  python manage.py collectstatic --noinput
  ```
- [ ] Verify `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- [ ] For production, consider using AWS S3 or CloudFront

### 5. **Media Files**
- [ ] Create media directories:
  ```bash
  mkdir -p media/food_items media/temp
  ```
- [ ] Set proper permissions on media folders
- [ ] Consider cloud storage for production (AWS S3, Azure Blob)

### 6. **Security Checks**
- [ ] Change `SECRET_KEY` from default
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable HTTPS/SSL certificate
- [ ] Set `SECURE_SSL_REDIRECT=True`
- [ ] Run Django security check:
  ```bash
  python manage.py check --deploy
  ```

### 7. **Application Checks**
- [ ] Run system checks:
  ```bash
  python manage.py check
  ```
- [ ] Test all URLs:
  ```bash
  python manage.py test
  ```
- [ ] Verify face recognition modules (requires camera/images)
- [ ] Test email configuration

### 8. **Logging & Monitoring**
- [ ] Verify logs directory exists: `mkdir -p logs`
- [ ] Check log file permissions
- [ ] Set up log rotation
- [ ] Configure error tracking (Sentry recommended)

---

## 📦 Deployment Options

### **Option 1: Docker (Recommended)**

**Prerequisites:**
- Docker installed
- Docker Compose installed

**Steps:**
```bash
# 1. Create .env file with your configuration
cp .env.example .env
# Edit .env with your settings

# 2. Build and run with docker-compose
docker-compose up -d

# 3. Run migrations
docker-compose exec web python manage.py migrate

# 4. Create superuser
docker-compose exec web python manage.py createsuperuser

# 5. Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

**Verify:**
- Application running on `http://localhost:8000`
- PostgreSQL running on `localhost:5432`
- Redis running on `localhost:6379`

---

### **Option 2: Heroku**

**Prerequisites:**
- Heroku CLI installed
- Heroku account

**Steps:**
```bash
# 1. Login to Heroku
heroku login

# 2. Create Heroku app
heroku create your-app-name

# 3. Set environment variables
heroku config:set DEBUG=False
heroku config:set SECRET_KEY='your-secret-key'
heroku config:set ALLOWED_HOSTS='your-app-name.herokuapp.com'
heroku config:set DB_ENGINE=postgresql

# 4. Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# 5. Deploy
git push heroku main

# 6. Run migrations
heroku run python manage.py migrate

# 7. Create superuser
heroku run python manage.py createsuperuser
```

**Verify:**
- Application running on `https://your-app-name.herokuapp.com`
- Check logs: `heroku logs --tail`

---

### **Option 3: AWS (EC2 + RDS)**

**Prerequisites:**
- AWS account
- EC2 instance running (Ubuntu 20.04 or later)
- RDS PostgreSQL instance

**Steps:**

1. **SSH into EC2 instance:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-ip
   ```

2. **Update system:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-pip python3-venv nginx supervisor postgresql-client
   ```

3. **Clone repository:**
   ```bash
   git clone https://github.com/your-repo.git
   cd project2
   ```

4. **Setup virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Configure environment:**
   ```bash
   cat > .env << 'EOL'
   DEBUG=False
   SECRET_KEY='your-secret-key'
   ALLOWED_HOSTS='your-domain.com,www.your-domain.com'
   DB_ENGINE=postgresql
   DB_NAME=campus_db
   DB_USER=dbuser
   DB_PASSWORD=dbpassword
   DB_HOST=your-rds-endpoint.rds.amazonaws.com
   DB_PORT=5432
   EOL
   ```

6. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

7. **Configure Gunicorn:**
   ```bash
   cat > /etc/supervisor/conf.d/campus.conf << 'EOL'
   [program:campus]
   directory=/home/ec2-user/project2
   command=/home/ec2-user/project2/venv/bin/gunicorn campus_project.wsgi:application --bind 127.0.0.1:8000 --workers 4
   autostart=true
   autorestart=true
   redirect_stderr=true
   stdout_logfile=/var/log/campus.log
   EOL
   ```

8. **Configure Nginx:**
   ```bash
   cat > /etc/nginx/sites-available/campus << 'EOL'
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           alias /home/ec2-user/project2/staticfiles/;
       }

       location /media/ {
           alias /home/ec2-user/project2/media/;
       }

       location / {
           include proxy_params;
           proxy_pass http://127.0.0.1:8000;
       }
   }
   EOL
   ```

9. **Enable and start services:**
   ```bash
   sudo systemctl enable supervisor
   sudo systemctl start supervisor
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

10. **Setup SSL with Let's Encrypt:**
    ```bash
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d your-domain.com -d www.your-domain.com
    ```

---

### **Option 4: DigitalOcean (Similar to AWS)**

**Prerequisites:**
- DigitalOcean account
- Droplet created (Ubuntu 20.04 or later)

**Follow AWS steps above** (EC2 and RDS sections are similar)

---

## 🔍 Post-Deployment Verification

### Health Checks

```bash
# 1. Check application is running
curl https://your-domain.com

# 2. Check admin panel
curl https://your-domain.com/admin

# 3. Check database connection
python manage.py dbshell

# 4. Verify static files are served
curl https://your-domain.com/static/style.css

# 5. Check logs
tail -f logs/django.log
```

### Performance Checks

```bash
# 1. Run Django checks
python manage.py check --deploy

# 2. Check query performance
python manage.py runserver --nothreading

# 3. Monitor logs
tail -f logs/django.log
```

### Security Checks

```bash
# 1. SSL/TLS verification
ssl-test https://your-domain.com

# 2. Security headers check
curl -I https://your-domain.com

# 3. Django security check
python manage.py check --deploy

# 4. Run vulnerability scanner
safety check
```

---

## 📊 Monitoring & Maintenance

### Daily Tasks
- [ ] Check error logs: `tail logs/django.log`
- [ ] Monitor database size
- [ ] Verify backup jobs running

### Weekly Tasks
- [ ] Review user activity logs
- [ ] Check disk space usage
- [ ] Verify SSL certificate validity

### Monthly Tasks
- [ ] Database optimization
- [ ] Performance analysis
- [ ] Security updates
- [ ] Backup verification

### Tools to Install
```bash
# Error tracking
pip install sentry-sdk

# Performance monitoring
pip install django-debug-toolbar

# API monitoring
pip install django-extensions

# Database monitoring
pip install django-db-multitenant
```

---

## 🚨 Common Issues & Solutions

### **Issue: DEBUG=True in production**
**Solution:**
```bash
# In .env
DEBUG=False

# Restart application
```

### **Issue: Static files not loading**
**Solution:**
```bash
# Collect static files
python manage.py collectstatic --clear --noinput

# Check STATIC_ROOT in settings.py
```

### **Issue: Database connection errors**
**Solution:**
```bash
# Verify database credentials in .env
# Test connection
python manage.py dbshell

# Check PostgreSQL is running
sudo systemctl status postgresql
```

### **Issue: Media files not uploading**
**Solution:**
```bash
# Check permissions
chmod -R 755 media/

# Verify MEDIA_ROOT setting
```

### **Issue: Face recognition not working**
**Solution:**
```bash
# Verify camera/image permissions
# Check face_encoding models are loaded
# Verify PIL/OpenCV installations
pip install --upgrade opencv-python pillow

# Test camera access
python -c "import cv2; print(cv2.__version__)"
```

---

## 📋 Final Checklist Before Going Live

- [ ] All environment variables configured
- [ ] DEBUG = False
- [ ] SECRET_KEY is strong and unique
- [ ] ALLOWED_HOSTS configured correctly
- [ ] Database migrations run
- [ ] Superuser created
- [ ] Static files collected
- [ ] SSL certificate installed
- [ ] HTTPS redirect enabled
- [ ] Email configured
- [ ] Logging configured
- [ ] Backups automated
- [ ] Monitoring enabled
- [ ] Error tracking setup
- [ ] Security check passed
- [ ] Performance tested
- [ ] All apps tested
- [ ] Face recognition tested
- [ ] Documentation updated
- [ ] Team notified

---

## 📞 Support & Resources

- Django Documentation: https://docs.djangoproject.com/
- Gunicorn Documentation: https://docs.gunicorn.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Docker Documentation: https://docs.docker.com/
- AWS Documentation: https://docs.aws.amazon.com/
- Heroku Documentation: https://devcenter.heroku.com/

---

**Last Updated:** March 17, 2026
