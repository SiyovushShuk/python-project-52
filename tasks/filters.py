from django import forms
from django.contrib.auth import get_user_model
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
        label='Статус',
    )
    executor = ModelChoiceFilter(
        queryset=User.objects.all(),
        label='Исполнитель',
    )
    labels = ModelMultipleChoiceFilter(
        field_name='labels',
        queryset=Label.objects.all(),
        label='Метки',
    )
    self_tasks = BooleanFilter(
        field_name='author',
        method='filter_self_tasks',
        label='Только мои задачи',
        widget=forms.CheckboxInput,
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels', 'self_tasks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, f in self.filters.items():
            if fname == 'self_tasks':
                f.field.widget.attrs['class'] = 'form-check-input'
            else:
                wname = f.field.widget.__class__.__name__
                css = 'form-select' if wname in ('Select', 'SelectMultiple') else 'form-control'
                f.field.widget.attrs['class'] = css

    def filter_self_tasks(self, queryset, name, value):
        if value:
            user = getattr(self.request, 'user', None)
            if user and user.is_authenticated:
                return queryset.filter(author=user)
        return queryset
