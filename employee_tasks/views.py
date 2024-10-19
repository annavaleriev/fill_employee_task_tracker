from django.db.models import Count, Q
from rest_framework import viewsets, status
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
        """Получаем список сотрудников с количеством активных задач"""
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

    @action(
        detail=False,
        methods=["get"],
        url_path="not-worked-tasks"
    )
    def not_worked_tasks(self, request):
        """Получаем важные задачи, которые не взяты в работу"""
        try:
            important_tasks = self.get_queryset().filter(
                Q(status="pending") & Q(parent_task_isnull=False)
            ).distinct()

            serializer = TaskSerializer(important_tasks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_employees_for_task(self, request, pk=None):
        """Получаем список сотрудников, которые могут взять важную задачу"""
        try:
            task = self.get_queryset().get(pk=pk)
            if task.status != "pending":
                return Response({"detail": "Задача уже взята в работу"}, status=status.HTTP_400_BAD_REQUEST)

            busy_employees = Employee.objects.annotate(
                active_tasks_count=Count(
                    "task", filter=Q(tasks__status="in_progress"))
            ).order_by("active_tasks_count")

            list_busy_employees = busy_employees.first()

            free_employees_for_tasks = busy_employees.filter(
                Q(active_tasks_count_lte=list_busy_employees.active_tasks_count + 2) |
                Q(task__parent_task=task.parent_task)
            ).distinct()


            employee_data = EmployeeSerializer(free_employees_for_tasks, many=True).data

            response_data = {
                "importNCE": "Важная",
                "deadline": task.deadline,
                "employee": employee_data,
            }

            return Response(response_data)

        except Task.DoesNotExist:
            return Response({"detail": "Задача не найдена"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
