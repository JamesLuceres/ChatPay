# chat/consumers.py

from typing import Any, Dict
import logging
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth import get_user_model
from django.conf import settings
import requests

from .models import Message, Room

User = get_user_model()
logger = logging.getLogger(__name__)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for chat rooms.
    Assumes JWTAuthMiddleware has already populated scope['user'].
    """

    async def connect(self):
        user = self.scope.get("user")
        room_id = self.scope["url_route"]["kwargs"].get("room_id")

        # Reject if not authenticated
        if not user or user.is_anonymous:
            await self.close(code=4401)
            return

        # Save group name
        self.room_id = room_id
        self.group_name = f"chat_{room_id}"

        # Join the channel layer group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group if we joined
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
       
    async def receive_json(self, content: Dict[str, Any]):
        text = content.get("message")
        if not text:
            return

        user = self.scope.get("user")
        if not user or user.is_anonymous:
            await self.send_json({"error": "Unauthorized"})
            return

        try:
            room = await sync_to_async(Room.objects.get)(uuid=self.room_id)
        except Room.DoesNotExist:
            await self.send_json({"error": "Room not found"})
            return

        # Payment logic (sync call in async context)
        def call_payment_service(u, r):
            if not getattr(r, 'contract_address', None):
                logger.warning(f"Room {r.id} contract address not configured; skipping payment service call.")
                return

            payment_url = getattr(settings, 'PAYMENT_SERVICE_URL', "http://localhost:5001/send-message-payment")
            fee_sats = int(float(r.message_fee) * 1e8) if r.message_fee else 1800
            payload = {
                "userName": u.username,
                "userId": str(u.id),
                "roomContractAddress": r.contract_address,
                "amountSats": fee_sats
            }
            logger.info(f"Posting payment payload to {payment_url}: {payload}")
            try:
                resp = requests.post(payment_url, json=payload, timeout=5)
                if resp.status_code != 200:
                    logger.error(f"Payment service failure: {resp.status_code} {resp.text}")
                    raise Exception("Payment failed: " + resp.text)
            except requests.RequestException as req_err:
                logger.error(f"Could not reach payment microservice: {req_err}")
                # Log warning but allow message in local dev if configured
                pass

        try:
            await sync_to_async(call_payment_service)(user, room)
        except Exception as pay_err:
            await self.send_json({"error": str(pay_err)})
            return

        # Persist to database
        msg = await sync_to_async(Message.objects.create)(
            room=room,
            sender=user,
            content=text
        )

        payload = {
            "id": msg.id,
            "sender_id": msg.sender.id,
            "sender_name": msg.sender.username,
            "message": msg.content,
            "timestamp": msg.timestamp.isoformat(),
        }
        
        # Broadcast to everyone in this room
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat.message",
                "data": payload
            }
        )

    async def chat_message(self, event: Dict[str, Any]):
        await self.send_json(event["data"])