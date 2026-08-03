# chat/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import CustomUser, Room, Message, RoomInvite

User = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display   = ("user", "token_address", "date_joined")
    search_fields  = ("user__username", "token_address")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display    = ("name", "created_at")
    search_fields   = ("name",)
    filter_horizontal = ("participants",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display   = ("room", "sender", "short_content", "timestamp")
    list_filter    = ("room", "sender")
    search_fields  = ("content",)

    def short_content(self, obj):
        return obj.content[:40] + ("…" if len(obj.content) > 40 else "")
    short_content.short_description = "Content"


@admin.register(RoomInvite)
class RoomInviteAdmin(admin.ModelAdmin):
    list_display = ('code', 'room', 'created_by', 'uses', 'max_uses', 'expires_at')
    list_filter  = ('room', 'created_by', 'uses', 'max_uses', 'expires_at')
    search_fields = ('code', 'room__name', 'created_by__username')

    # show a "used" boolean in list_display
    def used(self, obj):
        return not obj.is_valid()
    used.boolean = True
    used.short_description = "Expired/Depleted"
