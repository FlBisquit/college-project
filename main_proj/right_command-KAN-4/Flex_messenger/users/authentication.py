from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone


class JWTAuthenticationWithLastSeen(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, token = result
            user.last_seen = timezone.now()
            user.save(update_fields=['last_seen'])
        return result