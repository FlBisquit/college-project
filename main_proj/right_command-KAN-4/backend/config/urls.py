# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'API is running',
        'endpoints': {
            'admin': '/admin/',
            'users': '/api/users/',
            'servers': '/api/servers/',
        }
    })

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/servers/', include('servers.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)