#!/usr/bin/env python3
"""Herramienta para estimar el ancho del lomo en centímetros."""

from __future__ import annotations

import argparse
from typing import Final

# Constante derivada de la guía de KDP para interiores en blanco y negro (papel de 55 lb).
# 0.002252 pulgadas por hoja * 2.54 cm/pulgada / 2 páginas por hoja = 0.00286104 cm por página.
PAGE_THICKNESS_CM: Final[float] = 0.00286104


def calculate_spine_width(page_count: int, page_thickness_cm: float = PAGE_THICKNESS_CM) -> float:
    """Devuelve el ancho estimado del lomo en centímetros para ``page_count`` páginas."""
    if page_count <= 0:
        raise ValueError("El número de páginas debe ser mayor que cero.")

    return page_count * page_thickness_cm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Calcula el ancho del lomo en centímetros usando las pautas estándar de KDP "
            "para interiores en blanco y negro."
        )
    )
    parser.add_argument(
        "pages",
        type=int,
        help="Número total de páginas del libro (debe ser mayor que cero).",
    )
    parser.add_argument(
        "--page-thickness",
        type=float,
        default=PAGE_THICKNESS_CM,
        help=(
            "Grosor por página en centímetros. Usa 0.0033 para color (página más gruesa) "
            "o el valor recomendado por tu imprenta. Valor por defecto: %(default)s."
        ),
    )
    parser.add_argument(
        "--precision",
        type=int,
        default=2,
        help="Número de decimales para mostrar en la salida (por defecto: %(default)s).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    width_cm = calculate_spine_width(args.pages, args.page_thickness)
    formatted = f"{width_cm:.{args.precision}f}"
    print(f"Ancho del lomo: {formatted} cm")


if __name__ == "__main__":
    main()
