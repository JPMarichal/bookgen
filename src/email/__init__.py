"""Compatibilidad temporal para el antiguo paquete `src.email`.

Se carga explícitamente el paquete estándar `email` desde la ruta de la
biblioteca de Python y se reexporta, de modo que cualquier dependencia que
importe `src.email` obtenga la versión oficial del lenguaje. Usa
`src.mailer` para las funcionalidades propias de BookGen.
"""

import importlib.util as _importlib_util
import os as _os
import sys as _sys
import warnings as _warnings

_warnings.warn(
    "El paquete 'src.email' está en desuso; usa 'src.mailer'.",
    DeprecationWarning,
    stacklevel=2,
)

_stdlib_dir = _os.path.dirname(_os.__file__)
_email_pkg_path = _os.path.join(_stdlib_dir, "email")
_email_init_path = _os.path.join(_email_pkg_path, "__init__.py")

_spec = _importlib_util.spec_from_file_location(
    name="email",
    location=_email_init_path,
    submodule_search_locations=[_email_pkg_path],
)

if _spec is None or _spec.loader is None:
    raise ImportError("No se pudo localizar el paquete estándar 'email'.")

_stdlib_email = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_stdlib_email)

globals().update(_stdlib_email.__dict__)
_sys.modules[__name__] = _stdlib_email

del _stdlib_email
del _spec
del _importlib_util
del _email_pkg_path
del _email_init_path
del _stdlib_dir
del _os
del _sys
del _warnings
