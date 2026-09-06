from datetime import time, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.tenants.models import Centro, Dominio
from apps.users.models import (
    Rol, Permiso, Paciente, Psicologo, Especialidad,
    DisponibilidadPsicologo, Cita, AlertaPriorizacion, Teleconsulta,
)
from apps.users.serializers import TeleconsultaSerializer

DEMO_PASSWORD = 'Demo1234!'

# Nombres de rol canónicos (sin acento, PascalCase). El frontend y los permisos
# normalizan, así que la ortografía exacta no es crítica, pero se mantiene estable.
ROLES = {
    'admincentro': ('AdminCentro', 'Administrador del centro', True),
    'coordinador': ('Coordinador', 'Coordinador clínico', True),
    'psicologo': ('Psicologo', 'Psicólogo tratante', False),
    'recepcionista': ('Recepcionista', 'Recepción y turnos', True),
    'paciente': ('Paciente', 'Paciente del centro', False),
}


class Command(BaseCommand):
    help = 'Inicializa tenants (public + 2 centros demo) y datos semilla.'

    def handle(self, *args, **options):
        User = get_user_model()
        self.stdout.write('Inicializando SIGEPSI…')

        # ── 1. Esquema público + superadmin ──────────────────────
        public, created = Centro.objects.get_or_create(
            schema_name='public', defaults={'name': 'SIGEPSI Plataforma'}
        )
        if created:
            Dominio.objects.get_or_create(domain='localhost', tenant=public, is_primary=True)
        with schema_context('public'):
            if not User.objects.filter(email='admin@sigepsi.com').exists():
                User.objects.create_superuser(
                    username='admin@sigepsi.com',
                    email='admin@sigepsi.com',
                    password='admin123',
                )
                self.stdout.write(self.style.SUCCESS('  superadmin: admin@sigepsi.com / admin123'))

        # ── 2. Centro demo "Sanamente" ───────────────────────────
        self._seed_centro(
            schema='clinica_demo',
            name='Clínica Psicológica Sanamente',
            domain='sanamente.localhost',
            prefix='sanamente',
        )

        # ── 3. Segundo centro "Centro Norte" (para probar aislamiento) ──
        self._seed_centro(
            schema='clinica_norte',
            name='Centro Psicológico Norte',
            domain='norte.localhost',
            prefix='norte',
        )

        self.stdout.write(self.style.SUCCESS('¡Seed completado!'))
        self.stdout.write(f'  Contraseña de todos los usuarios de centro: {DEMO_PASSWORD}')

    # ---------------------------------------------------------------
    def _seed_centro(self, schema, name, domain, prefix):
        User = get_user_model()
        centro, created = Centro.objects.get_or_create(
            schema_name=schema, defaults={'name': name}
        )
        if created:
            Dominio.objects.get_or_create(domain=domain, tenant=centro, is_primary=True)
            self.stdout.write(self.style.SUCCESS(f'Centro "{name}" ({domain})'))

        with schema_context(schema):
            # Roles
            roles = {}
            for key, (rn, desc, is_staff) in ROLES.items():
                roles[key], _ = Rol.objects.get_or_create(name=rn, defaults={'description': desc})
            Permiso.objects.get_or_create(name='Ver citas', codename='read_citas')

            # Usuarios del personal
            admin = self._user(User, f'admin@{prefix}.com', 'Admin', name.split()[-1],
                               roles['admincentro'], is_staff=True)
            coord = self._user(User, f'coordinador@{prefix}.com', 'Coord', 'Clínico',
                               roles['coordinador'], is_staff=True)
            recep = self._user(User, f'recepcion@{prefix}.com', 'Recep', 'Turnos',
                               roles['recepcionista'], is_staff=True)
            psico_user = self._user(User, f'psicologo@{prefix}.com', 'Dra. Carla', 'Rivas',
                                    roles['psicologo'], is_staff=False)
            pac_user = self._user(User, f'paciente@{prefix}.com', 'Ana', 'Martínez',
                                  roles['paciente'], is_staff=False)

            # Especialidades
            esp_tcc, _ = Especialidad.objects.get_or_create(name=f'Terapia Cognitivo-Conductual ({prefix})')
            esp_ans, _ = Especialidad.objects.get_or_create(name=f'Ansiedad y estrés ({prefix})')

            # Psicólogo + disponibilidad Lun–Vie 08:00–18:00
            psico, _ = Psicologo.objects.get_or_create(
                usuario=psico_user,
                defaults={'modalidad_atencion': Psicologo.ModalidadAtencion.MIXTA, 'activo': True},
            )
            psico.especialidades.set([esp_tcc, esp_ans])
            for dia in range(1, 6):
                DisponibilidadPsicologo.objects.get_or_create(
                    psicologo=psico, dia_semana=dia,
                    hora_inicio=time(8, 0), hora_fin=time(18, 0),
                    defaults={'activo': True},
                )

            # Paciente
            paciente, _ = Paciente.objects.get_or_create(
                usuario=pac_user,
                defaults={'genero': 'Femenino', 'direccion': f'Calle {prefix} 123'},
            )

            # Citas (dentro de la disponibilidad)
            base = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
            while base.isoweekday() > 5:
                base += timedelta(days=1)
            c1, _ = Cita.objects.get_or_create(
                paciente=paciente, psicologo=psico,
                fecha_hora=base + timedelta(days=1),
                defaults={'duracion_minutos': 60, 'estado': Cita.Estado.CONFIRMADA,
                          'modalidad': Cita.Modalidad.PRESENCIAL,
                          'motivo': 'Sesión de seguimiento'},
            )
            c2, _ = Cita.objects.get_or_create(
                paciente=paciente, psicologo=psico,
                fecha_hora=base + timedelta(days=2, hours=2),
                defaults={'duracion_minutos': 50, 'estado': Cita.Estado.RESERVADA,
                          'modalidad': Cita.Modalidad.VIRTUAL,
                          'motivo': 'Primera teleconsulta'},
            )

            # Teleconsulta para la cita virtual
            if not hasattr(c2, 'teleconsulta'):
                ser = TeleconsultaSerializer()
                ser.create({'cita': c2})

            # Alerta de priorización
            AlertaPriorizacion.objects.get_or_create(
                paciente=paciente,
                tipo=AlertaPriorizacion.Tipo.INASISTENCIA,
                defaults={'descripcion': 'Faltó a 2 sesiones consecutivas sin aviso.',
                          'estado': AlertaPriorizacion.Estado.PENDIENTE},
            )

    def _user(self, User, email, first, last, rol, is_staff):
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create_user(
                username=email, email=email, password=DEMO_PASSWORD,
                first_name=first, last_name=last, is_staff=is_staff,
            )
            self.stdout.write(f'    usuario: {email}')
        user.roles.add(rol)
        return user
