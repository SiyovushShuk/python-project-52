from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.contrib.auth.models import User
from django.forms import CharField


def _apply_bootstrap_classes(form):
    for field in form.fields.values():
        widget = field.widget
        wtype = widget.__class__.__name__
        if wtype in ('Select', 'SelectMultiple'):
            css = 'form-select'
        elif wtype in ('CheckboxInput',):
            css = 'form-check-input'
        else:
            css = 'form-control'
        existing = widget.attrs.get('class', '')
        if existing:
            css = f'{existing} {css}'.strip()
        widget.attrs['class'] = css


class UserRegisterForm(UserCreationForm):
    first_name = CharField(label='Имя')
    last_name = CharField(label='Фамилия')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение'
        _apply_bootstrap_classes(self)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
        )


class UserUpdateForm(UserCreationForm):
    first_name = CharField(label='Имя')
    last_name = CharField(label='Фамилия')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password1'].label = 'Пароль'
        self.fields['password2'].label = 'Подтверждение'
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        _apply_bootstrap_classes(self)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance and self.instance.pk:
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                from django.core.exceptions import ValidationError
                raise ValidationError('Пользователь с таким именем уже существует')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 or password2:
            if password1 != password2:
                self.add_error('password2', 'Пароли не совпадают')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        else:
            existing = User.objects.get(pk=user.pk)
            user.password = existing.password
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
        )


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['password'].label = 'Пароль'
        _apply_bootstrap_classes(self)
