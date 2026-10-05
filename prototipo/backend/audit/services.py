import json
import base64
import hashlib
import os
import threading
from datetime import date, datetime
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone


_file_lock = threading.Lock()


def _cipher():
    key = getattr(settings, "AUDIT_LOG_KEY", "")
    if not key:
        raise ImproperlyConfigured("AUDIT_LOG_KEY debe estar configurada")
    try:
        derived_key = base64.urlsafe_b64encode(
            hashlib.sha256(key.encode("utf-8")).digest()
        )
        return Fernet(derived_key)
    except (ValueError, TypeError, UnicodeError) as exc:
        raise ImproperlyConfigured("AUDIT_LOG_KEY no es un secreto valido") from exc


def _log_path(log_date):
    directory = Path(settings.BASE_DIR) / "logs" / "audit"
    directory.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(directory, 0o700)
    except OSError:
        pass
    path = directory / f"audit-{log_date.isoformat()}.log.enc"
    if not path.exists():
        path.touch(mode=0o600)
    else:
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    return path


def write_event(event):
    now = timezone.localtime(timezone.now())
    payload = {
        "timestamp": now.isoformat(),
        **event,
    }
    encrypted_line = _cipher().encrypt(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    )
    with _file_lock:
        with _log_path(now.date()).open("ab") as log_file:
            log_file.write(encrypted_line + b"\n")


def log_event(**kwargs):
    """Alias para registrar eventos en la bitácora cifrada."""
    try:
        write_event(kwargs)
    except Exception as e:
        print(f"[AUDIT WARN] No se pudo escribir evento: {e}")


def read_events(log_date=None):
    """
    CU5 Pasos 5b a 8b:
    5b: abrir_archivo_cifrado(audit-YYYY-MM-DD.log.enc, modo=0600)
    6b: stream_lineas_cifradas_bytes()
    7b: decrypt_payload_fernet(linea_cifrada, derived_aes_key)
    8b: json_payload_en_claro(ip, user_id, action, timestamp_bolivia)
    """
    cipher = _cipher()
    directory = Path(settings.BASE_DIR) / "logs" / "audit"
    if not directory.exists():
        return []

    # CU5 Paso 5b: abrir_archivo_cifrado en modo seguro
    paths = [_log_path(log_date)] if log_date else sorted(directory.glob("audit-*.log.enc"))
    events = []
    for path in paths:
        if not path.exists():
            continue
        # CU5 Paso 6b: stream_lineas_cifradas_bytes
        for line_number, line in enumerate(path.read_bytes().splitlines(), start=1):
            if not line:
                continue
            try:
                # CU5 Pasos 7b y 8b: decrypt_payload_fernet & json_payload_en_claro
                events.append(json.loads(cipher.decrypt(line).decode("utf-8")))
            except (InvalidToken, json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise ValueError(
                    f"No se pudo descifrar la bitacora {path.name}, linea {line_number}"
                ) from exc
    return events


def parse_date(value):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("La fecha debe tener formato YYYY-MM-DD") from exc
