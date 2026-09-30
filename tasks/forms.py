from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from users.forms import _apply_bootstrap_classes

from .models import Task


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = (
            'name',
            'description',
            'status',
            'executor',
            'labels',
        )
        labels = {
            'name': 'Имя:',
            'description': 'Описание:',
            'status': 'Статус:',
            'executor': 'Исполнитель:',
            'labels': 'Метки:',
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['executor'].label_from_instance = (
            lambda user: user.get_full_name() or user.username
        )
        _apply_bootstrap_classes(self)

    def clean_name(self) -> str:
        name = self.cleaned_data.get('name')
        qs = Task.objects.filter(name=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Задача с таким именем уже существует')
        return name
