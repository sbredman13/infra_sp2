from django_filters.filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from reviews.models import Title


class TitlesFilter(FilterSet):
    '''Кастомный фильтр для поиска по жанру/категории'''
    category = CharFilter(field_name='category__slug')
    genre = CharFilter(field_name='genre__slug')
    name = CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    year = NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year', 'name')
