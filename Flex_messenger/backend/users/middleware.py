from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Пропускаем статику и media
        if request.path.startswith('/media/') or request.path.startswith('/static/'):
            return self.get_response(request)
        
        # Обновляем last_seen для аутентифицированных пользователей
        if request.user.is_authenticated:
            User.objects.filter(pk=request.user.pk).update(
                last_seen=timezone.now()
            )
        
        return self.get_response(request)