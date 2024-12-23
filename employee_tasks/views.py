from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from employee_tasks.filters import EmployeeTaskFilter
from employee_tasks.models import Employee, Task
from employee_tasks.paginators import EmployeeTaskPaginator
from employee_tasks.serializer import (BusyEmployeeSerializer, EmployeeCreateSerializer, EmployeeSerializer,
                                       TaskSerializer)


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для сотрудников"""

    serializer_class = EmployeeSerializer
    pagination_class = EmployeeTaskPaginator
    queryset = Employee.objects.employees_with_count_tasks()
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EmployeeTaskFilter

    @action(
        detail=False,
        serializer_class=BusyEmployeeSerializer,
        queryset=Employee.objects.employees_with_count_tasks().order_by("-active_tasks_count"),
    )
    def busy(self, request):
        """Получаем список сотрудников с количеством активных задач"""
        return super().list(request)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для задач"""

    serializer_class = TaskSerializer
    pagination_class = EmployeeTaskPaginator
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "put"]

    @action(
        detail=False,
        queryset=Task.objects.filter(
            Q(status="pending") & Q(parent_task__isnull=False) & Q(parent_task__status="in_progress")
        ).all(),
        serializer_class=TaskSerializer,
    )
    def important(self, request):
        """Получаем важные задачи, которые не взяты в работу"""
        return super().list(request)

class EmployeeCreateView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()
