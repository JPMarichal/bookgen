
---
description: Pipeline para generar biografías KDP en batch: planificación, redacción, concatenación y exportación a Word.
trigger: manual
auto_execution_mode: 3
---

# Workflow unificado para biografías KDP

## Cuándo ejecutar este workflow

Este workflow tiene `trigger: manual`, lo que significa que **debe iniciarse explícitamente** cuando:
- Se inicia un nuevo personaje de la colección (primera vez que se trabaja en esa biografía)
- Se requiere generar una biografía completa desde cero
- El usuario solicita explícitamente procesar un personaje específico

**Prerequisitos para ejecutar:**
- Archivo de colección disponible en `colecciones/` con lista de personajes
- Herramientas instaladas: Python 3, Pandoc
- Plantilla de Word en `wordTemplate/reference.docx`
- Acceso a fuentes bibliográficas verificables online

**Diferencia con reglas `always_on`**: Las reglas con `trigger: always_on` (como `automation.md`) están activas en todo momento y proporcionan guías técnicas que aplican durante cualquier tarea. Este workflow manual requiere activación intencional para procesar biografías completas.

## Objetivo
Pipeline completo para generar biografías KDP desde la selección del personaje hasta la exportación final a Word, asegurando cumplimiento de estándares editoriales y técnicos.

## Entradas requeridas
- Archivo de colección en `colecciones/` con lista de personajes.
- Acceso a fuentes bibliográficas verificables.
- Herramientas instaladas: Python 3, Pandoc, plantilla Word en `wordTemplate/reference.docx`.

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
- [automation.md](automation.md) - Detalles de scripts concat.py y Pandoc (trigger: always_on)
- [research.md](research.md) - Estándares de investigación y fuentes
- [structure.md](structure.md) - Estructura editorial obligatoria (trigger: always_on)
- [quality.md](quality.md) - Control de calidad y validaciones
- [style.md](style.md) - Lineamientos técnicos de estilo
- [literaryStyle.md](literaryStyle.md) - Estilo emocional y literario
- [lenght.md](lenght.md) - Validación de longitudes con check_lengths.py

## Glosario de términos
- **Batch**: Conjunto de capítulos o secciones redactadas de forma continua sin pausas, para mantener coherencia narrativa y tono.
- **Iteración**: Ciclo de redacción-validación-ajuste aplicado a cada capítulo o sección individual.
- **Loop de verificación**: Proceso repetitivo de validar longitudes, formato y calidad hasta cumplir todos los criterios antes de concatenar.
- **Concatenación**: Unión automática de todos los archivos `.md` en orden fijo para generar el manuscrito completo.
- **Normalización**: Conversión del nombre del personaje a formato estándar (minúsculas, guiones bajos) para nombres de directorios y scripts.
- **Trigger manual**: Workflow que requiere activación explícita del usuario, usado para procesos completos de inicio a fin.
- **Always_on**: Reglas que están siempre activas y proporcionan guías técnicas durante cualquier tarea.