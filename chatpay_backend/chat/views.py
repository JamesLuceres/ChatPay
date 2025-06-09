# chat/views.py

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Room, Message, RoomInvite
from .serializers import (
    RegisterSerializers,
    RoomSerializer, RoomInviteSerializer, JoinRoomSerializer
)


class RegisterView(generics.GenericAPIView):
    serializer_class       = RegisterSerializers
    authentication_classes = []
    permission_classes     = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access":  str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes     = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(
                {'error': 'Username and password both required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access':  str(refresh.access_token),
            })
        return Response(
            {'error': 'Invalid credentials.'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class MyRoomsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomSerializer

    def get_queryset(self):
        return self.request.user.rooms.all()

# Create a new invite for a room
class RoomInviteCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RoomInviteSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

# Join a room via invite code
class JoinRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, code):
        serializer = JoinRoomSerializer(data={'code': code})
        serializer.is_valid(raise_exception=True)

        invite = RoomInvite.objects.get(code=serializer.validated_data['code'])
        room = invite.room

        # Add user to room participants
        room.participants.add(request.user)
        # Mark this invite as used
        invite.mark_used()

        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
    
class RoomCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = RoomSerializer
    queryset           = Room.objects.all()