---
trigger: always_on
---

# Lineamientos de estructura editorial

## Orden de secciones
Todo manuscrito debe contener, en este orden:
1. Prólogo
2. Introducción metodológica
3. Cronología
4. Capítulos 1–N (número definido en `.env` como `CHAPTERS_NUMBER`, ejemplo: 20)
5. Epílogo analítico
6. Glosario
7. Dramatis personae
8. Fuentes

## Capítulos
- Número de capítulos obligatorios definido en `.env` (`CHAPTERS_NUMBER`).
- Cada capítulo comienza con `# Capítulo N: [título]`.
- Cada capítulo debe tener subtítulos internos (`##`, `###`) cuando la extensión lo justifique.

## Extensión
- Meta global: mínimo de palabras definido en `.env` (`TOTAL_WORDS`, ejemplo: 51,000 palabras / ~120 páginas).
- Cada capítulo: meta aproximada de palabras definida en `.env` (`WORDS_PER_CHAPTER`, ejemplo: 2,550 palabras), ajustada en el plan.
- Ajustar longitud inmediatamente al terminar cada capítulo.

## Archivos
- Cada sección en su propio `.md`.
- Al final, concatenar en `bios/x/La biografía de X.md`.