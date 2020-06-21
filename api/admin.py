from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from api.models import User, UserForm, Event

class UserModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = UserForm
        return super().get_form(request, obj, **kwargs)

    list_display = ('name', 'email', 'last_login')


class EventModelAdmin(admin.ModelAdmin):
    def event(self, obj):
        return str(obj)

    list_display = ('event', 'level', 'datetime', 'user')


admin.site.register(User, UserModelAdmin)
admin.site.register(Event, EventModelAdmin)
