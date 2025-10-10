"""Compatibilidad temporal para el antiguo paquete `src.email`.

Este paquete se renombró a `src.mailer` para evitar conflictos con la
biblioteca estándar `email`.  Importa desde `src.mailer` en su lugar.
"""

raise ImportError(
    "El paquete 'src.email' fue renombrado a 'src.mailer'. Actualiza las "
    "importaciones a 'from src.mailer.sender import EmailSender'."
)
