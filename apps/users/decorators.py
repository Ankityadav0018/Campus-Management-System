from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator to restrict access based on user role
    Usage: @role_required(['faculty', 'admin'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Please log in to access this page.")
                return redirect('users:login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, f"Access denied. This page is only for {', '.join(allowed_roles)}.")
                # Redirect to user's appropriate dashboard
                if request.user.role == 'student':
                    return redirect('users:student_home')
                elif request.user.role == 'faculty':
                    return redirect('users:faculty_home')
                elif request.user.role == 'vendor':
                    return redirect('users:vendor_home')
                else:
                    return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def student_required(view_func):
    """Decorator for student-only views"""
    return role_required(['student'])(view_func)

def faculty_required(view_func):
    """Decorator for faculty-only views"""
    return role_required(['faculty', 'admin'])(view_func)

def vendor_required(view_func):
    """Decorator for vendor-only views"""
    return role_required(['vendor', 'admin'])(view_func)
