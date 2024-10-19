from django.contrib import admin

from employee_tasks.models import Employee, Task


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'position')
    list_filter = ('last_name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title_task', 'employee', 'deadline', 'status')
    list_filter = ('employee','status',)
