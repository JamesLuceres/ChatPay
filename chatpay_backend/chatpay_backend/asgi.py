import os
import django

# 1) Tell Django where your settings live
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatpay_backend.settings')
# 2) Bootstrap Django
django.setup()

from django.core.asgi import get_asgi_application
from chat.middleware import JWTAuthMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter

import chat.routing   # now safe to import your routing & consumers

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(chat.routing.websocket_urlpatterns)
    ),
})
