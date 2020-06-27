from django.contrib import admin

from api.models import User, Event, Agent
from api.forms import UserChangeForm, UserCreateForm


class UserModelAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = UserChangeForm if obj else UserCreateForm
        return super().get_form(request, obj, **kwargs)

    readonly_fields = ('created_at', 'last_login')
    list_display = ('name', 'email', 'last_login')


class EventModelAdmin(admin.ModelAdmin):
    def event(self, obj):
        return str(obj)

    list_display = ('event', 'level', 'datetime', 'source', 'collected_by')


admin.site.register(User, UserModelAdmin)
admin.site.register(Event, EventModelAdmin)
admin.site.register(Agent)
