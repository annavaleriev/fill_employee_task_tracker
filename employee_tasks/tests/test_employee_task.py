from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from employee_tasks.models import Task
from employee_tasks.tests.fabrics import EmployeeFactory, TaskFactory


class BaseEmployeeTests(APITestCase):
    def setUp(self):
        self.employee = EmployeeFactory()
        self.client.force_authenticate(user=self.employee)


class EmployeeViewTests(BaseEmployeeTests):
    """Тесты для сотрудников"""

    def test__get_employees_list(self):
        employers = EmployeeFactory.create_batch(3)
        response = self.client.get(reverse("employee_tasks:employee-list"))

        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), len(employers) + 1)

        employer_ids = {employer.pk for employer in employers}
        employer_ids.add(self.employee.pk)
        response_employer_ids = {employer.get("id") for employer in data}

        self.assertSetEqual(employer_ids, response_employer_ids)

    def test__get_employer_by_id(self):
        """Тест получения информации о сотруднике"""
        response = self.client.get(reverse("employee_tasks:employee-detail", args=[self.employee.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertEqual(self.employee.pk, data.get("id"))
        self.assertEqual(self.employee.email, data.get("email"))
        self.assertEqual(self.employee.first_name, data.get("first_name"))
        self.assertEqual(self.employee.last_name, data.get("last_name"))
        self.assertEqual(self.employee.position, data.get("position"))

    def test__get_busy_employers(self):
        """Тест получения списка занятых сотрудников"""
        progress_count_tasks = 3
        TaskFactory.create_batch(progress_count_tasks, employee=self.employee, status="in_progress")
        response = self.client.get(reverse("employee_tasks:employee-busy"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["results"]

        self.assertEqual(len(data), 1)

        employee_with_tasks = data[0]
        self.assertEqual(employee_with_tasks.get("id"), self.employee.pk)
        self.assertEqual(len(employee_with_tasks.get("task_set")), progress_count_tasks)
        self.assertEqual(employee_with_tasks.get("active_tasks_count"), progress_count_tasks)

        #########################################################################################################

        busy_employer = EmployeeFactory()
        busy_employer_count_tasks = 5
        TaskFactory.create_batch(busy_employer_count_tasks, employee=busy_employer, status="in_progress")

        pending_count_tasks = 2
        TaskFactory.create_batch(pending_count_tasks, employee=self.employee, status="pending")
        response = self.client.get(reverse("employee_tasks:employee-busy"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data["results"]

        self.assertEqual(len(data), 2)

        employee_with_tasks = data[0]
        self.assertEqual(employee_with_tasks.get("id"), busy_employer.pk)
        self.assertEqual(len(employee_with_tasks.get("task_set")), busy_employer_count_tasks)
        self.assertEqual(employee_with_tasks.get("active_tasks_count"), busy_employer_count_tasks)


class TaskViewTests(BaseEmployeeTests):
    def test__get_tasks_list(self):
        """Тест получения списка задач"""
        tasks = TaskFactory.create_batch(3)
        response = self.client.get(reverse("employee_tasks:task-list"))

        data = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), len(tasks))

        task_ids = {task.pk for task in tasks}
        response_task_ids = {task.get("id") for task in data}

        self.assertSetEqual(task_ids, response_task_ids)

    def test__get_task_by_id(self):
        """Тест получения информации о задаче"""
        task = TaskFactory()
        response = self.client.get(reverse("employee_tasks:task-detail", args=[task.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data

        self.assertEqual(task.pk, data.get("id"))
        self.assertEqual(task.title_task, data.get("title_task"))
        self.assertEqual(task.parent_task, data.get("parent_task"))
        self.assertEqual(task.task_description, data.get("task_description"))
        self.assertEqual(datetime.strftime(task.deadline, "%Y-%m-%dT%H:%M:%S.%fZ"), data.get("deadline"))
        self.assertEqual(task.status, data.get("status"))

    def test__create_task(self):
        """Тест создания задачи"""
        data = {
            "title_task": "test_title",
            "task_description": "task_description",
            "deadline": datetime.now(),
            "status": "in_progress",
        }
        response = self.client.post(reverse("employee_tasks:task-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

        response_data = response.data
        self.assertEqual(response_data.get("title_task"), data["title_task"])
        self.assertEqual(response_data.get("status"), data["status"])
        self.assertEqual(response_data.get("task_description"), data["task_description"])

    def test__delete_task(self):
        """Тест удаления задачи"""
        task = TaskFactory(employee=self.employee)
        self.assertEqual(Task.objects.count(), 1)
        response = self.client.delete(reverse("employee_tasks:task-detail", args=[task.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test__put_task(self):
        """Тест изменения задачи"""
        task = TaskFactory()
        self.assertEqual(Task.objects.count(), 1)

        title_task = task.title_task
        data = {
            "title_task": "test_title",
            "task_description": task.task_description,
            "deadline": datetime.now(),
            "status": task.status,
        }
        response = self.client.put(reverse("employee_tasks:task-detail", args=[task.pk]), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data

        self.assertNotEqual(title_task, response_data.get("title_task"))

        task_from_bd = Task.objects.get(pk=task.pk)
        self.assertEqual(task_from_bd.title_task, "test_title")
