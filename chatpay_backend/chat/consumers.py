# chat/consumers.py
import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from django.db import close_old_connections
from asgiref.sync import sync_to_async

User = get_user_model()

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_id   = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f"chat_{self.room_id}"

        # authenticate token from querystring ?token=…
        token = dict((x.split('=') for x in self.scope['query_string'].decode().split("&")))\
                    .get('token', None)

        if not token:
            return await self.close()

        try:
            # verify JWT
            UntypedToken(token)
        except (InvalidToken, TokenError):
            return await self.close()

        # pull user instance out
        payload = UntypedToken(token).payload
        user = await sync_to_async(User.objects.get)(id=payload['user_id'])
        self.scope['user'] = user

        # join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        text = content.get('message')
        if not text:
            return

        # persist to your Message model
        from .models import Message
        msg = await sync_to_async(Message.objects.create)(
            room_id=self.room_id,
            sender=self.scope['user'],
            content=text
        )

        data = {
            'id':           msg.id,
            'sender_id':    msg.sender.id,
            'sender_name':  msg.sender.username,
            'message':      msg.content,
            'timestamp':    msg.timestamp.isoformat(),
        }

        # broadcast to everyone in room
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat.message',
                'data': data
            }
        )

    async def chat_message(self, event):
        # this automatically does self.send_json(event['data'])
        await self.send_json(event['data'])
