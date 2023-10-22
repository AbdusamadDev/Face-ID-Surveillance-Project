from rest_framework.pagination import PageNumberPagination


class CameraPagination(PageNumberPagination):
    page_size = 10


class CriminalsPagination(PageNumberPagination):
    page_size = 10
