---
trigger: always_on
---

# Lineamientos de estructura editorial

## Objetivo
Definir estructura uniforme y obligatoria para todos los manuscritos biográficos, garantizando orden consistente de secciones, número fijo de capítulos y metas de extensión alineadas con requisitos de publicación KDP.

## Entradas requeridas
- Plan de trabajo en `esquemas/X - plan de trabajo.md` con distribución de capítulos.
- Meta global de 51,000 palabras mínimo (~120 páginas).
- Conocimiento del personaje y disponibilidad de documentación por periodo de vida.
- Variables de configuración desde `.env`:
  - `CHAPTERS_NUMBER`: Número de capítulos (por defecto: 20)
  - `TOTAL_WORDS`: Meta global de palabras (por defecto: 51000)
  - `WORDS_PER_CHAPTER`: Meta de palabras por capítulo (por defecto: 2550)

## Pasos automáticos
1. Crear estructura de directorios `bios/x/` para el personaje.
2. Generar archivos individuales para cada sección:
   - prologo.md
   - introduccion.md
   - cronologia.md
   - capitulo-01.md hasta capitulo-20.md
   - epilogo.md
   - glosario.md
   - dramatis-personae.md
   - fuentes.md
3. Asegurar que cada capítulo comience con encabezado `# Capítulo N: [título]`.
4. Incluir subtítulos internos (`##`, `###`) en cada capítulo según extensión y organización temática.

## Validaciones/Logs
- **Orden obligatorio de secciones**:
  1. Prólogo
  2. Introducción metodológica
  3. Cronología
  4. Capítulos 1-20
  5. Epílogo analítico
  6. Glosario
  7. Dramatis personae
  8. Fuentes
- **Número de capítulos**: Exactamente 20 capítulos obligatorios.
- **Encabezados de capítulos**: Cada capítulo debe comenzar con `# Capítulo N: [título]`.
- **Subtítulos internos**: Usar `##` y `###` cuando la extensión del capítulo lo justifique (jerarquía máxima de 3 niveles).
- **Meta de extensión global**: Mínimo 51,000 palabras (~120 páginas).
- **Meta por capítulo**: Aproximadamente 2,550 palabras, ajustada según disponibilidad de documentación y relevancia del periodo (ej. infancia con menos fuentes puede ser más breve).
- **Archivo de salida concatenado**: `bios/x/La biografía de X.md` (generado por concat.py).
- **Archivo Word final**: `docx/x/La biografía de X.docx` (generado por Pandoc).

## Fallbacks/Escalada
- Si un capítulo queda significativamente por debajo de la meta: expandir con contexto histórico, descripciones ambientales, análisis de motivaciones.
- Si no hay suficiente documentación para un periodo: ajustar meta de ese capítulo en el plan y compensar en capítulos con más fuentes.
- Si el total no alcanza 51,000 palabras: identificar capítulos prioritarios para expansión según riqueza de fuentes disponibles.

## Validaciones automatizables

### Checklist de verificación

Al validar la estructura editorial, un agente debe verificar:

- [ ] Verificar que el directorio `bios/x/` exista
- [ ] Verificar que existan exactamente 25 archivos `.md` (prólogo + introducción + cronología + 20 capítulos + epílogo + glosario + dramatis personae + fuentes)
- [ ] Verificar el orden obligatorio de secciones:
  - [ ] 1. prologo.md
  - [ ] 2. introduccion.md
  - [ ] 3. cronologia.md
  - [ ] 4. capitulo-01.md hasta capitulo-20.md
  - [ ] 5. epilogo.md
  - [ ] 6. glosario.md
  - [ ] 7. dramatis-personae.md
  - [ ] 8. fuentes.md
- [ ] Verificar que cada capítulo comience con `# Capítulo N: [título]`
- [ ] Verificar que los subtítulos usen `##` y `###` (máximo 3 niveles)
- [ ] Verificar meta de extensión global: mínimo 51,000 palabras
- [ ] Verificar que cada capítulo tenga aproximadamente 2,550 palabras (±5%)

### Evidencia a conservar

Para cada verificación completada, adjuntar:

- **Lista de archivos**: Salida de `ls -1 bios/x/*.md` mostrando los 25 archivos
- **Estructura de encabezados**: Todos los encabezados `#` extraídos de cada archivo
- **Reporte de longitudes**: CSV completo de `bios/x/control/longitudes.csv`
- **Conteo total de palabras**: Suma de palabras de todas las secciones

### Scripts a ejecutar

1. **Verificación de archivos obligatorios**:
   ```bash
   # Debe listar exactamente 25 archivos
   ls -1 bios/x/*.md | wc -l
   ls -1 bios/x/*.md > bios/x/logs/structure-files-<fecha>.log
   ```

2. **Verificación de encabezados**:
   ```bash
   # Extraer todos los encabezados de nivel 1
   grep -h "^# " bios/x/*.md > bios/x/logs/structure-headers-<fecha>.log
   ```

3. **Verificación de longitudes**:
   ```bash
   python check_lengths.py <personaje> 2>&1 | tee bios/x/logs/structure-lengths-<fecha>.log
   ```

4. **Conteo total de palabras**:
   ```bash
   wc -w bios/x/*.md | tail -1 > bios/x/logs/structure-wordcount-<fecha>.log
   ```

## Relacionados
- [quality.md](quality.md) - Control de longitud y calidad
- [length.md](length.md) - Validación de longitudes por sección
- [automation.md](automation.md) - Concatenación automática
- [workflow.md](workflow.md) - Integración en flujo completo