from __future__ import annotations

from django.urls import path

from .views import (
    UserDeleteView,
    UserRegisterView,
    UsersListView,
    UserUpdateView,
)

urlpatterns = [
    path('', UsersListView.as_view(), name='users_list'),
    path('create/', UserRegisterView.as_view(), name='user_create'),
    path('<int:pk>/update/', UserUpdateView.as_view(), name='user_update'),
    path('<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]
