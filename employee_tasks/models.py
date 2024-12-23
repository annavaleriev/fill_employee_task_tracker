from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, Q

NULLABLE = {"blank": True, "null": True}


class UserManager(BaseUserManager):
    """Класс для создания пользователей"""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("У пользователя должен быть адрес электронной почты")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    def employees_with_count_tasks(self):
        return self.annotate(active_tasks_count=Count("task", filter=Q(task__status="in_progress"))).order_by(
            "last_name"
        )


class Employee(AbstractUser):
    """Класс для создания пользователей"""

    username = None
    email = models.EmailField(
        unique=True, verbose_name="Почта", help_text="Введите адрес электронной почты", **NULLABLE
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name="Имя",
        help_text="Введите имя",
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name="Фамилия",
        help_text="Введите фамилию",
    )

    position = models.CharField(
        max_length=150,
        verbose_name="Должность",
        help_text="Введите должность",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["last_name"]

    def __str__(self):
        return f"Пользователь  {self.first_name} {self.last_name} {self.email}"


class Task(models.Model):
    """Класс для создания задач"""

    STATUS_CHOICES = [
        ("pending", "в ожидании"),
        ("in_progress", "в процессе"),
        ("completed", "выполнена"),
        ("canceled", "отменена"),
    ]

    title_task = models.CharField(
        max_length=150,
        verbose_name="Название задачи",
        help_text="Введите название задачи",
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        verbose_name="Сотрудник",
        help_text="Выберите сотрудника ответственного за задачу",
        null=True,
    )

    parent_task = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        **NULLABLE,
        verbose_name="Родительская задача",
        help_text="Выберите родительскую задачу",
    )

    task_description = models.TextField(
        verbose_name="Описание задачи",
        help_text="Введите описание задачи",
    )

    deadline = models.DateTimeField(
        verbose_name="Срок выполнения задачи", help_text="Введите срок выполнения задачи", **NULLABLE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Статус задачи",
        help_text="Выберите статус задачи",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Дата создания задачи",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления",
        help_text="Дата обновления задачи",
    )

    def __str__(self):
        return f"Задача {self.title_task} {self.employee} {self.status}"

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["employee", "title_task", "status"]
