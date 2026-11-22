# ==============================================================================
# MÓDULO: subscriptions/services.py
# CASO DE USO: CU26 (HU-55) Panel SuperAdmin SaaS, MRR en USD y FacturaSaaS
#              idempotente en esquema public.
# ==============================================================================
from datetime import timedelta
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from audit.services import log_event
from tenants.models import Tenant
from .models import Suscripcion, FacturaSaaS
from .plans import PLANES, get_plan
from .quotas import obtener_plan_tenant, obtener_uso_cupos_tenant, _normalizar_plan_id


def _siguiente_numero_factura(anio: int) -> str:
    prefix = f"FAC-SAAS-{anio}-"
    ultimo = (
        FacturaSaaS.objects.select_for_update()
        .filter(numero_factura__startswith=prefix)
        .order_by('-numero_factura')
        .values_list('numero_factura', flat=True)
        .first()
    )
    correlativo = 1
    if ultimo:
        try:
            correlativo = int(ultimo.split('-')[-1]) + 1
        except (ValueError, IndexError):
            correlativo = FacturaSaaS.objects.filter(numero_factura__startswith=prefix).count() + 1
    return f"{prefix}{correlativo:06d}"


def registrar_factura_saas_idempotente(
    suscripcion: Suscripcion,
    stripe_session_id: str,
    stripe_invoice_id: str | None = None,
    monto_usd: Decimal | None = None,
    estado: str = 'PAGADA',
) -> tuple[FacturaSaaS, bool]:
    """
    HU-55 (c): Emite una FacturaSaaS de forma 100% idempotente por stripe_session_id.
    Si el webhook o verificación se repite, retorna la factura existente sin duplicar.
    """
    with schema_context(get_public_schema_name()):
        with transaction.atomic():
            existente = FacturaSaaS.objects.filter(stripe_session_id=stripe_session_id).first()
            if existente:
                return existente, False

            plan_key = _normalizar_plan_id(suscripcion.plan)
            plan_info = get_plan(plan_key) or PLANES['profesional']
            monto = monto_usd if monto_usd is not None else Decimal(str(plan_info['precio_mensual'] / 100.0))

            hoy = timezone.localdate()
            factura = FacturaSaaS.objects.create(
                suscripcion=suscripcion,
                tenant=suscripcion.tenant,
                numero_factura=_siguiente_numero_factura(hoy.year),
                plan=plan_key,
                monto_usd=monto,
                moneda='USD',
                stripe_session_id=stripe_session_id,
                stripe_invoice_id=stripe_invoice_id,
                estado=estado,
                fecha_renovacion=hoy + timedelta(days=30),
            )

            log_event(
                action='FACTURA_SAAS_EMITIDA',
                modulo='CU26_SAAS',
                tenant=suscripcion.tenant.schema_name if suscripcion.tenant else 'public',
                numero_factura=factura.numero_factura,
                stripe_session_id=stripe_session_id,
                plan=plan_key,
                monto_usd=float(monto),
            )
            return factura, True


def asegurar_suscripciones_catalogo() -> None:
    """
    Garantiza que todos los centros tenant existentes en el catálogo SaaS
    cuenten con su registro de Suscripcion y FacturaSaaS inicial en public.
    """
    with schema_context(get_public_schema_name()):
        tenants = Tenant.objects.exclude(schema_name=get_public_schema_name())
        for tenant in tenants:
            plan_info = obtener_plan_tenant(tenant)
            susc = Suscripcion.objects.filter(tenant=tenant).order_by('-fecha_creacion').first()
            if not susc:
                session_id = f"cs_catalog_{tenant.schema_name}_init"
                susc = Suscripcion.objects.create(
                    tenant=tenant,
                    plan=plan_info['id'],
                    email_cliente=tenant.email_contacto or f"admin@{tenant.schema_name}.com",
                    nombre_centro=tenant.nombre,
                    nombre_admin='Administrador',
                    stripe_session_id=session_id,
                    estado='activa' if tenant.activo else 'cancelada',
                    fecha_activacion=tenant.fecha_creacion,
                )
            registrar_factura_saas_idempotente(
                suscripcion=susc,
                stripe_session_id=susc.stripe_session_id,
                estado='PAGADA' if susc.estado == 'activa' else 'PENDIENTE',
            )


