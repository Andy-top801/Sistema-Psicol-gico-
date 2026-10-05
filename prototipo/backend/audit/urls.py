from django.urls import path

from .views import AuditLogView


urlpatterns = [
    path("audit/logs/", AuditLogView.as_view(), name="audit-logs"),
    path("audit/log/", AuditLogView.as_view(), name="audit-log-singular"),
    path("v1/audit/log/", AuditLogView.as_view(), name="audit-log-v1"),
]

