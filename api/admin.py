from django.contrib import admin

from api.models import Event, Agent


class EventModelAdmin(admin.ModelAdmin):
    def event(self, obj):
        return str(obj)

    list_display = ('event', 'level', 'datetime', 'source', 'collected_by')


admin.site.register(Event, EventModelAdmin)
admin.site.register(Agent)
