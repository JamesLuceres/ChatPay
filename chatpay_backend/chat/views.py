# chat/views.py
from django.shortcuts import get_object_or_404 
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from .models import Room, Message, RoomInvite
from .serializers import (
    RegisterSerializers, MessageSerializer,
    RoomSerializer, RoomInviteSerializer, JoinRoomSerializer, RoomCreateSerializer, 
    ProfileSerializer, ChangePasswordSerializer, AvatarSerializer,
)
from rest_framework.decorators import api_view, permission_classes
from .bch_utils import ensure_user_has_bch_address


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
        
        # Generate BCH address for the new user
        ensure_user_has_bch_address(user)
        
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
        return Room.objects.filter(participants=self.request.user)

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

#create new rooms
class RoomCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        # Use the lightweight serializer on POST, full one elsewhere
        if self.request.method == 'POST':
            return RoomCreateSerializer
        return RoomSerializer

    def perform_create(self, serializer):
        # Inject created_by and add the creator as a participant
        room = serializer.save(created_by=self.request.user)
        room.participants.add(self.request.user)
    
#store messages in rooms
class RoomMessageListCreateView(generics.ListCreateAPIView):
    permission_classes =[permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        room_id = self.kwargs['room_id']
        Room.objects.get(pk=room_id)
        return Message.objects.filter(room_id=room_id)
    
    def perform_create(self, serializer):
        room_id = self.kwargs['room_id']
        room = Room.objects.get(id=room_id)
        serializer.save(sender=self.request.user, room=room)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

class LeaveRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        room.participants.remove(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ProfileSerializer

    def get_object(self):
        # simply return the logged-in user
        return self.request.user

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ChangePasswordSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = AvatarSerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # save avatar and return new URL
        request.user.profile.avatar = serializer.validated_data['avatar']
        request.user.profile.save()
        return Response({'avatar_url': request.user.profile.avatar.url}, status=status.HTTP_200_OK)