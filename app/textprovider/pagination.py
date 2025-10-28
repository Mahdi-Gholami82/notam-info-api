from rest_framework.pagination import PageNumberPagination

class NotamsPagination(PageNumberPagination):
  page_size = 10