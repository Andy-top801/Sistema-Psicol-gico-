from django.urls import path
from core.views import CentroConfigView

urlpatterns = [
    path('centro/config/', CentroConfigView.as_view(), name='centro-config'),
]
