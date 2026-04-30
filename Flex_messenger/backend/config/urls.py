from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

def api_root(request):
    return JsonResponse({
        'message': 'API is running',
        'endpoints': {
            'admin': '/admin/',
            'users': '/api/users/',
            'servers': '/api/servers/',
        }
    })

@csrf_exempt
def csrf_token_view(request):
    """Возвращает CSRF токен"""
    return JsonResponse({'csrfToken': get_token(request)})

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/csrf/', csrf_token_view, name='csrf_token'),
    path('api/users/', include('users.urls')),
    path('api/servers/', include('servers.urls')),
    path('api/chat/', include('chatting.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)