from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Status


class StatusForm(ModelForm):
    class Meta:
        model = Status
        fields = ('name',)
        labels = {
            'name': 'Имя',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        qs = Status.objects.filter(name=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Статус с таким именем уже существует')
        return name
