# ==============================================================================
# MÓDULO: subscriptions/urls.py
# DESCRIPCIÓN: Rutas URL de la app de suscripciones.
# PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
# ==============================================================================
from django.urls import path
from subscriptions.views import PlansListView, CreateCheckoutView, VerifySessionView

urlpatterns = [
    path('plans/', PlansListView.as_view(), name='subscription-plans'),
    path('create-checkout/', CreateCheckoutView.as_view(), name='create-checkout'),
    path('verify-session/', VerifySessionView.as_view(), name='verify-session'),
]
