import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chatting.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messenger.settings')
django.setup()

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chatting.routing.websocket_urlpatterns
        )
    ),
})