import django_filters

from employee_tasks.models import Employee, Task


class EmployeeTaskFilter(django_filters.FilterSet):
    task_id = django_filters.BaseInFilter(field_name='task__id')

    class Meta:
        model = Employee
        fields = ['task_id']

    def filter_queryset(self, queryset):
        task_ids = self.data.get('task_id', None)

        if task_ids:
            task_id_list = [int(i) for i in task_ids.split(',')]

            empl_with_small_count_tasks = queryset.order_by("-active_tasks_count")[:1]

            parent_tasks = Task.objects.filter(
                id__in=task_id_list
            ).values_list("parent_task_id", flat=True)

            parent_tasks_empl = queryset.filter(
                task__id__in=parent_tasks,
                active_tasks_count__lte=empl_with_small_count_tasks.first().active_tasks_count + 2
            )[:1]

            return parent_tasks_empl or empl_with_small_count_tasks

        return queryset


