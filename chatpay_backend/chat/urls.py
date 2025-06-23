# chat/urls.py

from django.urls import path
from .views import (
    RegisterView, LoginView, MyRoomsView, RoomInviteCreateView,RoomCreateView,
    JoinRoomView, RoomMessageListCreateView, LeaveRoomView, ProfileView, ChangePasswordView, AvatarUploadView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    LoginView.as_view(),    name='login'),
    path('refresh/',  TokenRefreshView.as_view(), name='token_refresh'),
    
    #profiles
    path('profile/',          ProfileView.as_view(),          name='profile'),
    path('profile/password/', ChangePasswordView.as_view(),   name='profile-password'),
    path('profile/avatar/',   AvatarUploadView.as_view(),     name='profile-avatar'),

    # Rooms & invites
    path('rooms/<int:room_id>/leave/', LeaveRoomView.as_view(), name='room-leave'),
    path('rooms/my/', MyRoomsView.as_view(), name='my-rooms'),
    path('rooms/invite/', RoomInviteCreateView.as_view(),name='room-invite-create'),
    path('rooms/join/<uuid:code>/', JoinRoomView.as_view(), name='room-join'),

    path('rooms/', RoomCreateView.as_view(), name='room-create'),
    # Token refresh etc.
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # message list
    path('rooms/<int:room_id>/messages/', RoomMessageListCreateView.as_view(), name='room-messages'),
]
