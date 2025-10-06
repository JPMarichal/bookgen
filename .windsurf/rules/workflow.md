---
trigger: manual
---

# Flujo de trabajo completo para biografías KDP

## Objetivo
Establecer el flujo de trabajo completo desde selección del personaje hasta publicación, definiendo todas las fases: selección, investigación, planificación, redacción, concatenación, conversión a Word y cierre. Garantizar que cada biografía cumpla con los estándares editoriales y técnicos para KDP.

## Entradas requeridas
- Archivo de colección en `colecciones/` con lista de personajes.
- Acceso a fuentes bibliográficas verificables.
- Herramientas instaladas: Python 3, Pandoc, plantilla de Word en `wordTemplate/reference.docx`.

## Pasos automáticos

### 1. Selección del personaje
1.1. Tomar nombre desde archivo de colección en `colecciones/`.
1.2. Una vez completado el libro, marcar nombre con ✅ en el archivo de colección.

### 2. Investigación y fuentes
2.1. Crear `esquemas/X - fuentes.md` con bibliografía verificable en formato académico (APA o Chicago).
2.2. Incluir al menos dominio o URL completa para fuentes online.
2.3. Compilar mínimo 2-3 fuentes por capítulo (40-60 fuentes total).
2.4. Clasificar fuentes en primarias, secundarias y terciarias.
2.5. Las fuentes deben estar completas antes de iniciar redacción.

### 3. Planificación
3.1. Crear `esquemas/X - plan de trabajo.md` con:
- 20 capítulos con título descriptivo.
- Descripción breve del contenido de cada capítulo.
- Meta de palabras equilibrada por capítulo (~2,550 palabras promedio).
- Ajustes según disponibilidad de documentación (ej. infancia con menos fuentes puede tener meta menor).
3.2. Crear directorio `bios/x/` para el personaje.
3.3. Crear archivo `bios/x/control/longitudes.csv` con metas esperadas por sección.

### 4. Redacción en batches
4.1. Planear batches cuidadosamente para escribir sin interrupciones hasta concatenación.
4.2. Una vez aprobado el plan, crear estructura completa de archivos en `bios/x/`:
- prologo.md
- introduccion.md
- cronologia.md
- capitulo-01.md hasta capitulo-20.md
- epilogo.md
- glosario.md
- dramatis-personae.md
- fuentes.md

4.3. Redactar en batches todos los archivos hasta el final, sin pausas ni resúmenes intermedios.
4.4. Cada capítulo debe alcanzar la meta definida en el plan (~2,550 palabras promedio).
4.5. Aplicar estilo narrativo-literario, académico cuando corresponda, siempre envolvente.
4.6. No usar citas directas. Narración corrida en voz propia.
4.7. Recursos permitidos: tablas en Markdown, listas con `-` o `*`, mapas como descripciones en prosa.

### 5. Validación de longitudes
5.1. Al terminar cada capítulo, ejecutar:
```
python check_lengths.py x
```
5.2. Revisar `bios/x/control/longitudes.csv` para verificar cumplimiento de metas (±5%).
5.3. Ajustar capítulos que no cumplan meta antes de continuar.

### 6. Concatenación automática
6.1. Una vez completados todos los archivos, ejecutar script oficial de concatenación:
```
python concat.py -personaje "nombre_personaje"
```
6.2. Script concatena archivos en orden fijo:
- prologo.md
- introduccion.md
- cronologia.md
- capitulo-01.md hasta capitulo-20.md
- epilogo.md
- glosario.md
- dramatis-personae.md
- fuentes.md
6.3. Archivo final generado: `bios/x/La biografía de X.md`

### 7. Conversión a Word
7.1. Convertir con Pandoc usando plantilla de Word:
```
pandoc "bios\x\La biografía de X.md" -o "bios\x\La biografía de X.docx" --reference-doc="wordTemplate\reference.docx"
```
7.2. Mover el archivo `.docx` a `docx/x/La biografía de X.docx`.

### 8. Cierre
8.1. Marcar con ✅ al personaje en el archivo de colección correspondiente.
8.2. Verificar que archivo Word final esté en `docx/x/`.

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
- [automation.md](automation.md) - Detalles de scripts concat.py y Pandoc
- [research.md](research.md) - Estándares de investigación y fuentes
- [structure.md](structure.md) - Estructura editorial obligatoria
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