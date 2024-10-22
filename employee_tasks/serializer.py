from rest_framework import serializers

from employee_tasks.models import Employee, Task


class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач"""

    class Meta:
        model = Task
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор для сотрудников"""

    active_tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "email", "first_name", "last_name", "position", "active_tasks_count")


class BusyEmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор для сотрудников"""

    task_set = TaskSerializer(many=True, read_only=True)
    active_tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ("id", "email", "first_name", "last_name", "position", "task_set", "active_tasks_count")


class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ("password", "email", "first_name", "last_name", "position")
