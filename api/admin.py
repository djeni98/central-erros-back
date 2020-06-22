from django.contrib import admin

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from api.models import User, Event

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
    class Meta:
        model = User
        widgets = { 'password': forms.PasswordInput() }
        fields = ['name', 'email', 'password']


class UserModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = UserChangeForm if obj else UserCreateForm
        return super().get_form(request, obj, **kwargs)

    list_display = ('name', 'email', 'last_login')


class EventModelAdmin(admin.ModelAdmin):
    def event(self, obj):
        return str(obj)

    list_display = ('event', 'level', 'datetime', 'user')


admin.site.register(User, UserModelAdmin)
admin.site.register(Event, EventModelAdmin)
