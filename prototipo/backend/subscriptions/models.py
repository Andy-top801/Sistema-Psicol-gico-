# ==============================================================================
# MÓDULO: subscriptions/models.py
# DESCRIPCIÓN: Modelo de datos para suscripciones SaaS con Stripe.
#              Registra cada transacción de checkout y su vinculación al tenant creado.
# PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
# ==============================================================================
import uuid
from django.db import models


class Suscripcion(models.Model):
    """
    Registra cada suscripción creada a través de Stripe Checkout.
    Actúa como puente entre el pago y el tenant auto-provisionado.
    """
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Pago'),
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suscripciones',
        verbose_name='Centro (Tenant)',
    )
    plan = models.CharField(max_length=50, verbose_name='Plan de Suscripción')
    email_cliente = models.EmailField(max_length=150, verbose_name='Email del Cliente')
    nombre_centro = models.CharField(max_length=150, verbose_name='Nombre del Centro')
    nombre_admin = models.CharField(
        max_length=100,
        default='Administrador',
        verbose_name='Nombre del Administrador',
    )
    stripe_session_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Stripe Session ID',
    )
    stripe_customer_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Stripe Customer ID',
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name='Estado',
    )
    password_temporal = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name='Contraseña Temporal Inicial',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_activacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Activación',
    )

    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.nombre_centro} — {self.plan} ({self.estado})'


class FacturaSaaS(models.Model):
    """
    HU-55 (CU26): Registro oficial de facturación SaaS en USD por centro psicológico
    en esquema public, con idempotencia garantizada sobre eventos Stripe.
    """
    ESTADO_CHOICES = [
        ('PAGADA', 'Pagada'),
        ('PENDIENTE', 'Pendiente'),
        ('FALLIDA', 'Fallida'),
        ('ANULADA', 'Anulada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suscripcion = models.ForeignKey(
        Suscripcion,
        on_delete=models.CASCADE,
        related_name='facturas',
        verbose_name='Suscripción',
    )
    tenant = models.ForeignKey(
        'tenants.Tenant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='facturas_saas',
        verbose_name='Centro (Tenant)',
    )
    numero_factura = models.CharField(max_length=40, unique=True, verbose_name='N° Factura SaaS')
    plan = models.CharField(max_length=50, verbose_name='Plan Facturado')
    monto_usd = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto (USD)')
    moneda = models.CharField(max_length=5, default='USD', verbose_name='Moneda')
    stripe_session_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Stripe Session / Event ID (Idempotencia)',
    )
    stripe_invoice_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Stripe Invoice ID',
    )
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PAGADA', verbose_name='Estado')
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Emisión')
    fecha_renovacion = models.DateField(null=True, blank=True, verbose_name='Próxima Renovación')

    class Meta:
        db_table = 'subscriptions_facturasaas'
        verbose_name = 'Factura SaaS (USD)'
        verbose_name_plural = 'Facturas SaaS (USD)'
        ordering = ['-fecha_emision']
        indexes = [
            models.Index(fields=['tenant', 'fecha_emision'], name='idx_factsaas_tenant_fecha'),
            models.Index(fields=['estado', 'fecha_emision'], name='idx_factsaas_estado_fecha'),
        ]

    def __str__(self):
        return f'{self.numero_factura} — {self.plan} (${self.monto_usd} USD)'

