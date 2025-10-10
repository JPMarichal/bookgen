# Glosario de términos del proyecto bookgen

Este glosario unifica la terminología utilizada en todos los documentos de reglas y workflows para evitar ambigüedades y facilitar la comprensión tanto por agentes automáticos como por humanos.

## Términos operativos

### Batch
Conjunto de capítulos o secciones redactadas de forma continua sin pausas, para mantener coherencia narrativa y tono. Un batch típico puede incluir 5-10 capítulos consecutivos.

### Iteración
Ciclo de redacción-validación-ajuste aplicado a cada capítulo o sección individual. Incluye: redactar → verificar longitud → ajustar si es necesario.

### Loop de verificación
Proceso repetitivo de validar longitudes, formato y calidad hasta cumplir todos los criterios antes de concatenar. Se ejecuta mediante `check_lengths.py` en ciclos hasta que todas las secciones alcancen ≥100% de cumplimiento.

### Concatenación
Unión automática de todos los archivos `.md` en orden fijo para generar el manuscrito completo. Ejecutada por el script `concat.py`, produce un único archivo markdown con todas las secciones.

### Normalización
Conversión del nombre del personaje a formato estándar (minúsculas, guiones bajos, sin acentos) para nombres de directorios y scripts. Ejemplo: "José Martí" → "jose_marti".

## Términos de workflow

### Trigger manual
Workflow que requiere activación explícita del usuario, usado para procesos completos de inicio a fin. Ejemplo: iniciar una biografía nueva.

### Always_on
Reglas que están siempre activas y proporcionan guías técnicas durante cualquier tarea. Ejemplo: `development.md`, `business-rules.md`.

### Auto_execution_mode
Nivel de autonomía permitido para ejecución desatendida:
- **Nivel 1**: Requiere confirmación en cada paso
- **Nivel 2**: Requiere confirmación solo en decisiones críticas
- **Nivel 3**: Ejecución completamente autónoma sin intervención

### Escalada
Proceso de reportar un problema que no puede resolverse automáticamente y requiere revisión humana. Incluye registrar detalles en logs específicos y, si es necesario, abrir issues en el repositorio.

## Términos técnicos

### Personaje
Individuo biografiado. El término se usa de forma genérica independientemente del género. Cada personaje tiene un directorio dedicado en `bios/x/` donde `x` es el nombre normalizado.

### Sección
Archivo markdown individual que forma parte del manuscrito. Tipos de secciones:
- **Estructurales**: prólogo, introducción, cronología, epílogo
- **Narrativas**: capítulo-01 a capítulo-20
- **Complementarias**: glosario, dramatis-personae, fuentes

### CSV de control
Archivo `bios/x/control/longitudes.csv` que registra el progreso de cada sección:
- `seccion`: Nombre del archivo sin extensión
- `longitud_esperada`: Meta de palabras según plan
- `longitud_real`: Palabras actuales en el archivo
- `porcentaje`: Cumplimiento calculado (longitud_real/longitud_esperada × 100)

### Spine width / Ancho del lomo
Grosor del lomo del libro impreso, calculado en centímetros usando el script `spine_width.py` basado en el número total de páginas y tipo de papel.

## Términos de calidad

### Rigor académico
Uso exclusivo de datos verificables desde fuentes confiables, sin invención de hechos ni citas textuales directas. Todo contenido histórico debe rastrearse a las fuentes listadas.

### Tono narrativo-literario
Estilo de escritura que equilibra precisión histórica con narrativa envolvente, emotiva y ligeramente poética. No debe ser seco como un paper académico, pero tampoco novelesco sin sustento.

### Coherencia narrativa
Ausencia de contradicciones internas entre capítulos, mantenimiento de línea temporal consistente, y desarrollo lógico de eventos y motivaciones.

### Fuentes verificables
Fuentes bibliográficas que cumplen todos estos criterios:
- Devuelven código HTTP 200 (si son online)
- Contenido relevante al tema indicado
- No redirigen a páginas genéricas
- Formato académico consistente (APA o Chicago)

## Variables de configuración (.env)

### CHAPTERS_NUMBER
Número total de capítulos narrativos del manuscrito. Valor estándar: 20.

### TOTAL_WORDS
Meta global mínima de palabras para el manuscrito completo. Valor estándar: 51,000 (aproximadamente 120 páginas impresas).

### WORDS_PER_CHAPTER
Meta promedio de palabras por capítulo. Valor estándar: 2,550 (calculado como TOTAL_WORDS / CHAPTERS_NUMBER).

**Nota:** Estos valores se definen en el archivo `.env` en la raíz del proyecto y deben leerse dinámicamente por scripts y procesos, no hardcodearse en el código.

## Directorios principales

### `bios/`
Contiene subdirectorios para cada personaje (`bios/x/`) con todos los archivos markdown de secciones individuales, archivos concatenados finales, y subdirectorios de control y logs.

### `colecciones/`
Archivos markdown que listan personajes agrupados por tema o periodo histórico. Cada personaje se marca con ✅ cuando su biografía está completa.

### `docx/`
Versiones finales en formato Word para publicación. Estructura espejo de `bios/`: `docx/x/La biografía de X.docx`.

### `esquemas/`
Documentos de planificación y fuentes para cada personaje:
- `X - fuentes.md`: Bibliografía verificable
- `X - plan de trabajo.md`: Distribución de capítulos y metas

### `wordTemplate/`
Plantilla de referencia (`reference.docx`) usada por Pandoc para aplicar formato consistente al convertir markdown a Word.

## Scripts principales

### `concat.py`
Script Python que concatena todos los archivos markdown de un personaje en orden fijo, generando el manuscrito completo en `bios/x/La biografía de X.md`.

### `check_lengths.py`
Script Python que verifica el cumplimiento de metas de palabras por sección, actualizando el archivo CSV de control con longitudes reales y porcentajes de cumplimiento.

### `spine_width.py`
Script Python que calcula el ancho del lomo del libro impreso basándose en el número de páginas y el grosor del papel. Soporta parámetros opcionales para papel color y precisión decimal.

## Abreviaturas y códigos

### APA / Chicago
Formatos de citación bibliográfica académica. APA (American Psychological Association) y Chicago Manual of Style son los estándares aceptados para fuentes en este proyecto.

### HTTP 200
Código de respuesta HTTP que indica éxito. Las URLs de fuentes deben devolver este código para ser consideradas válidas.

### CSV
Comma-Separated Values. Formato de archivo para datos tabulares usado en `longitudes.csv` y otros archivos de control.

### KDP
Kindle Direct Publishing. Plataforma de autopublicación de Amazon para la cual se optimizan estos manuscritos.

### SEO
Search Engine Optimization. Optimización para motores de búsqueda, aplicada en palabras clave y descripciones de venta para mejorar descubrimiento en Amazon.

---

**Actualizado:** 2024-01-15
**Mantenedores:** Este glosario debe actualizarse cuando se introduzcan nuevos términos o conceptos en las reglas del proyecto.
