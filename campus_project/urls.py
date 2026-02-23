from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('users/', include('apps.users.urls')),
    path('attendance/', include('apps.attendance.urls')),
    path('food/', include('apps.food.urls')),
    path('resources/', include('apps.resources.urls')),
    path('remedial/', include('apps.remedial.urls')),
    # path('ai/', include('apps.ai_module.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
