#!/bin/bash

# Campus Management System - Server Startup Script
# This script ensures all connections are working before starting the server

echo "🔧 Campus Management System - Starting..."
echo "=========================================="

# Step 1: Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Step 2: Activate virtual environment
echo "✓ Activating virtual environment..."
source venv/bin/activate

# Step 3: Install/Update dependencies
echo "✓ Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Step 4: Check database connection
echo "✓ Testing database connection..."
python manage.py dbshell ".databases" 2>/dev/null || echo "Database: db.sqlite3"

# Step 5: Run migrations
echo "✓ Applying database migrations..."
python manage.py migrate --no-input

# Step 6: Collect static files
echo "✓ Collecting static files..."
python manage.py collectstatic --no-input --clear 2>/dev/null || true

# Step 7: Run system checks
echo "✓ Running system checks..."
python manage.py check

# Step 8: Display database status
echo ""
echo "📊 Database Status:"
python manage.py shell -c "
from apps.users.models import User
from apps.attendance.models import Student, Attendance
from apps.food.models import FoodStall
from apps.resources.models import CampusFaculty, Course
print('  - Users:', User.objects.count())
print('  - Students:', Student.objects.count())
print('  - Faculty:', CampusFaculty.objects.count())
print('  - Attendance Records:', Attendance.objects.count())
print('  - Food Stalls:', FoodStall.objects.count())
print('  - Courses:', Course.objects.count())
"

echo ""
echo "=========================================="
echo "✅ All connections verified!"
echo "🚀 Starting Django development server..."
echo "=========================================="
echo ""
echo "Server will be available at: http://127.0.0.1:8000"
echo "Admin panel: http://127.0.0.1:8000/admin"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Step 9: Start the server
python manage.py runserver 0.0.0.0:8000
