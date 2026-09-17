# ==============================================================================
# MÓDULO: subscriptions/views.py
# DESCRIPCIÓN: Endpoints REST para el flujo de suscripción SaaS con Stripe.
#              Gestiona la creación de sesiones de checkout, verificación de pagos
#              y auto-provisión de tenants con usuario administrador.
# PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
# ==============================================================================
import re
import string
import secrets
import stripe
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from subscriptions.models import Suscripcion
from subscriptions.plans import get_plan, get_all_plans
from subscriptions.serializers import (
    PlanSerializer,
    CreateCheckoutSerializer,
    VerifySessionSerializer,
)
from subscriptions.email_utils import enviar_correo_bienvenida
from tenants.models import Tenant, Dominio
from accounts.models import Usuario, Rol
from accounts.utils import seed_tenant_roles_and_permissions


def _generar_password_temporal(nombre_centro: str = "", nombre_admin: str = "", email: str = "") -> str:
    """
    Genera una contraseña temporal única y robusta derivada de:
      1. Raíz del nombre del centro psicológico
      2. Iniciales de la persona/administrador
      3. Número aleatorio criptográfico (4 dígitos)
      4. Carácter especial aleatorio
    Garantiza que cada centro y usuario tengan una contraseña temporal completamente
    distinta y no predecible, evitando colisiones o patrones repetitivos.
    """
    # 1. Extraer y limpiar raíz del centro
    centro_clean = nombre_centro or ""
    for orig, rep in [
        ('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n'),
        ('Á', 'A'), ('É', 'E'), ('Í', 'I'), ('Ó', 'O'), ('Ú', 'U'), ('Ñ', 'N')
    ]:
        centro_clean = centro_clean.replace(orig, rep)
    palabras_centro = re.findall(r'[A-Za-z0-9]+', centro_clean)

    genericos = {'centro', 'gabinete', 'clinica', 'consultorio', 'instituto'}
    if len(palabras_centro) > 1 and palabras_centro[0].lower() in genericos:
        stem = palabras_centro[1].capitalize()[:8]
    elif palabras_centro:
        stem = palabras_centro[0].capitalize()[:8]
    else:
        stem = "Centro"

    if len(stem) < 3:
        stem = stem.capitalize() + "Psi"

    # 2. Iniciales de la persona / admin
    admin_clean = nombre_admin or ""
    for orig, rep in [('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n')]:
        admin_clean = admin_clean.replace(orig, rep)
    palabras_admin = re.findall(r'[A-Za-z0-9]+', admin_clean)

    if palabras_admin and palabras_admin[0].lower() not in {'administrador', 'admin'}:
        iniciales = ''.join(w[0].upper() for w in palabras_admin[:2])
    elif email and '@' in email:
        prefijo_email = email.split('@')[0]
        prefijo_clean = re.sub(r'[^a-zA-Z]', '', prefijo_email)
        iniciales = (prefijo_clean[:2].upper() if len(prefijo_clean) >= 2 else (prefijo_clean + 'A').upper())
    else:
        iniciales = secrets.choice(string.ascii_uppercase) + secrets.choice(string.ascii_uppercase)

    # 3. Número aleatorio criptográfico (1000 - 9999)
    numero = secrets.randbelow(9000) + 1000

    # 4. Símbolo especial aleatorio
    simbolo = secrets.choice('!@#$%&*+')

    return f"{stem}{iniciales}{numero}{simbolo}"


def _generar_slug(nombre: str) -> str:
    """Genera un slug válido a partir del nombre del centro."""
    slug = nombre.lower().strip()
    slug = re.sub(r'[áàäâ]', 'a', slug)
    slug = re.sub(r'[éèëê]', 'e', slug)
    slug = re.sub(r'[íìïî]', 'i', slug)
    slug = re.sub(r'[óòöô]', 'o', slug)
    slug = re.sub(r'[úùüû]', 'u', slug)
    slug = re.sub(r'[ñ]', 'n', slug)
    slug = re.sub(r'[^a-z0-9]+', '_', slug)
    slug = slug.strip('_')
    if not slug:
        slug = 'centro'
    # Asegurar unicidad
    base_slug = slug
    counter = 1
    while Tenant.objects.filter(slug=slug).exists():
        slug = f'{base_slug}_{counter}'
        counter += 1
    return slug


