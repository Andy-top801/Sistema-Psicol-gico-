# ==============================================================================
# MÓDULO: subscriptions/email_utils.py
# DESCRIPCIÓN: Utilidades para enviar correos de bienvenida con credenciales
#              temporales al nuevo administrador del centro creado vía suscripción.
# PUNTO 7+8: Modelo SaaS en la nube — Web/Móvil con pasarela de pagos Stripe
# ==============================================================================
import socket
from django.conf import settings
from django.core.mail import send_mail


def enviar_correo_bienvenida(
    email: str,
    nombre: str,
    nombre_centro: str,
    password_temporal: str,
    plan: str,
):
    """
    Envía un correo de bienvenida al administrador del nuevo centro
    con sus credenciales temporales de acceso.
    """
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:4200').rstrip('/')
    login_url = f'{frontend_url}/login'

    subject = f'🎉 ¡Bienvenido a SIGEPSI! — Tu centro "{nombre_centro}" está listo'

    message_plain = (
        f'Hola {nombre},\n\n'
        f'¡Tu suscripción al plan {plan.upper()} de SIGEPSI ha sido activada exitosamente!\n\n'
        f'Tu centro "{nombre_centro}" ya está configurado y listo para usar.\n\n'
        f'═══════════════════════════════════════\n'
        f'  CREDENCIALES DE ACCESO\n'
        f'═══════════════════════════════════════\n'
        f'  📧 Email: {email}\n'
        f'  🔑 Contraseña temporal: {password_temporal}\n'
        f'  🌐 Acceder: {login_url}\n'
        f'═══════════════════════════════════════\n\n'
        f'⚠️ IMPORTANTE: Por seguridad, deberás cambiar tu contraseña\n'
        f'   en tu primer inicio de sesión.\n\n'
        f'Pasos para acceder:\n'
        f'  1. Visita {login_url}\n'
        f'  2. Selecciona el modo "Centro Psicológico"\n'
        f'  3. Elige tu centro "{nombre_centro}"\n'
        f'  4. Ingresa las credenciales proporcionadas\n'
        f'  5. Cambia tu contraseña cuando el sistema te lo solicite\n\n'
        f'Si necesitas ayuda, contáctanos respondiendo a este correo.\n\n'
        f'— Equipo SIGEPSI\n'
    )

    # Imprimir en consola/logs para auditoría y pruebas en desarrollo
    print('=' * 80)
    print(f'🎉 [NUEVA SUSCRIPCIÓN] Centro: {nombre_centro} | Plan: {plan}')
    print(f'📧 Email admin: {email}')
    print(f'🔑 Contraseña temporal: {password_temporal}')
    print(f'🌐 Login: {login_url}')
    print('=' * 80)

    # Intentar envío SMTP con timeout para no bloquear en entornos sin SMTP
    default_sock_timeout = socket.getdefaulttimeout()
    try:
        socket.setdefaulttimeout(5)
        from_email = (
            getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            or getattr(settings, 'EMAIL_HOST_USER', None)
        )
        send_mail(
            subject=subject,
            message=message_plain,
            from_email=from_email,
            recipient_list=[email],
            fail_silently=False,
        )
        print(f'✅ Correo de bienvenida enviado exitosamente a {email}')
    except Exception as smtp_err:
        print(
            f'ℹ️ [AVISO] Envío SMTP omitido o bloqueado ({smtp_err}). '
            f'Credenciales disponibles en consola/logs.'
        )
    finally:
        socket.setdefaulttimeout(default_sock_timeout)
