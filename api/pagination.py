from rest_framework.pagination import PageNumberPagination


class CameraPagination(PageNumberPagination):
    page_size = 8


class CriminalsPagination(PageNumberPagination):
    page_size = 8


class CriminalsRecordsPagination(PageNumberPagination):
    page_size = 8
