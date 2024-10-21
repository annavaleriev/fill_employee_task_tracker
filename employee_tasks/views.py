from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from employee_tasks.filters import EmployeeTaskFilter
from employee_tasks.models import Employee, Task
from employee_tasks.paginators import EmployeeTaskPaginator
from employee_tasks.serializer import EmployeeSerializer, TaskSerializer, EmployeeCreateSerializer, \
    BusyEmployeeSerializer


class EmployeeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для сотрудников"""
    serializer_class = EmployeeSerializer
    pagination_class = EmployeeTaskPaginator
    queryset = Employee.objects.employees_with_count_tasks()
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = EmployeeTaskFilter

    @action(
        detail=False,
        serializer_class=BusyEmployeeSerializer,
        queryset=Employee.objects.employees_with_count_tasks().order_by("-active_tasks_count")
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
    http_method_names = ["get", "post", "delete", "patch"]

    @action(
        detail=False,
        queryset=Task.objects.filter(
            Q(status="pending")
            &
            Q(parent_task__isnull=False)
            &
            Q(parent_task__status="in_progress")
        ).all(),
        serializer_class=TaskSerializer
    )
    def important(self, request):
        """Получаем важные задачи, которые не взяты в работу"""
        return super().list(request)

    # @action(
    #     detail=True,
    #     methods=["get"],
    #     url_path="get-employees-for-task"
    # )
    # def get_employees_for_tasks(self, request, pk=None):
    #     """Получаем список сотрудников, которые могут взять важную задачу"""
    #     try:
    #         task = self.get_queryset().get(pk=pk)
    #         if task.status != "pending":
    #             return Response({"message": "Задача уже взята в работу"}, status=status.HTTP_400_BAD_REQUEST)
    #
    #         busy_employees = Employee.objects.annotate(
    #             active_tasks_count=Count(
    #                 "tasks", filter=Q(tasks__status="in_progress"))
    #         ).order_by("active_tasks_count")
    #
    #         list_busy_employees = busy_employees.first()
    #
    #         if list_busy_employees is None:
    #             return Response({"message": "Нет сотрудников"}, status=status.HTTP_404_NOT_FOUND)
    #
    #         free_employees_for_tasks = busy_employees.filter(
    #             Q(active_tasks_count__lte=list_busy_employees.active_tasks_count + 2) |
    #             Q(tasks__parent_task=task.parent_task)
    #         ).distinct()
    #
    #
    #         employee_data = EmployeeSerializer(free_employees_for_tasks, many=True).data
    #
    #         response_data = {
    #             "importance": "Важная",
    #             "deadline": task.deadline,
    #             "employees": employee_data,
    #         }
    #
    #         return Response(response_data)
    #
    #     except Task.DoesNotExist:
    #         return Response({"message": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EmployeeCreateView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateSerializer
    permission_classes = (
        AllowAny,
    )

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()
