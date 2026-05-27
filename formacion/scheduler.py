import logging
import os
import sys
import threading
from datetime import datetime, timedelta

import pandas as pd
from django.conf import settings
from django.utils import timezone

from .models import polivalencia

logger = logging.getLogger(__name__)

DEFAULT_EXPORT_DIR = r"D:\Matriz de polivalencia"
TARGET_DAY = 1
TARGET_HOUR = 1
TARGET_MINUTE = 0

_EXCLUDED_COMMANDS = {
    "makemigrations",
    "migrate",
    "collectstatic",
    "test",
    "check",
    "shell",
    "createsuperuser",
    "dbshell",
    "flush",
    "loaddata",
    "dumpdata",
}

_scheduler_started = False
_scheduler_lock = threading.Lock()
_stop_event = threading.Event()


def _build_polivalencia_dataframe():
    registros = polivalencia.objects.all().values()
    df = pd.DataFrame(registros)

    if "id" in df.columns:
        df = df.drop(columns=["id"])

    for col in df.columns:
        if pd.api.types.is_datetime64tz_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    def _limpiar_valor(valor):
        if isinstance(valor, (int, float)):
            if valor in [1, 2, 3]:
                return valor
            return ""
        return valor

    return df.map(_limpiar_valor)


def exportar_polivalencia_diaria(destino_dir=DEFAULT_EXPORT_DIR):
    os.makedirs(destino_dir, exist_ok=True)
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"TPL-708_Matriz_de_Polivalencia_{fecha_hoy}.xlsx"
    ruta_salida = os.path.join(destino_dir, nombre_archivo)

    df = _build_polivalencia_dataframe()
    with pd.ExcelWriter(ruta_salida, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Polivalencia")

    return ruta_salida


def _seconds_until_next_run(day=TARGET_DAY, hour=TARGET_HOUR, minute=TARGET_MINUTE):
    now = timezone.localtime()
    next_run = now.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
    if next_run <= now:
        if now.month == 12:
            next_run = next_run.replace(year=now.year + 1, month=1)
        else:
            next_run = next_run.replace(month=now.month + 1)
    return max(int((next_run - now).total_seconds()), 1)


def _should_start_scheduler():
    if os.environ.get("DISABLE_POLIVALENCIA_SCHEDULER") == "1":
        return False

    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command in _EXCLUDED_COMMANDS:
        return False

    if settings.DEBUG and command == "runserver" and os.environ.get("RUN_MAIN") != "true":
        return False

    return True


def _scheduler_loop():
    while not _stop_event.is_set():
        wait_seconds = _seconds_until_next_run()
        interrupted = _stop_event.wait(wait_seconds)
        if interrupted:
            break

        try:
            ruta = exportar_polivalencia_diaria()
            logger.info("Exportacion diaria de polivalencia creada: %s", ruta)
        except Exception:
            logger.exception("Error al exportar la matriz de polivalencia programada")


def iniciar_scheduler_polivalencia():
    global _scheduler_started

    if not _should_start_scheduler():
        return

    with _scheduler_lock:
        if _scheduler_started:
            return

        worker = threading.Thread(
            target=_scheduler_loop,
            name="polivalencia-daily-export",
            daemon=True,
        )
        worker.start()
        _scheduler_started = True
