---
description: Pipeline para generar biografías KDP en batch: planificación, redacción, concatenación y exportación a Word.
trigger: manual
auto_execution_mode: 3
---

# Workflow unificado para biografías KDP

**Nota:** Este archivo es una copia de `workflow.md` ubicado en `rules/`. Ambos archivos contienen el mismo workflow. Se mantiene aquí por compatibilidad con estructuras previas del proyecto.

## Cuándo ejecutar este workflow
Pipeline completo para generar biografías KDP desde la selección del personaje hasta la exportación final a Word, asegurando cumplimiento de estándares editoriales y técnicos.

## Entradas requeridas
- Archivo de colección en `colecciones/` con lista de personajes.
- Acceso a fuentes bibliográficas verificables.
- Herramientas instaladas: Python 3, Pandoc, plantilla Word en `wordTemplate/reference.docx`.
- Variables de configuración desde `.env`:
  - `CHAPTERS_NUMBER`: Número de capítulos (por defecto: 20)
  - `TOTAL_WORDS`: Meta global de palabras (por defecto: 51000)
  - `WORDS_PER_CHAPTER`: Meta de palabras por capítulo (por defecto: 2550)

## Pasos (orden estricto)
1. **Selección**: Tomar el primer personaje sin ✅ en `colecciones/`, normalizar nombre para rutas.
2. **Fuentes**: Crear `esquemas/X - fuentes.md` con bibliografía (APA/Chicago + URLs válidas). No iniciar redacción si faltan fuentes.
3. **Planificación**: Crear `esquemas/X - plan de trabajo.md` con 20 capítulos (título, descripción, meta palabras), y `bios/x/control/longitudes.csv` con metas por sección.
4. **Redacción batch**: Generar en `bios/x/` todos los archivos en orden (prologo.md, introduccion.md, cronologia.md, capitulo-01.md ... capitulo-20.md, epilogo.md, glosario.md, dramatis-personae.md, fuentes.md). Redactar en batches, sin pausas ni reportes intermedios.
5. **Validación de longitudes**: Ejecutar `python check_lengths.py x` tras cada batch. Revisar y ajustar hasta que todas las secciones cumplan ≥100% de meta (±5%).
6. **Concatenación**: Ejecutar `python concat.py -personaje "x"`. El archivo final debe ser `bios/x/La biografía de X.md`.
7. **Conversión a Word**: Ejecutar `pandoc "bios/x/La biografía de X.md" -o "docx/x/La biografía de X.docx" --reference-doc="wordTemplate/reference.docx"`.
8. **Cierre**: Marcar personaje con ✅ en `colecciones/` y verificar que el Word final esté en `docx/x/`.

## Triggers y modos de ejecución
- `trigger: manual`: El workflow debe ejecutarse manualmente cuando se inicia un nuevo personaje o cuando un agente detecta que hay un personaje sin procesar (sin ✅) en el archivo de colección.
- `auto_execution_mode: 3`: Permite operación desatendida, pero requiere checklist previa:
  - Fuentes completas (`esquemas/X - fuentes.md` existe y es válida).
  - Plan aprobado (`esquemas/X - plan de trabajo.md` con metas y capítulos).
  - Estructura de directorios y archivos creada.
  - Herramientas instaladas y accesibles.
- Un agente automatizado debe:
  1. Verificar checklist anterior.
  2. Si todo está listo, ejecutar el workflow completo sin intervención.
  3. Si falta algún prerequisito, detenerse y reportar el estado.

## Validaciones/Logs
- **Fuentes completas**: `esquemas/X - fuentes.md` existe antes de redactar.
- **Plan aprobado**: `esquemas/X - plan de trabajo.md` con 20 capítulos y metas definidas.
- **Estructura de directorios**: `bios/x/` con todos los archivos `.md` necesarios.
- **Longitudes**: Cada capítulo cumple ±5% de meta; total supera 51,000 palabras.
- **Concatenación exitosa**: Archivo `bios/x/La biografía de X.md` generado sin errores.
- **Conversión Word**: Archivo `docx/x/La biografía de X.docx` con formato aplicado.
- **Personaje marcado**: ✅ aparece junto al nombre en archivo de colección.

## Fallbacks/Escalada
- Si faltan fuentes: no iniciar redacción hasta completar investigación mínima.
- Si un capítulo no alcanza meta: expandir con contexto, detalles, descripciones sensoriales (ver literaryStyle.md).
- Si manuscrito no alcanza 51,000 palabras: identificar capítulos prioritarios para expansión.
- Si concat.py reporta archivos faltantes: completar archivos antes de generar Word.
- Si Pandoc falla: revisar sintaxis Markdown (tablas, encabezados) en archivo concatenado.

## Relacionados
- [automation.md](../rules/automation.md) - Detalles de scripts concat.py y Pandoc
- [research.md](../rules/research.md) - Estándares de investigación y fuentes
- [structure.md](../rules/structure.md) - Estructura editorial obligatoria
- [quality.md](../rules/quality.md) - Control de calidad y validaciones
- [style.md](../rules/style.md) - Lineamientos técnicos de estilo
- [literaryStyle.md](../rules/literaryStyle.md) - Estilo emocional y literario
- [length.md](../rules/length.md) - Validación de longitudes con check_lengths.py

## Glosario de términos
- **Batch**: Conjunto de capítulos o secciones redactadas de forma continua sin pausas, para mantener coherencia narrativa y tono.
- **Iteración**: Ciclo de redacción-validación-ajuste aplicado a cada capítulo o sección individual.
- **Loop de verificación**: Proceso repetitivo de validar longitudes, formato y calidad hasta cumplir todos los criterios antes de concatenar.
- **Concatenación**: Unión automática de todos los archivos `.md` en orden fijo para generar el manuscrito completo.
- **Normalización**: Conversión del nombre del personaje a formato estándar (minúsculas, guiones bajos) para nombres de directorios y scripts.
