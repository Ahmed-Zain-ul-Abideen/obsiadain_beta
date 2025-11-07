from django.urls import re_path
from webapp.Chat.consumers  import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<username>\w+)/$", ChatConsumer.as_asgi()),
]
