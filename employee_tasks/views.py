from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from employee_tasks.models import Employee, Task
from employee_tasks.paginators import EmployeeTaskPaginator
from employee_tasks.serializer import EmployeeSerializer, TaskSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet для сотрудников"""
    serializer_class = EmployeeSerializer
    pagination_class = EmployeeTaskPaginator
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "put"]

    def get_queryset(self):
        """Получаем список сотрудников с количеством активных задач"""
        queryset = super().get_queryset()
        return queryset.annotate(
            active_tasks_count=Count(
                "tasks", filter=Q(tasks__status="in_progress"))
        ).order_by("-active_tasks_count")

    @action(
        detail=False,
        methods=["get"],
        url_path="workload",
    )
    def workload(self, request):
        """Получаем список сотрудников с количеством задач"""
        queryset = Employee.objects.all()
        serializer = EmployeeSerializer(queryset, many=True)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet для задач"""
    serializer_class = TaskSerializer
    pagination_class = EmployeeTaskPaginator
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete", "put"]

    # def get_queryset(self):
    #     """Получаем список задач для текущего пользователя """
    #     queryset = super().get_queryset()
    #     return queryset.filter(Q(employee=self.request.user) | Q(status="pemding"))

