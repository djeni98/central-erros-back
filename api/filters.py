from rest_framework.filters import SearchFilter
from django_filters import rest_framework as filters

from logs.models import Event


class EventFilterClass(filters.FilterSet):
    environment = filters.ChoiceFilter(
        choices=[(e, e) for e in ['production', 'testing', 'development']],
        label='Environment',
        field_name='agent__environment'
    )

    class Meta:
        model = Event
        fields = ['environment', 'archived']


class EventSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        search_by = request.query_params.get('search_by')
        if search_by in ('level', 'description'):
            return [search_by]
        elif search_by == 'source':
            return['agent__name']
        return super().get_search_fields(view, request)
