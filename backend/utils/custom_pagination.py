from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math


class CustomPagination(PageNumberPagination):

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):

        current_page = self.page.number
        total_items = self.page.paginator.count
        page_size = self.get_page_size(self.request)

        total_pages = math.ceil(total_items / page_size)
        print("nber items ", total_items, " page size ", page_size, " total page ", total_pages)

        return Response({
            'currentPage': current_page,
            'nber_pages': total_pages,
            'page_size': page_size,
            'nberItems': total_items,
            'nextPage': self.get_next_link(),
            'previousPage': self.get_previous_link(),
            'listItems': data
        })