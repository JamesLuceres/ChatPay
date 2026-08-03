# chat/urls.py

from django.urls import path
from .views import (
    RegisterView, LoginView, MyRoomsView, RoomInviteCreateView, RoomCreateView,
    JoinRoomView, RoomMessageListCreateView, LeaveRoomView, ProfileView, 
    ChangePasswordView, AvatarUploadView, RoomDetailView, RoomSettingsView, 
    invite_info, RoomMembersView, remove_room_member,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    LoginView.as_view(),    name='login'),
    path('refresh/',  TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profiles
    path('profile/',          ProfileView.as_view(),          name='profile'),
    path('profile/password/', ChangePasswordView.as_view(),   name='profile-password'),
    path('profile/avatar/',   AvatarUploadView.as_view(),     name='profile-avatar'),

    # Rooms & Invites
    path('rooms/', RoomCreateView.as_view(), name='room-create'),
    path('rooms/my/', MyRoomsView.as_view(), name='my-rooms'),
    path('rooms/invite/', RoomInviteCreateView.as_view(), name='room-invite-create'),
    path('rooms/join/<uuid:code>/', JoinRoomView.as_view(), name='room-join'),
    path('rooms/invite-info/<uuid:code>/', invite_info, name='invite-info'),
    path('rooms/<uuid:room_id>/', RoomDetailView.as_view(), name='room-detail'),
    path('rooms/<uuid:room_id>/leave/', LeaveRoomView.as_view(), name='room-leave'),
    path('rooms/<uuid:room_id>/members/', RoomMembersView.as_view(), name='room-members'),
    path('rooms/<uuid:room_id>/remove_member/', remove_room_member, name='remove_room_member'),
    path('rooms/<uuid:room_id>/settings/', RoomSettingsView.as_view(), name='room-settings'),
    path('rooms/<uuid:room_id>/messages/', RoomMessageListCreateView.as_view(), name='room-messages'),
]
