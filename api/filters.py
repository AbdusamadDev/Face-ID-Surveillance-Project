from django_filters import rest_framework as filters
from django.db.models import Q
import django_filters

from api.models import CriminalsRecords, Camera, Criminals


class GenericFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(criminal__first_name__icontains=value) |
            Q(criminal__last_name__icontains=value) |
            Q(criminal__age__icontains=value) |
            Q(camera__name__icontains=value) |
            Q(image_path__icontains=value)
        )

    class Meta:
        model = CriminalsRecords
        fields = {
            'date_recorded': ['exact', 'year', 'month', 'day', 'hour', 'minute', 'second', 'gte', 'lte'],
            'criminal__first_name': ['exact', 'icontains'],
            'criminal__last_name': ['exact', 'icontains'],
            'criminal__age': ['exact', 'gte', 'lte'],
            'camera__name': ['exact', 'icontains'],
            'image_path': ['exact', 'icontains'],
        }


class CameraFilter(django_filters.FilterSet):
    class Meta:
        model = Camera
        fields = ["name", "longitude", "latitude", "id"]


class CriminalsFilter(django_filters.FilterSet):
    class Meta:
        model = Criminals
        fields = ["first_name", "last_name", "age", "date_created"]


class CriminalsRecordFilter(filters.FilterSet):
    eday = filters.NumberFilter(field_name="date_recorded__day", lookup_expr='exact')
    emonth = filters.NumberFilter(field_name="date_recorded__month", lookup_expr='exact')
    eyear = filters.NumberFilter(field_name="date_recorded__year", lookup_expr='exact')
    ehour = filters.NumberFilter(field_name="date_recorded__hour", lookup_expr='exact')
    eminute = filters.NumberFilter(field_name="date_recorded__minute", lookup_expr='exact')
    esecond = filters.NumberFilter(field_name="date_recorded__second", lookup_expr='exact')

    class Meta:
        model = CriminalsRecords
        fields = {
            'date_recorded': ['exact', 'year', 'month', 'day', 'hour', 'minute', 'second', 'gte', 'lte'],
            'criminal__first_name': ['exact', 'icontains'],
            'criminal__last_name': ['exact', 'icontains'],
            'criminal__age': ['exact', 'gte', 'lte'],
        }