class PlansListView(APIView):
    """
    GET /api/subscriptions/plans/
    Retorna la lista de planes de suscripción disponibles para la landing page.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        connection.set_schema_to_public()
        planes = get_all_plans()
        serializer = PlanSerializer(planes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateCheckoutView(APIView):
    """
    POST /api/subscriptions/create-checkout/
    Crea una sesión de Stripe Checkout para el plan seleccionado.

    Flujo:
      1. Valida datos del cliente (email, nombre_centro, plan)
      2. Crea sesión en Stripe Checkout con metadata
      3. Registra la suscripción como 'pendiente'
      4. Retorna la URL de checkout para redirigir al cliente
    """
    permission_classes = [AllowAny]

    def post(self, request):
        connection.set_schema_to_public()
        serializer = CreateCheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan_id = serializer.validated_data['plan']
        email = serializer.validated_data['email']
        nombre_centro = serializer.validated_data['nombre_centro']
        nombre_admin = serializer.validated_data.get('nombre_admin', 'Administrador')

        plan = get_plan(plan_id)
        if not plan:
            return Response(
                {'error': 'Plan no encontrado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verificar que no exista ya un centro con ese email activo
        if Suscripcion.objects.filter(email_cliente=email, estado='activa').exists():
            return Response(
                {'error': 'Ya existe una suscripción activa con este correo electrónico.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Configurar Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:4200').rstrip('/')

        try:
            # Crear sesión de Stripe Checkout
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                mode='subscription',
                customer_email=email,
                line_items=[
                    {
                        'price_data': {
                            'currency': plan['moneda'],
                            'unit_amount': plan['precio_mensual'],
                            'recurring': {'interval': 'month'},
                            'product_data': {
                                'name': f'SIGEPSI — Plan {plan["nombre"]}',
                                'description': f'Suscripción mensual al plan {plan["nombre"]} para centro psicológico.',
                            },
                        },
                        'quantity': 1,
                    }
                ],
                metadata={
                    'plan': plan_id,
                    'nombre_centro': nombre_centro,
                    'nombre_admin': nombre_admin,
                    'email': email,
                },
                success_url=f'{frontend_url}/checkout-success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{frontend_url}/landing',
            )

            # Registrar suscripción pendiente
            Suscripcion.objects.create(
                plan=plan_id,
                email_cliente=email,
                nombre_centro=nombre_centro,
                nombre_admin=nombre_admin,
                stripe_session_id=checkout_session.id,
                estado='pendiente',
            )

            return Response(
                {
                    'checkout_url': checkout_session.url,
                    'session_id': checkout_session.id,
                },
                status=status.HTTP_200_OK,
            )

        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Error al crear sesión de pago: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerifySessionView(APIView):
    """
    POST /api/subscriptions/verify-session/
    Verifica el pago de Stripe Checkout y auto-provisiona el tenant.

    Flujo:
      1. Recibe session_id de Stripe
      2. Verifica payment_status == 'paid' con la API de Stripe
      3. Verifica idempotencia (no procesar dos veces)
      4. Genera contraseña temporal
      5. Crea Tenant + Schema + Dominio + Centro + Roles + Admin
      6. Marca admin con must_change_password = True
      7. Envía correo de bienvenida con credenciales
      8. Retorna datos de éxito
    """
    permission_classes = [AllowAny]

    def post(self, request):
        connection.set_schema_to_public()
        serializer = VerifySessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data['session_id']

        # Buscar suscripción pendiente
        try:
            suscripcion = Suscripcion.objects.get(stripe_session_id=session_id)
        except Suscripcion.DoesNotExist:
            return Response(
                {'error': 'Sesión de pago no encontrada.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Idempotencia: si ya fue activada, retornar éxito
        if suscripcion.estado == 'activa' and suscripcion.tenant:
            return Response(
                {
                    'success': True,
                    'centro_nombre': suscripcion.nombre_centro,
                    'email': suscripcion.email_cliente,
                    'password_temporal': suscripcion.password_temporal,
                    'tenant_slug': suscripcion.tenant.slug,
                    'mensaje': 'Su centro ya fue creado anteriormente.',
                    'ya_procesado': True,
                },
                status=status.HTTP_200_OK,
            )

        # Verificar pago con Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Error al verificar la sesión de pago: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if checkout_session.payment_status != 'paid':
            return Response(
                {
                    'error': 'El pago aún no ha sido confirmado.',
                    'payment_status': checkout_session.payment_status,
                },
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        # === Auto-provisionar Tenant ===
        plan_id = suscripcion.plan
        email = suscripcion.email_cliente
        nombre_centro = suscripcion.nombre_centro
        nombre_admin = suscripcion.nombre_admin
        slug = _generar_slug(nombre_centro)
        password_temporal = _generar_password_temporal(
            nombre_centro=nombre_centro,
            nombre_admin=nombre_admin,
            email=email,
        )

        try:
            with transaction.atomic():
                # 1. Crear Tenant (auto_create_schema = True genera el schema)
                tenant = Tenant.objects.create(
                    nombre=nombre_centro,
                    slug=slug,
                    schema_name=slug,
                    email_contacto=email,
                    plan=plan_id.upper(),
                    activo=True,
                )

                # 2. Crear dominio asociado
                Dominio.objects.create(
                    domain=f'{slug}.localhost',
                    tenant=tenant,
                    is_primary=True,
                )

                # 3. Inicializar datos en el nuevo esquema
                with schema_context(tenant.schema_name):
                    from core.models import Centro

                    Centro.objects.create(
                        nombre=nombre_centro,
                        direccion='',
                        telefono='',
                        email=email,
                        horarios_atencion={
                            'lunes_viernes': '08:00 - 18:00',
                            'sabado': '08:00 - 13:00',
                        },
                        configuracion={
                            'cancelacion_horas_anticipacion': 24,
                            'duracion_sesion_minutos': 50,
                        },
                    )

                    # 4. Sembrar roles y permisos
                    roles_map = seed_tenant_roles_and_permissions()
                    rol_admin = roles_map[Rol.ADMIN_CENTRO]

                    # 5. Crear usuario administrador con contraseña temporal
                    admin_user = Usuario.objects.create_user(
                        email=email,
                        password=password_temporal,
                        nombre=nombre_admin,
                        apellido='Centro',
                        rol=rol_admin,
                        activo=True,
                    )
                    # 6. Marcar que debe cambiar contraseña en primer login
                    admin_user.must_change_password = True
                    admin_user.save()

                # 7. Actualizar suscripción
                suscripcion.tenant = tenant
                suscripcion.estado = 'activa'
                suscripcion.password_temporal = password_temporal
                suscripcion.fecha_activacion = timezone.now()
                suscripcion.stripe_customer_id = checkout_session.customer
                suscripcion.save()

        except Exception as e:
            return Response(
                {'error': f'Error al crear el centro: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 8. Enviar correo de bienvenida con credenciales
        enviar_correo_bienvenida(
            email=email,
            nombre=nombre_admin,
            nombre_centro=nombre_centro,
            password_temporal=password_temporal,
            plan=plan_id,
        )

        return Response(
            {
                'success': True,
                'centro_nombre': nombre_centro,
                'email': email,
                'password_temporal': password_temporal,
                'tenant_slug': slug,
                'mensaje': (
                    f'¡Centro "{nombre_centro}" creado exitosamente! '
                    f'Se enviaron las credenciales de acceso a {email}.'
                ),
                'login_url': f'{getattr(settings, "FRONTEND_URL", "http://localhost:4200")}/login',
            },
            status=status.HTTP_201_CREATED,
        )
