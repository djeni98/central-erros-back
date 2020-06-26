from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from api.models import User

# Create UserChangePassword class to change user password

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        label='Password',
        help_text=(
            'Raw passwords are not stored, so there is no way to see this '
            'user’s password, but you can change the password using '
            'this form.'
            # '<a href="../password/">this form</a>.'
        )
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password']


class UserCreateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html()
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def _post_clean(self):
        super()._post_clean()
        try:
            password = self.cleaned_data.get('password')
            password_validation.validate_password(password, self.instance)
        except ValidationError as error:
            self.add_error('password', error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


