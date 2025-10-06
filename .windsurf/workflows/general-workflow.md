---
description: Pipeline para generar biografías KDP en batch: planificación, redacción, concatenación y exportación a Word.
auto_execution_mode: 3
---

# Workflow de biografías KDP

## Config
chapters: 20
total_words: 51000
words_per_chapter: 2550

## Pasos
1. Selección → tomar primer personaje sin ✅ en `colecciones/`, normalizar nombre.
2. Fuentes → crear `esquemas/X - fuentes.md` con bibliografía verificable (APA/Chicago + URLs). Todas las fuentes deben ser online, existir y devolver 200 (no 404, 403, 500 u otros códigos de error).
3. Plan → crear `esquemas/X - plan de trabajo.md` con:
   - 20 capítulos (título, descripción, meta de palabras).  
   - Longitud planificada para todas las secciones (prólogo, introducción, cronología, capítulos, epílogo, glosario, dramatis-personae, fuentes).  
   - Crear `bios/x/control/longitudes.csv` con esas metas iniciales.
4. Redacción batch → generar en `bios/x/` todos los archivos en orden, de un tirón (sin pausas, sin reportes, sin interacción del usuario):  
   - `prologo.md`  
   - `introduccion.md`  
   - `cronologia.md`  
   - `capitulo-01.md` … `capitulo-20.md`  
   - `epilogo.md`  
   - `glosario.md`  
   - `dramatis-personae.md`  
   - `fuentes.md`
   Organiza la ejecución en batches, por medio de una lista de tareas, para vencer tus limitantes, de modo que puedas hacer la ejecución de manera ininterrumpida, pasando de manera inmediata de un batch a otro.
5. Loop de verificación y ajustes →  
   - Ejecutar: `python check_lengths.py x`  (ejemplo: python check_lengths.py joseph_stalin) al principio de cada iteración. Desde la primera iteración, organiza una lista de tareas, para que puedas seguirlas sin interrupción.
   - El script actualiza `bios/x/control/longitudes.csv` con longitud real y % cumplimiento.  
   - Si alguna sección < 100%, la IA se enfoca en mejorar solo esa sección hasta que alcance 100%, entonces pasa a la siguiente iteración sin interrumpirte, sin solicitar interacción, sin brindar reporte, hasta terminar el loop.
   - Repetir iteraciones hasta que todas estén ≥100%. 
6. Concatenación → ejecutar `python concat.py -personaje "x"` → `bios/x/concat/La biografía de X.md`.
7. Word → `pandoc "bios\x\La biografía de X.md" -o "bios\x\doc\concat\La biografía de X.docx" --reference-doc="wordTemplate\reference.docx"`.
8. Cierre → marcar personaje con ✅ en `colecciones/`.