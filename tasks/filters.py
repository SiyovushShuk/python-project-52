from __future__ import annotations

from typing import Any

from django import forms
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.http import HttpRequest
from django_filters import (
    BooleanFilter,
    FilterSet,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
)

from labels.models import Label
from statuses.models import Status

from .models import Task

User = get_user_model()


class TaskFilter(FilterSet):
    status = ModelChoiceFilter(
        queryset=Status.objects.all(),
        label='Статус:',
    )
    executor = ModelChoiceFilter(
        queryset=User.objects.all(),
        label='Исполнитель:',
    )
    labels = ModelMultipleChoiceFilter(
        field_name='labels',
        queryset=Label.objects.all(),
        label='Метка:',
    )
    self_tasks = BooleanFilter(
        field_name='author',
        method='filter_self_tasks',
        label='Только свои задачи:',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels', 'self_tasks']

    def __init__(self, data: Any | None = None, queryset: QuerySet[Any] | None = None, *, request: HttpRequest | None = None, **kwargs: Any) -> None:
        super().__init__(data, queryset, request=request, **kwargs)
        if self.filters.get('executor'):
            self.filters['executor'].field.label_from_instance = (
                lambda user: user.get_full_name() or user.username
            )
        for fname, f in self.filters.items():
            if fname == 'self_tasks':
                f.field.widget.attrs['class'] = 'form-check-input'
            else:
                wname = f.field.widget.__class__.__name__
                css = 'form-select' if wname in ('Select', 'SelectMultiple') else 'form-control'
                f.field.widget.attrs['class'] = css

    def filter_self_tasks(self, queryset: QuerySet[Task], name: str, value: bool) -> QuerySet[Task]:
        if value:
            user = getattr(self.request, 'user', None)
            if user and user.is_authenticated:
                return queryset.filter(author=user)
        return queryset
