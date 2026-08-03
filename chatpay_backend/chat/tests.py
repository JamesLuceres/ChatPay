from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import uuid
from .models import Room, Message, RoomInvite

User = get_user_model()

class ChatPayBackendTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="Password123!"
        )
        self.user2 = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="Password123!"
        )
        
        # Login to get JWT token
        response = self.client.post("/api/login/", {
            "username": "alice",
            "password": "Password123!"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

    def test_user_registration(self):
        response = self.client.post("/api/register/", {
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertTrue(User.objects.filter(username="charlie").exists())

    def test_profile_retrieval_and_update(self):
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "alice")

        # Update profile token_address
        patch_resp = self.client.patch("/api/profile/", {
            "token_address": "bitcoincash:qp5le2vn7hjs73tlgskfdswzy60s908ly5wtll9lm9"
        })
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.profile.token_address, "bitcoincash:qp5le2vn7hjs73tlgskfdswzy60s908ly5wtll9lm9")

    def test_room_creation_and_my_rooms(self):
        room_uuid = str(uuid.uuid4())
        response = self.client.post("/api/rooms/", {
            "name": "General Chat",
            "id": room_uuid,
            "min_balance_required": "0.0001",
            "message_fee": "0.00001",
            "max_participants": 10
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check /api/rooms/my/
        my_rooms_resp = self.client.get("/api/rooms/my/")
        self.assertEqual(my_rooms_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(my_rooms_resp.data), 1)
        self.assertEqual(my_rooms_resp.data[0]["name"], "General Chat")

    def test_invite_creation_and_joining(self):
        # Create a room
        room = Room.objects.create(
            uuid=uuid.uuid4(),
            name="Crypto Room",
            created_by=self.user1,
            min_balance_required=0,
            message_fee=0
        )
        room.participants.add(self.user1)

        # Create invite
        invite = RoomInvite.objects.create(
            room=room,
            created_by=self.user1
        )

        # Bob joins via invite
        client_bob = APIClient()
        login_bob = client_bob.post("/api/login/", {
            "username": "bob",
            "password": "Password123!"
        })
        client_bob.credentials(HTTP_AUTHORIZATION=f"Bearer {login_bob.data['access']}")

        join_resp = client_bob.post(f"/api/rooms/join/{invite.code}/")
        self.assertEqual(join_resp.status_code, status.HTTP_200_OK)
        self.assertIn(self.user2, room.participants.all())

    def test_room_settings_permissions(self):
        room = Room.objects.create(
            uuid=uuid.uuid4(),
            name="Admin Only Settings Room",
            created_by=self.user1
        )
        room.participants.add(self.user1)

        # Alice (creator) patches room settings
        settings_resp = self.client.patch(f"/api/rooms/{room.uuid}/settings/", {
            "min_balance_required": 0.0005,
            "message_fee": 0.00002
        }, format="json")
        self.assertEqual(settings_resp.status_code, status.HTTP_200_OK)

        # Bob attempts to patch room settings (should be forbidden)
        client_bob = APIClient()
        login_bob = client_bob.post("/api/login/", {
            "username": "bob",
            "password": "Password123!"
        })
        client_bob.credentials(HTTP_AUTHORIZATION=f"Bearer {login_bob.data['access']}")

        bob_settings_resp = client_bob.patch(f"/api/rooms/{room.uuid}/settings/", {
            "min_balance_required": 0.001
        }, format="json")
        self.assertEqual(bob_settings_resp.status_code, status.HTTP_403_FORBIDDEN)
