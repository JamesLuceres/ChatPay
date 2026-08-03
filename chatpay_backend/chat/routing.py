# chat/routing.py
from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/?$", ChatConsumer.as_asgi()),  # Accepts /ws and /ws/
    re_path(r"ws/rooms/(?P<room_id>[0-9a-fA-F-]+)/$", ChatConsumer.as_asgi()),
]
