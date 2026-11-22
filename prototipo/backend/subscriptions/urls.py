# ==============================================================================
# MÓDULO: subscriptions/urls.py
# DESCRIPCIÓN: Rutas URL de la app de suscripciones.
# PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
# ==============================================================================
from django.urls import path
from subscriptions.views import (
    PlansListView,
    CreateCheckoutView,
    VerifySessionView,
    StripeWebhookView,
    SuperAdminSaaSDashboardView,
    SuperAdminTenantPlanUpdateView,
    SuperAdminFacturasListView,
    TenantQuotasView,
)

urlpatterns = [
    path('plans/', PlansListView.as_view(), name='subscription-plans'),
    path('create-checkout/', CreateCheckoutView.as_view(), name='create-checkout'),
    path('verify-session/', VerifySessionView.as_view(), name='verify-session'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('quotas/', TenantQuotasView.as_view(), name='tenant-quotas'),
    # Consola SuperAdmin SaaS (HU-55)
    path('admin/dashboard/', SuperAdminSaaSDashboardView.as_view(), name='saas-admin-dashboard'),
    path('admin/facturas/', SuperAdminFacturasListView.as_view(), name='saas-admin-facturas'),
    path('admin/tenants/<uuid:tenant_id>/', SuperAdminTenantPlanUpdateView.as_view(), name='saas-admin-tenant-update'),
]
