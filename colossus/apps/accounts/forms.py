from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

import pytz

from .models import User


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user


class UserForm(forms.ModelForm):
    TIMEZONE_CHOICES = (('', '---------'),) + tuple(map(lambda tz: (tz, tz), pytz.common_timezones))

    timezone = forms.ChoiceField(
        choices=TIMEZONE_CHOICES,
        required=False,
        label=_('Timezone')
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'timezone')
