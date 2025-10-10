"""Compatibilidad temporal para el antiguo paquete `src.email`.

Este módulo ahora actúa como *proxy* del paquete estándar `email` de Python
para evitar romper dependencias externas que esperan importarlo. La lógica del
remitente de correo de BookGen se movió a `src.mailer`.
"""

from importlib import import_module as _import_module

_stdlib_email = _import_module("email")

# Replicar atributos públicos del paquete estándar para mantener compatibilidad
for _name in dir(_stdlib_email):
    if _name.startswith("__") and _name not in {"__path__", "__all__", "__spec__"}:
        continue
    globals()[_name] = getattr(_stdlib_email, _name)

__all__ = getattr(_stdlib_email, "__all__", [
    name for name in dir(_stdlib_email) if not name.startswith("_")
])

# Asegurar que los submódulos del paquete estándar sigan resolviéndose
if hasattr(_stdlib_email, "__path__"):
    __path__ = _stdlib_email.__path__  # type: ignore[name-defined]

del _stdlib_email
del _import_module
