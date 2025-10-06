---
trigger: always_on
---

# Flujo técnico de automatización

## Directorios
- colecciones/ → lista de personajes.
- esquemas/ → planes de trabajo y fuentes.
- bios/ → capítulos y secciones.
- docx/ → versiones finales en Word.

## Scripts
- concat.py concatena en orden fijo:
  - prólogo, introducción, cronología, capítulos 1–15, epílogo, glosario, dramatis personae, fuentes.

## Conversión
- Usar Pandoc con plantilla de Word:
  pandoc "bios\x\La biografía de X.md" -o "bios\x\La biografía de X.docx" --reference-doc="wordTemplate\reference.docx"

## Marcado
- Una vez generado el libro, marcar personaje con ✅ en colecciones.txt.
