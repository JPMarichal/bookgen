---
trigger: always_on
---

# Control de calidad editorial

## Objetivo
Garantizar que cada capítulo y el manuscrito completo cumplan con los estándares de calidad editorial: longitud adecuada, coherencia narrativa, rigor histórico y formato Markdown correcto antes de la concatenación final.

## Entradas requeridas
- Archivos `.md` de cada capítulo y sección en `bios/x/`.
- Plan de trabajo en `esquemas/X - plan de trabajo.md` con metas de palabras por capítulo.
- Archivo `bios/x/control/longitudes.csv` generado durante la planificación.

## Pasos automáticos
1. Al terminar cada capítulo, ejecutar validación de longitud:
   ```
   python check_lengths.py x
   ```
   (donde `x` es el nombre normalizado del personaje)
2. Revisar archivo `bios/x/control/longitudes.csv` para verificar porcentajes de cumplimiento.
3. Ajustar capítulo si no alcanza ±5% de la meta definida.
4. Antes de concatenar, validar que el total del manuscrito supere 51,000 palabras.

## Validaciones/Logs
- **Por capítulo**: Verificar que alcance la meta de palabras definida (±5% de la meta, ~2,550 palabras promedio).
- **Flujo narrativo**: Coherente, sin contradicciones internas o con otros capítulos.
- **Redundancia**: Ausencia de repeticiones innecesarias de información.
- **Contexto**: Inclusión adecuada de contexto histórico, sociopolítico y cultural.
- **Antes de concatenar**:
  - Manuscrito completo supera 51,000 palabras (meta mínima global).
  - Todas las secciones presentes en el orden correcto (prólogo, introducción, cronología, 20 capítulos, epílogo, glosario, dramatis personae, fuentes).
  - Encabezados usan jerarquía correcta (`#`, `##`, `###`).
  - Tablas y listas en Markdown están bien formadas.
  - No hay archivos faltantes en `bios/x/`.

## Fallbacks/Escalada
- Si un capítulo no alcanza la meta de palabras: ampliar con más contexto histórico, detalles verificables, descripciones sensoriales y emotivas. Mantener rigor académico.
- Si el manuscrito completo no alcanza 51,000 palabras: identificar capítulos más cortos y expandirlos según disponibilidad de fuentes.
- Si hay errores de formato Markdown: corregir sintaxis de tablas (`| col |`), listas (`-` o `*`), o encabezados antes de concatenar.
- Si faltan secciones: completar redacción de archivos faltantes antes de continuar.

## Relacionados
- [lenght.md](lenght.md) - Validación de longitudes con check_lengths.py
- [structure.md](structure.md) - Estructura y orden de secciones
- [style.md](style.md) - Lineamientos de estilo narrativo
- [literaryStyle.md](literaryStyle.md) - Estilo literario y emocional
- [automation.md](automation.md) - Script de concatenación
