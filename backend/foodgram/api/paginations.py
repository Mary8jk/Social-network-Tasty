from rest_framework.pagination import PageNumberPagination
from . import constants


class CustomPagination(PageNumberPagination):
    page_size = constants.PAGE_SIZE
    page_size_query_param = 'limit'
