from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import PasswordChangeStatus


class PasswordExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if self._should_skip_path(request):
                return self.get_response(request)

            status, _ = PasswordChangeStatus.objects.get_or_create(user=request.user)
            expiration_days = getattr(settings, "PASSWORD_EXPIRATION_DAYS", 90)
            expires_at = status.last_password_change + timedelta(days=expiration_days)

            if timezone.now() >= expires_at:
                messages.info(
                    request,
                    "Tu contraseña ha caducado. Debes renovarla para continuar.",
                )
                return redirect("password_change")

        return self.get_response(request)

    def _should_skip_path(self, request):
        path = request.path
        static_url = getattr(settings, "STATIC_URL", "/static/")
        media_url = getattr(settings, "MEDIA_URL", "/media/")

        if static_url and path.startswith(static_url):
            return True
        if media_url and path.startswith(media_url):
            return True
        if path.startswith("/admin/"):
            return True

        allowed = {
            reverse("login"),
            reverse("logout"),
            reverse("logout_message"),
            reverse("password_change"),
            reverse("password_change_done"),
        }
        return path in allowed
