import factory
from django.utils import timezone

from employee_tasks.models import Employee, Task


class EmployeeFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания сотрудников"""
    class Meta:
        model = Employee

    email = factory.LazyAttribute(lambda n: "{}.{}@example.com".format(n.first_name, n.last_name).lower())
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    position = factory.Faker("job")
    password = factory.Faker("password")


class TaskFactory(factory.django.DjangoModelFactory):
    """Фабрика для создания задач"""
    class Meta:
        model = Task

    employee = factory.SubFactory(EmployeeFactory)

    title_task = factory.Faker("sentence", nb_words=5)
    task_description = factory.Faker("paragraph", nb_sentences=2)
    deadline = factory.LazyFunction(timezone.now)
    status = factory.Iterator(["pending", "in_progress", "completed", "canceled"])

    parent_task = None
