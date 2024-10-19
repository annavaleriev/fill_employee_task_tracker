from rest_framework.routers import DefaultRouter

from employee_tasks.apps import EmployeeTasksConfig
from employee_tasks.views import EmployeeViewSet, TaskViewSet

app_name = EmployeeTasksConfig.name

router = DefaultRouter()
router.register("employee", EmployeeViewSet)
router.register("task", TaskViewSet)

urlpatterns = router.urls
