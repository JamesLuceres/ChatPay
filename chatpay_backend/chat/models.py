# chat/models.py

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class CustomUser(models.Model):
    """
    Profile extension for the built-in User.
    Stores join date, avatar, and token address.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    token_address = models.CharField(max_length=100, blank=True, null=True)
    avatar        = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_joined   = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} Profile"


class Room(models.Model):
    """
    A chat room that many users can join.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    participants = models.ManyToManyField(
       settings.AUTH_USER_MODEL,
       related_name='rooms',
       blank=True
    )
    max_participants = models.PositiveIntegerField(
        default=0,
        help_text="Maximum number of users allowed in this room(0 = unlimited)"
    )
    created_at = models.DateTimeField(default=timezone.now)
    contract_address = models.CharField(max_length=100, blank=True, null=True)  # BCH contract address for the room

   # ─── track who created the room ────────────────────────────────────
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='rooms_created',
        null=True,                 # allow null on existing rows
        on_delete=models.SET_NULL  # don't delete rooms if user is removed
    )
    
    # Minimum balance required to join this room (in BCH)
    min_balance_required = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        default=0.00018,  # Default minimum balance (0.00018 BCH)
        help_text="Minimum BCH balance required to join this room"
    )
    # Per-message BCH fee required to send messages in this room
    message_fee = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        default=0.000018,  # Default message fee (0.000018 BCH)
        help_text="BCH fee required to send a message in this room"
    )
    
    def __str__(self):
        return self.name
    

class Message(models.Model):
    """
    A message sent by a user into a Room.
    """
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content   = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('timestamp',)

    def __str__(self):
        ts = self.timestamp.strftime('%Y-%m-%d %H:%M')
        return f"[{ts}] {self.sender.username}: {self.content[:20]}…"


class RoomInvite(models.Model):
    """
    A one-time or reusable invite link for a Room.
    Users who hold the link/code can join the room.
    """
    room       = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='invites'
    )
    code       = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique code to share for joining this room"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_invites'
    )
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="If set, this invite cannot be used after this datetime"
    )
    max_uses   = models.PositiveIntegerField(
        default=0,
        help_text="0 = unlimited; otherwise number of times link can be used"
    )
    uses       = models.PositiveIntegerField(default=0)

    def is_valid(self):
        """
        Returns True if this invite can still be used.
        """
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_uses and self.uses >= self.max_uses:
            return False
        return True

    def mark_used(self):
        """
        Increment `uses` when someone joins via this invite.
        """
        self.uses = models.F('uses') + 1
        self.save(update_fields=['uses'])

    def get_invite_url(self):
        """
        Returns the URL path for this invite, e.g. "/rooms/join/{code}/"
        """
        return f"/rooms/join/{self.code}/"

    def __str__(self):
        return f"Invite {self.code} → {self.room.name}"
