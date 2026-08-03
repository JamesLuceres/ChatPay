# chat/middleware.py
import json
from urllib.parse import parse_qs

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from channels.middleware import BaseMiddleware
from asgiref.sync import sync_to_async

User = get_user_model()

@sync_to_async
def get_user(validated_token):
    try:
        return User.objects.get(id=validated_token["user_id"])
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom Channels middleware that:
    1) pulls `?token=…` off the WS handshake URL,
    2) runs UntypedToken(token) to validate,
    3) looks up the user and stuffs it in scope['user'].
    """

    async def __call__(self, scope, receive, send):
        # parse query string
        query_params = parse_qs(scope.get("query_string", b"").decode())
        token = query_params.get("token", [None])[0]

        if token:
            try:
                validated = UntypedToken(token)
                close_old_connections()
                scope["user"] = await get_user(validated)
            except (InvalidToken, TokenError):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
