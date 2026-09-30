from django.core.exceptions import ValidationError
from django.forms import ModelForm

from users.forms import _apply_bootstrap_classes

from .models import Label


class LabelForm(ModelForm):
    class Meta:
        model = Label
        fields = ('name',)
        labels = {
            'name': 'Имя:',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_bootstrap_classes(self)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        qs = Label.objects.filter(name=name)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Метка с таким именем уже существует')
        return name
