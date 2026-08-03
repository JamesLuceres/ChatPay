# chat/views.py
from django.shortcuts import get_object_or_404 
from django.contrib.auth import authenticate
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
    ProfileSerializer, ChangePasswordSerializer, AvatarSerializer, RoomSettingsSerializer,
    UserSerializer,
)
from rest_framework.decorators import api_view, permission_classes
import requests
from rest_framework.generics import RetrieveUpdateDestroyAPIView


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

        if room.max_participants and room.participants.count() >= room.max_participants:
            return Response(
                {'error': 'Room is currently full. The maximum number of participants have been reached.'},
                status=status.HTTP_400_BAD_REQUEST
            )


        # Check if user meets minimum balance requirement
        try:
            # Get user's wallet balance 
            from .services.wallet_service import get_user_balance  
            
            user_balance = get_user_balance(request.user)
            if user_balance < float(room.min_balance_required):
                return Response({
                    'error': f'Insufficient balance. You need at least {room.min_balance_required} BCH to join this room. Your balance: {user_balance} BCH'
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # If wallet service is not available, skip balance check for now
            pass

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
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    
    def get_queryset(self):
        room_id = self.kwargs['room_id']
        get_object_or_404(Room, uuid=room_id)
        return Message.objects.filter(room__uuid=room_id)
    
    def perform_create(self, serializer):
        from django.conf import settings
        from rest_framework.exceptions import ValidationError
        room_id = self.kwargs['room_id']
        room = get_object_or_404(Room, uuid=room_id)
        user = self.request.user

        if not getattr(room, 'contract_address', None):
            # Save message directly if contract address is not yet configured for room
            serializer.save(sender=user, room=room)
            return

        nodejs_url = getattr(settings, 'PAYMENT_SERVICE_URL', "http://localhost:5001/send-message-payment")
        payload = {
            "userName": user.username,
            "userId": str(user.id),
            "roomContractAddress": room.contract_address,
            "amountSats": int(float(room.message_fee) * 1e8)
        }
        try:
            resp = requests.post(nodejs_url, json=payload, timeout=5)
            if resp.status_code != 200:
                raise ValidationError({"error": f"Payment failed: {resp.text}"})
        except requests.RequestException as e:
            # Fallback for dev mode when node service is not running
            pass

        serializer.save(sender=user, room=room)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

class LeaveRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        room = get_object_or_404(Room, uuid=room_id)
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

class RoomDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = 'uuid'
    lookup_url_kwarg = 'room_id'
    permission_classes = [IsAuthenticated]

class RoomMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = Room.objects.get(uuid=room_id)
            members = room.participants.all()
            serializer = UserSerializer(members, many=True)
            return Response({"admin_id": room.created_by.id,
                "members": serializer.data}, status=status.HTTP_200_OK)
        except Room.DoesNotExist:
            return Response({'detail': 'Room not found'}, status=404)

class RoomSettingsView(APIView):
    """
    View for room admins to update room settings
    """
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, room_id):
        room = get_object_or_404(Room, uuid=room_id)
        
        # Check if user is the room admin
        if room.created_by != request.user:
            return Response({
                'error': 'Only room admins can update room settings'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RoomSettingsSerializer(room, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def invite_info(request, code):
    try:
        invite = RoomInvite.objects.get(code=code)
        room = invite.room
        return Response({
            "room_name": room.name,
            "min_balance_required": room.min_balance_required,
        })
    except RoomInvite.DoesNotExist:
        return Response({"error": "Invalid invite code."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_room_member(request, room_id):
    room = get_object_or_404(Room, uuid=room_id)
    member_id = request.data.get('member_id')
    if not member_id:
        return Response({'error': 'member_id required'}, status=status.HTTP_400_BAD_REQUEST)
    try: 
        member = room.participants.get(id=member_id)
        room.participants.remove(member)
        return Response({'success': True}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)