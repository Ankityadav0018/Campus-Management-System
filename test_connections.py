#!/usr/bin/env python
"""
Comprehensive Connection Test Script
Tests all database connections, models, and configurations
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_project.settings')
django.setup()

from django.db import connection
from django.core.exceptions import ImproperlyConfigured
from apps.users.models import User
from apps.attendance.models import Student, Attendance, StudentFace
from apps.food.models import FoodStall, FoodItem, FoodOrder
from apps.resources.models import CampusFaculty, Course, CampusClassroom
from apps.remedial.models import RemedialClass

def test_database_connection():
    """Test database connection"""
    print("\n1️⃣  Testing Database Connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("   ✅ Database connection successful")
            return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_models():
    """Test all models can be queried"""
    print("\n2️⃣  Testing Models...")
    models = {
        'User': User,
        'Student': Student,
        'Attendance': Attendance,
        'StudentFace': StudentFace,
        'FoodStall': FoodStall,
        'FoodItem': FoodItem,
        'FoodOrder': FoodOrder,
        'CampusFaculty': CampusFaculty,
        'Course': Course,
        'CampusClassroom': CampusClassroom,
        'RemedialClass': RemedialClass,
    }
    
    all_good = True
    for name, model in models.items():
        try:
            count = model.objects.count()
            print(f"   ✅ {name}: {count} records")
        except Exception as e:
            print(f"   ❌ {name}: Error - {e}")
            all_good = False
    
    return all_good

def test_relationships():
    """Test model relationships"""
    print("\n3️⃣  Testing Model Relationships...")
    try:
        # Test User relationships
        if User.objects.exists():
            user = User.objects.first()
            print(f"   ✅ User model accessible: {user.email}")
        
        # Test Student-Attendance relationship
        if Student.objects.exists():
            student = Student.objects.first()
            attendance_count = student.attendance_set.count()
            print(f"   ✅ Student-Attendance relationship: {attendance_count} records")
        
        # Test FoodStall-FoodItem relationship
        if FoodStall.objects.exists():
            stall = FoodStall.objects.first()
            items_count = stall.items.count()
            print(f"   ✅ FoodStall-FoodItem relationship: {items_count} items")
        
        return True
    except Exception as e:
        print(f"   ❌ Relationship test failed: {e}")
        return False

def test_database_integrity():
    """Test database integrity"""
    print("\n4️⃣  Testing Database Integrity...")
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('check', '--database', 'default', stdout=out)
        print("   ✅ Database integrity check passed")
        return True
    except Exception as e:
        print(f"   ❌ Database integrity check failed: {e}")
        return False

def test_migrations():
    """Check migration status"""
    print("\n5️⃣  Checking Migrations...")
    try:
        from django.db.migrations.executor import MigrationExecutor
        
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        
        if plan:
            print(f"   ⚠️  Unapplied migrations found: {len(plan)}")
            return False
        else:
            print("   ✅ All migrations applied")
            return True
    except Exception as e:
        print(f"   ❌ Migration check failed: {e}")
        return False

def test_url_patterns():
    """Test URL configuration"""
    print("\n6️⃣  Testing URL Patterns...")
    try:
        from django.urls import get_resolver
        
        resolver = get_resolver()
        url_patterns = list(resolver.url_patterns)
        print(f"   ✅ URL patterns loaded: {len(url_patterns)} top-level patterns")
        
        # Test specific app URLs
        apps = ['users', 'attendance', 'food', 'resources', 'remedial']
        for app in apps:
            try:
                from django.urls import reverse
                # Try to reverse a URL from each app
                if app == 'users':
                    reverse(f'{app}:login')
                elif app == 'attendance':
                    reverse(f'{app}:attendance_home')
                elif app == 'food':
                    reverse(f'{app}:food_ordering_home')
                elif app == 'resources':
                    reverse(f'{app}:resources_home')
                elif app == 'remedial':
                    reverse(f'{app}:remedial_home')
                print(f"   ✅ {app} URLs configured correctly")
            except Exception as e:
                print(f"   ⚠️  {app} URL issue: {e}")
        
        return True
    except Exception as e:
        print(f"   ❌ URL pattern test failed: {e}")
        return False

def test_static_files():
    """Test static files configuration"""
    print("\n7️⃣  Testing Static Files...")
    try:
        from django.conf import settings
        
        static_url = settings.STATIC_URL
        static_root = settings.STATIC_ROOT
        media_url = settings.MEDIA_URL
        media_root = settings.MEDIA_ROOT
        
        print(f"   ✅ STATIC_URL: {static_url}")
        print(f"   ✅ STATIC_ROOT: {static_root}")
        print(f"   ✅ MEDIA_URL: {media_url}")
        print(f"   ✅ MEDIA_ROOT: {media_root}")
        
        # Check if directories exist
        if not os.path.exists(media_root):
            os.makedirs(media_root)
            print(f"   �� Created MEDIA_ROOT directory")
        
        return True
    except Exception as e:
        print(f"   ❌ Static files test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🔍 CAMPUS MANAGEMENT SYSTEM - CONNECTION TESTS")
    print("=" * 60)
    
    results = {
        'Database Connection': test_database_connection(),
        'Models': test_models(),
        'Relationships': test_relationships(),
        'Database Integrity': test_database_integrity(),
        'Migrations': test_migrations(),
        'URL Patterns': test_url_patterns(),
        'Static Files': test_static_files(),
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All connections are working perfectly!")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
