from django.contrib.auth import get_user_model
from axes.signals import user_locked_out

from .models import Notificacion


def _notify_superusers(message):
    User = get_user_model()
    for user in User.objects.filter(is_superuser=True, is_active=True):
        Notificacion.objects.create(
            usuario=user,
            mensaje=message,
            creado_por=user,
        )


@user_locked_out.connect
def on_user_locked_out(sender, request, credentials=None, **kwargs):
    username = (credentials or {}).get("username")
    user_display = username or "(desconocido)"
    ip_display = request.META.get("REMOTE_ADDR", "(sin ip)")
    ua = request.META.get("HTTP_USER_AGENT", "(sin user-agent)")
    message = (
        "Bloqueo por intentos fallidos de login. "
        f"Usuario: {user_display}. IP: {ip_display}. UA: {ua}"
    )
    _notify_superusers(message)
