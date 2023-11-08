import django_filters
from django_filters import rest_framework as filters
from api.models import Camera, Criminals
from .models import CriminalsRecords


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

    class Meta:
        model = CriminalsRecords
        fields = {
            'date_recorded': ['exact', 'year', 'month', 'day', 'gte', 'lte'],
            'criminal__first_name': ['exact', 'icontains'],
            'criminal__last_name': ['exact', 'icontains'],
            'criminal__age': ['exact', 'gte', 'lte'],
        }
