from __future__ import annotations

from typing import List

from django.urls import URLPattern, path

from .views import (
    StatusCreateView,
    StatusDeleteView,
    StatusesListView,
    StatusUpdateView,
)

urlpatterns: List[URLPattern] = [
    path('', StatusesListView.as_view(), name='statuses_list'),
    path('create/', StatusCreateView.as_view(), name='status_create'),
    path('<int:pk>/update/', StatusUpdateView.as_view(), name='status_update'),
    path('<int:pk>/delete/', StatusDeleteView.as_view(), name='status_delete'),
]
