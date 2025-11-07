import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obsidian.settings')

from django.core.asgi import get_asgi_application

# ✅ Initialize Django first BEFORE importing Channels routing & consumers
django_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import webapp.routing

application = ProtocolTypeRouter({
    "http": django_app,  # ✅ Django app loaded first
    "websocket": AuthMiddlewareStack(
        URLRouter(
            webapp.routing.websocket_urlpatterns
        )
    ),
})
