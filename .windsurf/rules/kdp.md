---
trigger: always_on
---

# Optimización para KDP y ventas

## Títulos y subtítulos
- Cada capítulo debe tener un título claro en el encabezado `#`.
- Subtítulos internos (`##`, `###`) deben reflejar ideas buscables y atractivas.

## Prólogo
- Destacar relevancia del personaje para el lector actual.
- Usar un inicio que enganche (plantear una pregunta, dilema o impacto histórico).

## Epílogo
- Conectar el legado del personaje con el presente.
- Resaltar vigencia de sus aportes o lecciones aprendidas.

## Palabras clave
- Incluir términos que los lectores buscarían en Amazon (ej: liderazgo, libertad, revolución, derechos civiles).
- Usarlas de forma natural, sin forzar.

- Mantener longitud mínima de 120 páginas para cumplir requisitos de impresión en KDP.
- El ancho del lomo debe calcularse exclusivamente con el script:

	```bash
	python spine_width.py <total_paginas>
	```

	Donde `<total_paginas>` es el número total de páginas del libro, determinado manualmente por el usuario tras revisar el archivo `.docx` final generado. Este dato es único para cada libro y no debe almacenarse en `.env` ni en variables globales.

	Si no se cuenta con el total de páginas al inicio del proceso, debe preguntarse explícitamente al usuario y no avanzar hasta obtenerlo. El proceso de metadatos y cálculo de lomo debe detenerse hasta contar con ese dato.

	Para materiales especiales, usa los parámetros opcionales `--page-thickness` y `--precision`.

## Valor comercial
- Equilibrar rigor académico con narrativa accesible.
- Priorizar personajes de alto interés cultural, político o histórico.

## Validaciones automatizables

### Checklist de verificación

Al optimizar contenido para KDP, un agente debe verificar:

- [ ] Verificar que cada capítulo tenga título claro con encabezado `#`
- [ ] Verificar que subtítulos internos (`##`, `###`) sean descriptivos y atractivos
- [ ] Verificar que el prólogo enganche al lector (pregunta, dilema o impacto)
- [ ] Verificar que el epílogo conecte el legado con el presente
- [ ] Verificar que se incluyan palabras clave SEO de forma natural
- [ ] Verificar longitud mínima de 120 páginas en archivo `.docx` final
- [ ] Verificar que el ancho del lomo se haya calculado con `spine_width.py`
- [ ] Verificar que el cálculo del lomo esté registrado en `bios/x/kdp/metadata.md`
- [ ] Verificar equilibrio entre rigor académico y narrativa accesible

### Evidencia a conservar

Para cada verificación completada, adjuntar:

- **Archivo Word final**: `docx/x/La biografía de X.docx` con el conteo de páginas visible
- **Captura del cálculo del lomo**: Salida del script `spine_width.py` con fecha/hora
- **Registro en metadata.md**: Confirmación de que el ancho del lomo está documentado
- **Análisis de palabras clave**: Lista de palabras clave SEO identificadas en el texto

### Scripts a ejecutar

1. **Cálculo del ancho del lomo**:
   ```bash
   python spine_width.py <total_paginas>
   ```
   Guardar salida en: `bios/x/kdp/logs/spine-width-<fecha>.log`
   Copiar resultado a: `bios/x/kdp/metadata.md`

2. **Verificación de estructura de encabezados**:
   ```bash
   grep -E "^#+ " bios/x/*.md > bios/x/kdp/logs/headers-check-<fecha>.log
   ```

3. **Análisis de palabras clave** (manual):
   - Identificar términos relevantes para búsquedas en Amazon
   - Documentar en: `bios/x/kdp/logs/keywords-analysis-<fecha>.md`

## Relacionados

- [kdpData-rules.md](kdpData-rules.md) - Reglas específicas para metadatos KDP
- [structure.md](structure.md) - Estructura editorial obligatoria
- [quality.md](quality.md) - Control de calidad editorial
- [workflow.md](workflow.md) - Flujo completo de trabajo

