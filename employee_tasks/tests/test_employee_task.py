from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from employee_tasks.models import Employee, Task
from employee_tasks.tests.fabrics import EmployeeFactory, TaskFactory


class EmployeeViewTests(APITestCase):
    """Тесты для сотрудников"""
    def setUP(self):
        self.employee = EmployeeFactory()
        self.client.force_authenticate(user=self.employee)

    def test_get_employees_list(self):
        response = self.client.get(reverse("employee-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_employee(self):
        """Тест создания сотрудника"""

        EmployeeFactory.create()
        new_employee = EmployeeFactory.build()
        new_employee.password = "password123"

        response = self.client.post(reverse("employee-list"), data=new_employee)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)


class TaskViewTests(APITestCase):

    def setUp(self):
        self.employee = EmployeeFactory()
        self.client.force_authenticate(user=self.employee)

    def test_get_tasks_list(self):
        """ Тест получения списка задач """
        task = TaskFactory(employee=self.employee)
        response = self.client.get(reverse("task-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, task.title_task)

    def test_create_task(self):
        """ Тест создания задачи """
        # employee = EmployeeFactory.create()
        # task = TaskFactory.build(employee=employee)
        task = TaskFactory(employee=self.employee)

        response = self.client.post(reverse("task-list"), data=task.__dict__)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def test_delete_task(self):
        """ Тест удаления задачи """
        task = TaskFactory(employee=self.employee)
        response = self.client.delete(reverse("task-detail", args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
