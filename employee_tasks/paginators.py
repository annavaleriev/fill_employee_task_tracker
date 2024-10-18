from rest_framework.pagination import PageNumberPagination

class EmployeeTaskPaginator(PageNumberPagination):
    """Класс пагинации для сотрудников и задач"""

    page_size = 20
    page_size_query_param = (
        "page_size"
    )
    max_page_size = 100
