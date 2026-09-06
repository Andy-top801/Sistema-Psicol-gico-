from django.core.management.base import BaseCommand
from apps.tenants.models import Centro, Dominio
from apps.users.models import Rol, Permiso, Paciente
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

class Command(BaseCommand):
    help = 'Inicializa el sistema creando el Tenant Público, una Clínica de prueba y usuarios semilla.'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando configuración base del sistema...')
        User = get_user_model()

        # ---------------------------------------------------------
        # 1. ESQUEMA PÚBLICO (GLOBAL ADMIN)
        # ---------------------------------------------------------
        tenant_public, created_pub = Centro.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'SIGEPSI Admin Global'}
        )
        if created_pub:
            Dominio.objects.get_or_create(domain='localhost', tenant=tenant_public, is_primary=True)
            self.stdout.write(self.style.SUCCESS('Tenant "public" creado con éxito.'))
        
        with schema_context('public'):
            if not User.objects.filter(email='admin@sigepsi.com').exists():
                User.objects.create_superuser(
                    username='admin@sigepsi.com',
                    email='admin@sigepsi.com',
                    password='admin123',
                )
                self.stdout.write(self.style.SUCCESS('Administrador global creado: admin@sigepsi.com / admin123'))

        # ---------------------------------------------------------
        # 2. ESQUEMA CLÍNICA DE PRUEBA
        # ---------------------------------------------------------
        tenant_demo, created_demo = Centro.objects.get_or_create(
            schema_name='clinica_demo',
            defaults={'name': 'Clínica Psicológica Sanamente'}
        )
        if created_demo:
            Dominio.objects.get_or_create(domain='sanamente.localhost', tenant=tenant_demo, is_primary=True)
            self.stdout.write(self.style.SUCCESS('Clínica de prueba "Sanamente" creada (Esquema: clinica_demo).'))
        
        # Poblar datos DENTRO de la clínica de prueba
        with schema_context('clinica_demo'):
            # Crear Permisos Básicos
            permiso_leer_citas, _ = Permiso.objects.get_or_create(name='Ver Citas', codename='read_citas')
            permiso_editar_exp, _ = Permiso.objects.get_or_create(name='Editar Expediente', codename='edit_expediente')
            
            # Crear Roles
            rol_psicologo, _ = Rol.objects.get_or_create(name='Psicólogo', description='Personal de salud')
            rol_psicologo.permisos.add(permiso_leer_citas, permiso_editar_exp)
            
            rol_paciente, _ = Rol.objects.get_or_create(name='Paciente', description='Usuario de la plataforma')
            rol_paciente.permisos.add(permiso_leer_citas)

            # Crear Usuario Psicólogo
            if not User.objects.filter(email='psicologo@sanamente.com').exists():
                user_psico = User.objects.create_user(
                    username='psicologo@sanamente.com',
                    email='psicologo@sanamente.com',
                    password='password123',
                    first_name='Dr. Carlos',
                    last_name='López'
                )
                user_psico.roles.add(rol_psicologo)
                self.stdout.write(self.style.SUCCESS('Psicólogo demo creado: psicologo@sanamente.com / password123'))
            
            # Crear Usuario Paciente
            if not User.objects.filter(email='paciente@sanamente.com').exists():
                user_pac = User.objects.create_user(
                    username='paciente@sanamente.com',
                    email='paciente@sanamente.com',
                    password='password123',
                    first_name='Ana',
                    last_name='Martínez'
                )
                user_pac.roles.add(rol_paciente)
                Paciente.objects.get_or_create(usuario=user_pac)
                self.stdout.write(self.style.SUCCESS('Paciente demo creado: paciente@sanamente.com / password123'))

        self.stdout.write(self.style.SUCCESS('¡Población de datos semilla (Seed) completada con éxito!'))
