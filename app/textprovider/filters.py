from django_filters.rest_framework import FilterSet, CharFilter
from textprovider.models import Notams, ParsedNotams

class NotamsFilter(FilterSet):
    search = CharFilter(field_name='notam_text',method='filter_text')

    def filter_text(self, queryset, name, value):
        lookup = '__'.join([name,'icontains'])
        if queryset.model is ParsedNotams :
            lookup = 'notam__' + lookup
        return queryset.filter(**{lookup: value})