def obtener_dashboard_saas() -> dict:
    """HU-55 (a): Consola SuperAdmin con MRR total en USD, distribución de planes y facturas."""
    asegurar_suscripciones_catalogo()

    with schema_context(get_public_schema_name()):
        tenants = list(Tenant.objects.exclude(schema_name=get_public_schema_name()).order_by('nombre'))
        mrr_usd = 0.0
        activos = 0
        distribucion_planes = {'basico': 0, 'profesional': 0, 'empresarial': 0}
        centros_detalle = []

        for t in tenants:
            susc = Suscripcion.objects.filter(tenant=t).order_by('-fecha_creacion').first()
            plan_info = obtener_plan_tenant(t)
            plan_id = plan_info['id']
            precio_usd = round(plan_info['precio_mensual'] / 100.0, 2)
            estado_susc = (susc.estado if susc else ('activa' if t.activo else 'cancelada')).upper()

            if t.activo and estado_susc == 'ACTIVA':
                activos += 1
                mrr_usd += precio_usd
                distribucion_planes[plan_id] = distribucion_planes.get(plan_id, 0) + 1

            facturas = list(
                FacturaSaaS.objects.filter(tenant=t).order_by('-fecha_emision')[:10]
            )
            ultima_fact = facturas[0] if facturas else None
            uso_cupos = obtener_uso_cupos_tenant(t)

            centros_detalle.append({
                'tenant_id': str(t.id),
                'schema_name': t.schema_name,
                'nombre': t.nombre,
                'email_contacto': t.email_contacto,
                'activo': t.activo,
                'plan_id': plan_id,
                'plan_nombre': plan_info['nombre'],
                'precio_mensual_usd': precio_usd,
                'estado_suscripcion': estado_susc,
                'stripe_session_id': susc.stripe_session_id if susc else None,
                'fecha_renovacion': ultima_fact.fecha_renovacion.isoformat() if (ultima_fact and ultima_fact.fecha_renovacion) else None,
                'cupos': uso_cupos,
                'facturas': [
                    {
                        'id': str(f.id),
                        'numero_factura': f.numero_factura,
                        'plan': f.plan,
                        'monto_usd': float(f.monto_usd),
                        'estado': f.estado,
                        'stripe_session_id': f.stripe_session_id,
                        'fecha_emision': timezone.localtime(f.fecha_emision).strftime('%Y-%m-%d %H:%M'),
                        'fecha_renovacion': f.fecha_renovacion.isoformat() if f.fecha_renovacion else None,
                    }
                    for f in facturas
                ],
            })

        total_facturado_usd = sum(
            float(f.monto_usd) for f in FacturaSaaS.objects.filter(estado='PAGADA')
        )

        return {
            'moneda': 'USD',
            'kpis': {
                'mrr_usd': round(mrr_usd, 2),
                'arr_estimado_usd': round(mrr_usd * 12, 2),
                'total_facturado_usd': round(total_facturado_usd, 2),
                'tenants_totales': len(tenants),
                'tenants_activos': activos,
                'distribucion_planes': distribucion_planes,
            },
            'planes_catalogo': list(PLANES.values()),
            'tenants': centros_detalle,
        }


def actualizar_suscripcion_tenant(tenant_id, nuevo_plan: str | None = None, nuevo_estado: str | None = None, usuario=None) -> dict:
    """Permite al SuperAdmin cambiar plan o suspender/reactivar una suscripción SaaS."""
    with schema_context(get_public_schema_name()):
        with transaction.atomic():
            tenant = Tenant.objects.get(pk=tenant_id)
            susc = Suscripcion.objects.filter(tenant=tenant).order_by('-fecha_creacion').first()

            if nuevo_plan:
                plan_key = _normalizar_plan_id(nuevo_plan)
                if plan_key not in PLANES:
                    raise ValueError(f"Plan inválido '{nuevo_plan}'.")
                tenant.plan = plan_key.upper()
                if susc:
                    susc.plan = plan_key

            if nuevo_estado:
                est_norm = nuevo_estado.lower().strip()
                if est_norm not in ('activa', 'pendiente', 'cancelada', 'expirada'):
                    raise ValueError('Estado inválido. Use: activa, pendiente, cancelada o expirada.')
                tenant.activo = (est_norm == 'activa')
                if susc:
                    susc.estado = est_norm

            tenant.save()
            if susc:
                susc.save()

            log_event(
                action='SUSCRIPCION_SAAS_ACTUALIZADA',
                modulo='CU26_SAAS',
                tenant=tenant.schema_name,
                user=getattr(usuario, 'email', None),
                nuevo_plan=tenant.plan,
                activo=tenant.activo,
            )

            return {
                'tenant_id': str(tenant.id),
                'nombre': tenant.nombre,
                'plan': tenant.plan,
                'activo': tenant.activo,
                'estado_suscripcion': (susc.estado if susc else ('activa' if tenant.activo else 'cancelada')).upper(),
            }
