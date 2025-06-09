# chat/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Room, Message, RoomInvite

# --- Registration Serializer ---
class RegisterSerializers(serializers.Serializer):
    username         = serializers.CharField(max_length=150)
    email            = serializers.EmailField()
    password         = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': ["Password and confirmation do not match."]
            })
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        CustomUser.objects.create(user=user)
        return user

    def to_representation(self, instance):
        user = instance
        profile = user.profile  # related_name='profile'
        return {
            "id":            user.id,
            "username":      user.username,
            "email":         user.email,
            "bch_address":   profile.bch_address,
            "token_address": profile.token_address,
            "date_joined":   user.date_joined
        }


# --- Chat Room & Message Serializers ---
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp']
        read_only_fields = ['id', 'sender', 'timestamp']


class RoomSerializer(serializers.ModelSerializer):
    participants = serializers.SlugRelatedField(
        many=True,
        slug_field='username',
        queryset=User.objects.all()
    )
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'participants', 'created_at', 'last_message']
        read_only_fields = ['id', 'created_at', 'last_message']

    def get_last_message(self, obj):
        last = obj.messages.order_by('-timestamp').first()
        if last:
            return MessageSerializer(last).data
        return None
class RoomInviteSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(source='created_by.username', read_only=True)
    room = serializers.SlugRelatedField(slug_field='name', queryset=Room.objects.all())

    class Meta:
        model = RoomInvite
        fields = ['id', 'room', 'code', 'created_by', 'created_at', 'expires_at', 'max_uses', 'uses']
        read_only_fields = ['id', 'code', 'created_by', 'created_at', 'uses']

class JoinRoomSerializer(serializers.Serializer):
    code = serializers.UUIDField()

    def validate_code(self, value):
        try:
            invite = RoomInvite.objects.get(code=value)
        except RoomInvite.DoesNotExist:
            raise serializers.ValidationError("Invalid invite code.")
        if not invite.is_valid():
            raise serializers.ValidationError("This invite is expired or has reached its usage limit.")
        return value