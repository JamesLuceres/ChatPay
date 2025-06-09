# chat/urls.py

from django.urls import path
from .views import (
    RegisterView, LoginView, MyRoomsView, RoomInviteCreateView,RoomCreateView,
    JoinRoomView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/',    LoginView.as_view(),    name='login'),
    path('refresh/',  TokenRefreshView.as_view(), name='token_refresh'),



    # Rooms & invites
    path('rooms/my/',          MyRoomsView.as_view(),         name='my-rooms'),
    path('rooms/invite/',      RoomInviteCreateView.as_view(),name='room-invite-create'),
    path('rooms/join/<uuid:code>/', JoinRoomView.as_view(),     name='room-join'),

    path('rooms/', RoomCreateView.as_view(), name='room-create'),
    # Token refresh etc.
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
