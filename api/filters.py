from django_filters import rest_framework as filters
from django.db.models import Q

from api.models import CriminalsRecords, Camera, Criminals


class CameraFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(url__icontains=value)
        )

    class Meta:
        model = Camera
        fields = {
            "name": ["exact", "icontains"],
            "url": ["exact", "icontains"],
            "longitude": ["exact", "icontains"],
            "latitude": ["exact", "icontains", "gte", "lte"],
        }


class CriminalsFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_search')

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(age__icontains=value) |
            Q(description__icontains=value)
        )

    class Meta:
        model = Criminals
        fields = {
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'age': ['exact', 'gte', 'lte'],
        }


class CriminalsRecordFilter(filters.FilterSet):
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
