from rest_framework.documentation import include_docs_urls
from django.urls import path
from rest_framework.permissions import AllowAny

urlpatterns = [
    path(
        "docs/",
        include_docs_urls(title="API Documentation", permission_classes=[AllowAny]),
    ),
]
