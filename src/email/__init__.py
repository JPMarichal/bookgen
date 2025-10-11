"""Compatibilidad temporal para el antiguo paquete `src.email`.

Se delega completamente al paquete estándar `email` para mantener
compatibilidad con dependencias externas. Usa `src.mailer` para las
funciones propias de BookGen.
"""

from importlib import import_module as _import_module
import sys as _sys
import warnings as _warnings

_warnings.warn(
    "El paquete 'src.email' está en desuso; usa 'src.mailer'.",
    DeprecationWarning,
    stacklevel=2,
)

_stdlib_email = _import_module("email")
_sys.modules[__name__] = _stdlib_email

del _stdlib_email
del _import_module
del _sys
del _warnings
