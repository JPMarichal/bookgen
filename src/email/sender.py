"""Compatibilidad temporal.

`src.email.sender` fue renombrado a `src.mailer.sender`. Este módulo solo existe
para avisar a quienes aún lo importan.
"""

raise ImportError(
    "El módulo 'src.email.sender' fue renombrado a 'src.mailer.sender'. "
    "Actualiza tus importaciones."
)
