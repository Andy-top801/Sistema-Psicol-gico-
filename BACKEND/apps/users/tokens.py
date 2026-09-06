from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import Usuario

CODE_SEPARATOR = '.'


def make_reset_code(user: Usuario) -> str:
    """HU-10: código de un solo uso para recuperar la contraseña.

    Combina uid + token de Django (`PasswordResetTokenGenerator`) en un
    único código copiable, ya que la app móvil no implementa deep-linking
    (fuera de alcance de esta fase). El token expira solo por
    `PASSWORD_RESET_TIMEOUT` (30 min) y queda invalidado automáticamente en
    cuanto la contraseña cambia, sin necesidad de guardarlo en la base de
    datos.
    """
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f'{uidb64}{CODE_SEPARATOR}{token}'


def resolve_reset_code(code: str) -> Usuario | None:
    """Devuelve el Usuario si el código es válido (existe, no expiró y no
    fue usado); None en cualquier otro caso."""
    try:
        uidb64, token = code.split(CODE_SEPARATOR, 1)
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (ValueError, TypeError, OverflowError, Usuario.DoesNotExist):
        return None

    if not default_token_generator.check_token(user, token):
        return None
    return user
