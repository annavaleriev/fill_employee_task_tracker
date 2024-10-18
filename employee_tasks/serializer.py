from rest_framework import serializers

from employee_tasks.models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    """Сериализатор для сотрудников"""
    class Meta:
        model = Employee
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    """Сериализатор для задач"""
    class Meta:
        model = Task
        fields = '__all__'
