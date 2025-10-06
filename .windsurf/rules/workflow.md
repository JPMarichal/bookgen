---
trigger: always_on
description: Pipeline para generar biografías KDP en batch: planificación, redacción, concatenación y exportación a Word.
---

## Changelog

**2025-10-06**
- Este documento ha sido consolidado como la única fuente de verdad del workflow general para biografías KDP.
- Se ha eliminado `.windsurf/workflows/general-workflow.md` y todas las referencias deben apuntar a este archivo.
- La información de ambos archivos ha sido revisada y unificada aquí, sin pérdida de detalles ni secciones.
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

## Validaciones automatizables

### Checklist de verificación completa

Un agente debe verificar cada fase del workflow:

**Fase 1: Selección y preparación**
- [ ] Verificar que el archivo de colección en `colecciones/` exista
- [ ] Verificar que haya al menos un personaje sin ✅
- [ ] Verificar normalización del nombre del personaje (minúsculas, guiones bajos)

**Fase 2: Investigación de fuentes**
- [ ] Verificar que `esquemas/X - fuentes.md` exista y contenga mínimo 40-60 fuentes
- [ ] Verificar que todas las URLs devuelvan código HTTP 200
- [ ] Verificar que las fuentes usen formato académico consistente (APA o Chicago)
- [ ] Verificar clasificación de fuentes (primarias, secundarias, terciarias)

**Fase 3: Planificación**
- [ ] Verificar que `esquemas/X - plan de trabajo.md` exista
- [ ] Verificar que el plan contenga exactamente 20 capítulos
- [ ] Verificar que cada capítulo tenga título, descripción y meta de palabras
- [ ] Verificar que `bios/x/control/longitudes.csv` exista con metas por sección
- [ ] Verificar que la suma de metas alcance mínimo 51,000 palabras

**Fase 4: Redacción**
- [ ] Verificar que el directorio `bios/x/` exista
- [ ] Verificar que se generen los 25 archivos `.md` requeridos
- [ ] Verificar que cada capítulo inicie con `# Capítulo N: [título]`

**Fase 5: Validación de longitudes**
- [ ] Ejecutar `python check_lengths.py <personaje>` después de cada batch
- [ ] Verificar que todas las secciones alcancen ≥100% de cumplimiento
- [ ] Verificar que el total supere 51,000 palabras
- [ ] Registrar resultado en log

**Fase 6: Concatenación**
- [ ] Ejecutar `python concat.py -personaje "<personaje>"`
- [ ] Verificar que se genere `bios/x/La biografía de X.md`
- [ ] Verificar que no haya errores ni warnings de archivos faltantes

**Fase 7: Conversión a Word**
- [ ] Verificar que `wordTemplate/reference.docx` exista
- [ ] Ejecutar comando Pandoc
- [ ] Verificar que se genere `docx/x/La biografía de X.docx`
- [ ] Verificar que el archivo Word sea accesible y tenga formato correcto

**Fase 8: Cierre**
- [ ] Marcar personaje con ✅ en archivo de colección
- [ ] Verificar que todos los logs se hayan guardado
- [ ] Registrar fecha y hora de finalización

### Evidencia a conservar

Para cada fase del workflow, adjuntar:

- **Fase 1**: Nombre del personaje seleccionado y ruta normalizada
- **Fase 2**: `esquemas/X - fuentes.md` y log de verificación HTTP
- **Fase 3**: `esquemas/X - plan de trabajo.md` y `bios/x/control/longitudes.csv`
- **Fase 4**: Lista de archivos generados en `bios/x/`
- **Fase 5**: CSV final y logs de todas las iteraciones de `check_lengths.py`
- **Fase 6**: `bios/x/La biografía de X.md` y log de concat.py
- **Fase 7**: `docx/x/La biografía de X.docx` y log de Pandoc
- **Fase 8**: Captura del archivo de colección con ✅ marcado

### Scripts a ejecutar

1. **Verificación de fuentes**:
   ```bash
   grep -Eo "https?://[^\s]+" "esquemas/X - fuentes.md" | \
     while read url; do \
       echo "$url: $(curl -s -o /dev/null -w '%{http_code}' "$url")"; \
     done > esquemas/logs/workflow-sources-<personaje>-<fecha>.log
   ```

2. **Validación de longitudes**:
   ```bash
   python check_lengths.py <personaje> 2>&1 | tee bios/x/logs/workflow-lengths-<fecha>.log
   ```

3. **Concatenación**:
   ```bash
   python concat.py -personaje "<personaje>" 2>&1 | tee bios/x/logs/workflow-concat-<fecha>.log
   ```

4. **Conversión a Word**:
   ```bash
   pandoc "bios/x/La biografía de X.md" \
     -o "docx/x/La biografía de X.docx" \
     --reference-doc="wordTemplate/reference.docx" \
     2>&1 | tee bios/x/logs/workflow-pandoc-<fecha>.log
   ```

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
- [length.md](length.md) - Validación de longitudes con check_lengths.py
- [GLOSARIO.md](../GLOSARIO.md) - Glosario unificado de términos del proyecto

## Glosario de términos
- **Batch**: Conjunto de capítulos o secciones redactadas de forma continua sin pausas, para mantener coherencia narrativa y tono.
- **Iteración**: Ciclo de redacción-validación-ajuste aplicado a cada capítulo o sección individual.
- **Loop de verificación**: Proceso repetitivo de validar longitudes, formato y calidad hasta cumplir todos los criterios antes de concatenar.
- **Concatenación**: Unión automática de todos los archivos `.md` en orden fijo para generar el manuscrito completo.
- **Normalización**: Conversión del nombre del personaje a formato estándar (minúsculas, guiones bajos) para nombres de directorios y scripts.
- **Trigger manual**: Workflow que requiere activación explícita del usuario, usado para procesos completos de inicio a fin.
- **Always_on**: Reglas que están siempre activas y proporcionan guías técnicas durante cualquier tarea.