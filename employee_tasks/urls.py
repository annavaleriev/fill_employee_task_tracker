from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from employee_tasks.apps import EmployeeTasksConfig
from employee_tasks.views import EmployeeCreateView, EmployeeViewSet, TaskViewSet

app_name = EmployeeTasksConfig.name

router = DefaultRouter()
router.register("employee", EmployeeViewSet)
router.register("task", TaskViewSet)

urlpatterns = [
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", EmployeeCreateView.as_view(), name="register"),
] + router.urls
