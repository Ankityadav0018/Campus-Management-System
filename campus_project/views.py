from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    # Redirect unauthenticated users to login page
    if not request.user.is_authenticated:
        return redirect('users:login')
    
    # Redirect authenticated users to their role-specific dashboards
    if request.user.role == 'student':
        return redirect('users:student_home')
    elif request.user.role == 'faculty':
        return redirect('users:faculty_home')
    
    # Admin or other roles will see the general home page
    return render(request, 'home.html')
