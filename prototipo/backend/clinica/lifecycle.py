from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError


def lock_history(history_id):
    from clinica.models import HistoriaClinica
    return HistoriaClinica.objects.select_for_update().get(pk=history_id)


def ensure_history_open(history):
    if getattr(history, 'cerrada', False):
        raise ValidationError({'historia_clinica': 'El expediente está cerrado y no admite mutaciones clínicas.'})
    return history


def history_for_object(obj):
    from clinica.models import HistoriaClinica
    if isinstance(obj, HistoriaClinica):
        return obj
    history = getattr(obj, 'historia_clinica', None)
    if history is None and getattr(obj, 'tarea', None) is not None:
        history = obj.tarea.historia_clinica
    if history is None and getattr(obj, 'cita', None) is not None:
        history = getattr(obj.cita.paciente, 'historia_clinica', None)
    return history


def ensure_object_history_open(obj):
    history = history_for_object(obj)
    if history is not None:
        ensure_history_open(lock_history(history.pk))
    return history


def linked_psychologist(user, history):
    role = (getattr(getattr(user, 'rol', None), 'nombre', '') or '').lower()
    psico = getattr(user, 'perfil_psicologo', None)
    if not getattr(user, 'is_authenticated', False) or 'psic' not in role or not psico:
        raise PermissionDenied('Se requiere un psicólogo autenticado.')
    if history.psicologo_apertura_id == psico.id:
        return psico
    if history.paciente.citas.filter(psicologo=psico).exists():
        return psico
    raise PermissionDenied('El psicólogo no está vinculado a esta historia clínica.')


def assert_no_future_pending_appointments(history):
    from agenda.models import Cita
    if Cita.objects.filter(
        paciente=history.paciente,
        fecha__gte=timezone.localdate(),
        estado__in=('PROGRAMADA', 'CONFIRMADA'),
    ).exists():
        raise ValidationError({'historia_clinica': 'No se puede cerrar: existen citas futuras programadas o confirmadas.'})


def close_history(*, history_id, user, tipo_derivacion, motivo_clinico, logros_alcanzados, recomendaciones_mantenimiento, **extra):
    from clinica.models import DerivacionCaso
    supported = {'CIERRE_ALTA', 'DESERCION', 'MUTUO_ACUERDO'}
    if tipo_derivacion not in supported:
        raise ValidationError({'tipo_derivacion': 'Tipo de cierre inválido.'})
    required = {
        'motivo_clinico': motivo_clinico,
        'logros_alcanzados': logros_alcanzados,
        'recomendaciones_mantenimiento': recomendaciones_mantenimiento,
    }
    missing = [name for name, value in required.items() if not str(value or '').strip()]
    if missing:
        raise ValidationError({name: 'Este campo es obligatorio para cerrar el caso.' for name in missing})
    with transaction.atomic():
        history = lock_history(history_id)
        linked_psychologist(user, history)
        if history.cerrada:
            raise ValidationError({'historia_clinica': 'El expediente ya está cerrado.'})
        assert_no_future_pending_appointments(history)
        values = {
            'historia_clinica': history,
            'psicologo_emisor': user.perfil_psicologo,
            'tipo_derivacion': tipo_derivacion,
            'motivo_clinico': motivo_clinico.strip(),
            'logros_alcanzados': logros_alcanzados.strip(),
            'recomendaciones_mantenimiento': recomendaciones_mantenimiento.strip(),
            **extra,
        }
        event = DerivacionCaso.objects.create(**values)
        history.cerrada = True
        history.fecha_cierre = timezone.now()
        history.save(update_fields=('cerrada', 'fecha_cierre', 'fecha_actualizacion'))
        return event


def reactivate_history(*, history_id, user, reason):
    from clinica.models import DerivacionCaso
    reason = (reason or '').strip()
    if not reason:
        raise ValidationError({'motivo_clinico': 'El motivo de reactivación es obligatorio.'})
    with transaction.atomic():
        history = lock_history(history_id)
        linked_psychologist(user, history)
        if not history.cerrada:
            raise ValidationError({'historia_clinica': 'El expediente ya está abierto.'})
        event = DerivacionCaso.objects.create(
            historia_clinica=history,
            psicologo_emisor=user.perfil_psicologo,
            tipo_derivacion='REACTIVACION',
            motivo_clinico=reason,
        )
        history.cerrada = False
        history.fecha_cierre = None
        history.save(update_fields=('cerrada', 'fecha_cierre', 'fecha_actualizacion'))
        return event
