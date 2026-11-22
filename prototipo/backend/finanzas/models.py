# ==============================================================================
# MÓDULO: finanzas/models.py
# CASOS DE USO: CU26 (HU-52 Cobros y Extracto Bancario 20 años,
#                     HU-53 Dashboard Financiero Gerencial >= 2 años,
#                     HU-54 Liquidación de Honorarios a Psicólogos)
# DESCRIPCIÓN: Entidades persistentes de contabilidad clínica en Bolivianos (BOB)
#              aisladas por esquema tenant.
# ==============================================================================
import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone
from accounts.models import Usuario
from clinica.models import Paciente, Psicologo
from agenda.models import Cita


class CuentaPaciente(models.Model):
    """
    Estado de cuenta consolidado por paciente en Bolivianos (BOB).
    Se actualiza de forma atómica (select_for_update + transaction.atomic)
    ante cada cargo de cita/servicio y cada pago confirmado.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paciente = models.OneToOneField(
        Paciente,
        on_delete=models.RESTRICT,
        related_name='cuenta_financiera',
        verbose_name='Paciente',
    )
    moneda = models.CharField(max_length=5, default='BOB', verbose_name='Moneda')
    total_cargado = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'),
        verbose_name='Total Cargado (Bs.)',
    )
    total_pagado = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'),
        verbose_name='Total Pagado (Bs.)',
    )
    saldo_pendiente = models.DecimalField(
        max_digits=14, decimal_places=2, default=Decimal('0.00'),
        verbose_name='Saldo Pendiente (Bs.)',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'finanzas_cuentapaciente'
        verbose_name = 'Cuenta de Paciente'
        verbose_name_plural = 'Cuentas de Pacientes'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(total_cargado__gte=0),
                name='chk_cuenta_total_cargado_no_neg',
            ),
            models.CheckConstraint(
                condition=models.Q(total_pagado__gte=0),
                name='chk_cuenta_total_pagado_no_neg',
            ),
        ]
        indexes = [
            models.Index(fields=['saldo_pendiente'], name='idx_cuenta_saldo_pend'),
        ]

    def __str__(self):
        return f"Cuenta {self.paciente.codigo_expediente} — Saldo: Bs. {self.saldo_pendiente}"


class PagoConsulta(models.Model):
    """
    Registro de cobro verificado en Bolivianos (Bs.) con número de recibo
    correlativo por tenant y código de verificación para comprobante PDF.
    """
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('QR_BANCARIO', 'QR Bancario'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('TARJETA_STRIPE', 'Tarjeta / Stripe'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cuenta = models.ForeignKey(
        CuentaPaciente,
        on_delete=models.RESTRICT,
        related_name='pagos',
        verbose_name='Cuenta del Paciente',
    )
    cita = models.ForeignKey(
        Cita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos',
        verbose_name='Cita Asociada',
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto Pagado (Bs.)')
    metodo_pago = models.CharField(
        max_length=20,
        choices=METODO_PAGO_CHOICES,
        default='EFECTIVO',
        verbose_name='Método de Pago',
    )
    numero_recibo = models.CharField(
        max_length=40,
        unique=True,
        verbose_name='Número de Recibo Correlativo',
    )
    codigo_verificacion = models.CharField(
        max_length=32,
        unique=True,
        verbose_name='Código de Verificación',
    )
    referencia_externa = models.CharField(
        max_length=120,
        blank=True,
        default='',
        verbose_name='Referencia Bancaria / Voucher',
    )
    observaciones = models.TextField(blank=True, default='', verbose_name='Observaciones')
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_registrados',
        verbose_name='Registrado Por',
    )
    anulado = models.BooleanField(default=False, verbose_name='Anulado')
    fecha_pago = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Pago')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finanzas_pagoconsulta'
        verbose_name = 'Pago de Consulta'
        verbose_name_plural = 'Pagos de Consultas'
        ordering = ['-fecha_pago']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monto__gt=0),
                name='chk_pago_monto_positivo',
            ),
        ]
        indexes = [
            models.Index(fields=['fecha_pago'], name='idx_pago_fecha'),
            models.Index(fields=['metodo_pago', 'fecha_pago'], name='idx_pago_metodo_fecha'),
            models.Index(fields=['cuenta', 'fecha_pago'], name='idx_pago_cuenta_fecha'),
            models.Index(fields=['anulado', 'fecha_pago'], name='idx_pago_anulado_fecha'),
        ]

    def __str__(self):
        return f"Recibo {self.numero_recibo} — Bs. {self.monto} ({self.metodo_pago})"


class MovimientoFinanciero(models.Model):
    """
    Libro mayor cronológico (Debe/Cargo y Haber/Abono) optimizado con índices
    para generar extractos históricos tipo bancario de hasta 20 años.
    """
    TIPO_CHOICES = [
        ('CARGO', 'Cargo (Debe)'),
        ('ABONO', 'Abono / Pago (Haber)'),
        ('AJUSTE', 'Ajuste Contable'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cuenta = models.ForeignKey(
        CuentaPaciente,
        on_delete=models.RESTRICT,
        related_name='movimientos',
        verbose_name='Cuenta del Paciente',
    )
    cita = models.ForeignKey(
        Cita,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_financieros',
        verbose_name='Cita Asociada',
    )
    pago = models.ForeignKey(
        PagoConsulta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos',
        verbose_name='Pago Asociado',
    )
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES, verbose_name='Tipo de Movimiento')
    concepto = models.CharField(max_length=255, verbose_name='Concepto / Glosa')
    metodo_pago = models.CharField(max_length=20, blank=True, default='', verbose_name='Método de Pago')
    numero_documento = models.CharField(max_length=50, blank=True, default='', verbose_name='N° Recibo / Documento')
    debe = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Debe / Cargo (Bs.)')
    haber = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name='Haber / Abono (Bs.)')
    fecha_movimiento = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Movimiento')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'finanzas_movimientofinanciero'
        verbose_name = 'Movimiento Financiero'
        verbose_name_plural = 'Movimientos Financieros'
        ordering = ['fecha_movimiento', 'fecha_creacion']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(debe__gte=0) & models.Q(haber__gte=0),
                name='chk_mov_debe_haber_no_neg',
            ),
        ]
        indexes = [
            models.Index(fields=['fecha_movimiento'], name='idx_mov_fecha'),
            models.Index(fields=['cuenta', 'fecha_movimiento'], name='idx_mov_cuenta_fecha'),
            models.Index(fields=['tipo', 'fecha_movimiento'], name='idx_mov_tipo_fecha'),
        ]

    def __str__(self):
        return f"{self.fecha_movimiento:%Y-%m-%d} | {self.tipo} | D:{self.debe} H:{self.haber}"


class LiquidacionHonorario(models.Model):
    """
    Liquidación periódica de honorarios profesionales a un psicólogo en Bs.
    con porcentaje configurable de retención/comisión institucional del centro.
    """
    ESTADO_CHOICES = [
        ('GENERADA', 'Generada (Pendiente de Pago)'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.RESTRICT,
        related_name='liquidaciones_honorarios',
        verbose_name='Psicólogo',
    )
    codigo_liquidacion = models.CharField(
        max_length=40,
        unique=True,
        verbose_name='Código de Liquidación',
    )
    fecha_inicio = models.DateField(verbose_name='Periodo Desde')
    fecha_fin = models.DateField(verbose_name='Periodo Hasta')
    total_sesiones = models.PositiveIntegerField(default=0, verbose_name='Total Sesiones Liquidadas')
    monto_bruto = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Monto Bruto (Bs.)')
    porcentaje_comision_centro = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('30.00'),
        verbose_name='Comisión del Centro (%)',
    )
    comision_centro = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Retención Centro (Bs.)')
    monto_neto_psicologo = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Neto Psicólogo (Bs.)')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='GENERADA', verbose_name='Estado')
    referencia_bancaria = models.CharField(max_length=120, blank=True, default='', verbose_name='Referencia Bancaria')
    observaciones = models.TextField(blank=True, default='', verbose_name='Observaciones')
    emitida_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='liquidaciones_emitidas',
        verbose_name='Emitida Por',
    )
    pagada_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='liquidaciones_pagadas',
        verbose_name='Pagada Por',
    )
    fecha_emision = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Emisión')
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Pago')

    class Meta:
        db_table = 'finanzas_liquidacionhonorario'
        verbose_name = 'Liquidación de Honorarios'
        verbose_name_plural = 'Liquidaciones de Honorarios'
        ordering = ['-fecha_emision']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fecha_fin__gte=models.F('fecha_inicio')),
                name='chk_liq_rango_fechas',
            ),
            models.CheckConstraint(
                condition=models.Q(porcentaje_comision_centro__gte=0) & models.Q(porcentaje_comision_centro__lte=100),
                name='chk_liq_porcentaje_valido',
            ),
            models.CheckConstraint(
                condition=models.Q(monto_bruto__gte=0) & models.Q(comision_centro__gte=0) & models.Q(monto_neto_psicologo__gte=0),
                name='chk_liq_montos_no_neg',
            ),
        ]
        indexes = [
            models.Index(fields=['psicologo', 'fecha_inicio', 'fecha_fin'], name='idx_liq_psico_periodo'),
            models.Index(fields=['estado', 'fecha_emision'], name='idx_liq_estado_fecha'),
        ]

    def __str__(self):
        return f"{self.codigo_liquidacion} — {self.psicologo} ({self.estado}) Bs. {self.monto_neto_psicologo}"


class DetalleLiquidacionCita(models.Model):
    """
    Vínculo granular entre una LiquidacionHonorario y cada Cita liquidada.
    Previene el doble pago de una misma sesión en periodos solapados.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    liquidacion = models.ForeignKey(
        LiquidacionHonorario,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Liquidación',
    )
    cita = models.ForeignKey(
        Cita,
        on_delete=models.RESTRICT,
        related_name='detalles_liquidacion',
        verbose_name='Cita Liquidada',
    )
    monto_sesion = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Monto Sesión (Bs.)')
    comision_sesion = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Comisión Centro (Bs.)')
    neto_sesion = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Neto Psicólogo (Bs.)')
    activo = models.BooleanField(default=True, verbose_name='Liquidación Activa (No Anulada)')

    class Meta:
        db_table = 'finanzas_detalleliquidacioncita'
        verbose_name = 'Detalle de Liquidación por Cita'
        verbose_name_plural = 'Detalles de Liquidación por Cita'
        constraints = [
            models.UniqueConstraint(
                fields=['cita'],
                condition=models.Q(activo=True),
                name='uq_cita_una_liquidacion_activa',
            ),
        ]
        indexes = [
            models.Index(fields=['liquidacion', 'cita'], name='idx_detliq_liq_cita'),
        ]

    def __str__(self):
        return f"{self.liquidacion.codigo_liquidacion} -> Cita {self.cita_id} (Bs. {self.neto_sesion})"
