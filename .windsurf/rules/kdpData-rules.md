---
trigger: manual
---

# Metadatos y optimización KDP

## Objetivo
Generar metadatos comerciales completos para publicación en Amazon KDP, incluyendo subtítulo, categorías, palabras clave SEO, descripción de venta y cálculo preciso del ancho del lomo usando `spine_width.py`.

## Entradas requeridas
- Archivo Word final generado: `docx/x/La biografía de X.docx`
- Número total de páginas del libro (contado manualmente desde el .docx)
- Manuscrito completo para revisar contenido y generar descripción de venta
- Conocimiento del personaje y temas principales para palabras clave SEO
- Variables de configuración desde `.env`:
  - `TOTAL_WORDS`: Meta global de palabras (para validación)
  - `WORDS_PER_CHAPTER`: Meta de palabras por capítulo (para validación)

## Pasos automáticos

### 1. Preparación
- Verificar que el archivo `.docx` final esté generado en `docx/x/`
- Solicitar al usuario el número total de páginas del documento Word
- Crear directorio `bios/x/kdp/` si no existe
- Crear directorio `bios/x/kdp/logs/` para registros

### 2. Cálculo del ancho del lomo
Ejecutar el script obligatoriamente:
```bash
python spine_width.py <total_paginas>
```

Para papel color u opciones especiales:
```bash
python spine_width.py <total_paginas> --page-thickness 0.0033 --precision 3
```

### 3. Generación de metadatos
- **Subtítulo**: Crear una sentencia breve, descriptiva e interesante (máximo 10-12 palabras)
- **Categorías**: Proponer 10 categorías relevantes según esquema de Amazon.mx
- **Palabras clave**: Identificar 15 palabras clave SEO para facilitar descubrimiento
- **Descripción de venta**: Redactar descripción dirigida al lector (segunda persona singular), con:
  - Keywords SEO integrados naturalmente
  - Guía de contenido de secciones y capítulos (como índice)
  - Puntos fuertes que hacen único al libro

### 4. Documentación
Crear dos archivos en `bios/x/kdp/`:

**metadata.md** contendrá:
- Subtítulo
- 10 categorías propuestas
- 15 palabras clave SEO
- Ancho del lomo con formato completo (ver ejemplo abajo)

**descripcion.md** contendrá:
- Descripción de venta para Amazon KDP (larga, con términos SEO de cola larga)

## Validaciones/Logs
- **Archivo Word final**: Debe existir `docx/x/La biografía de X.docx` antes de generar metadatos
- **Número de páginas**: Usuario debe proporcionar el conteo exacto del documento Word
- **Ancho del lomo**: Calculado con `spine_width.py`, formato completo registrado en `metadata.md`
- **Subtítulo**: Máximo 10-12 palabras, descriptivo y atractivo
- **Categorías**: Exactamente 10 categorías relevantes para Amazon.mx
- **Palabras clave**: Exactamente 15 palabras clave SEO
- **Descripción de venta**: Segunda persona singular, keywords integrados, índice de contenido incluido
- **Archivos generados**:
  - `bios/x/kdp/metadata.md` con todos los metadatos
  - `bios/x/kdp/descripcion.md` con descripción de venta
  - `bios/x/kdp/logs/spine-calculation-<fecha>.log` con resultado del cálculo

**Checklist para metadatos KDP:**

- [ ] Subtítulo breve y atractivo
- [ ] 10 categorías relevantes (Amazon.mx)
- [ ] 15 palabras clave SEO
- [ ] Ancho del lomo calculado con `spine_width.py` y copiado a `metadata.md`
- [ ] Fecha y hora del cálculo del lomo registrada en `metadata.md`
- [ ] Fuente del número de páginas (ej: "contado manualmente en docx") indicada en `metadata.md`
- [ ] Validar que el total de páginas coincide con `TOTAL_WORDS` y `WORDS_PER_CHAPTER` (si aplica)

**Ejemplo de registro en metadata.md:**

```markdown
- **Ancho del lomo (135 páginas, papel blanco, calculado el 2025-10-06 14:30, fuente: contado manualmente en docx)**: 0.94 cm
```

## Fallbacks/Escalada
- Si no se proporciona el número de páginas: detener proceso y solicitar explícitamente al usuario
- Si `spine_width.py` falla: verificar que el script esté disponible y que el número de páginas sea válido (>0)
- Si faltan palabras clave relevantes: revisar el manuscrito completo para identificar temas principales
- Si la descripción es muy breve: expandir con detalles de capítulos y puntos fuertes del libro
- Si las categorías no son relevantes: investigar categorías similares en Amazon.mx para biografías del periodo/tema

**Nota importante**: No se permite el cálculo manual ni aproximaciones del ancho del lomo. Siempre usar el script `spine_width.py` para asegurar consistencia.

### Cálculo del ancho del lomo

**Requisito previo**: El usuario debe proporcionar el número total de páginas del libro. Este número proviene de la revisión manual del archivo `.docx` final. Si el usuario no lo proporciona, solicítalo antes de proceder.

**Comando básico** (papel blanco y negro estándar, 55 lb):
```bash
python spine_width.py <total_pages>
```

**Ejemplo**:
```bash
python spine_width.py 150
# Salida: Ancho del lomo: 0.43 cm
```

**Comando con parámetros opcionales**:

- Para **interiores a color** (papel más grueso):
  ```bash
  python spine_width.py <total_pages> --page-thickness 0.0033
  ```

- Para **mayor precisión** en la salida (por ejemplo, 3 decimales):
  ```bash
  python spine_width.py <total_pages> --precision 3
  ```

- **Combinando opciones**:
  ```bash
  python spine_width.py 200 --page-thickness 0.0033 --precision 3
  # Salida: Ancho del lomo: 0.660 cm
  ```

**Origen del número de páginas**:
- El total de páginas debe obtenerse de la **revisión manual** del archivo `.docx` generado.
- Opcionalmente, puede contrastarse con el total de palabras esperadas en `.env` o con los resultados más recientes de `check_lengths.py` (sumando todas las secciones del archivo `bios/x/control/longitudes.csv`), pero el número definitivo **siempre** proviene del documento Word final.

**Nota importante**: El libro debe estar completamente creado y la versión `.docx` lista antes de este paso. No es necesario volver a tareas de redacción o concatenación.

## Validaciones automatizables

### Checklist de verificación completa

Al crear metadatos KDP, un agente debe verificar:

- [ ] Verificar que el libro esté completamente redactado y concatenado
- [ ] Verificar que el archivo `.docx` final esté generado
- [ ] Verificar que el usuario haya proporcionado el número total de páginas
- [ ] Ejecutar `python spine_width.py <total_paginas>` y verificar salida
- [ ] Verificar que el ancho del lomo esté copiado a `bios/x/kdp/metadata.md`
- [ ] Verificar que la fecha y hora del cálculo estén registradas
- [ ] Verificar que la fuente del número de páginas esté documentada
- [ ] Verificar que el subtítulo sea breve (máximo 10-12 palabras)
- [ ] Verificar que se hayan propuesto exactamente 10 categorías (Amazon.mx)
- [ ] Verificar que se hayan incluido exactamente 15 palabras clave SEO
- [ ] Verificar que la descripción de venta use segunda persona singular
- [ ] Verificar que la descripción incluya keywords SEO relevantes
- [ ] Verificar que la descripción mencione todas las secciones del libro
- [ ] Verificar que ambos archivos (`metadata.md` y `descripcion.md`) existan en `bios/x/kdp/`
- [ ] Verificar que el número de páginas registrado coincida con el archivo .docx final
- [ ] Verificar que el tipo de papel esté especificado (blanco/color)
- [ ] Verificar que la descripción de venta (descripcion.md) esté generada y revisada

### Evidencia a conservar

Para cada verificación completada, adjuntar:

- **Archivo metadata.md**: `bios/x/kdp/metadata.md` completo con todos los campos
- **Archivo descripcion.md**: `bios/x/kdp/descripcion.md` con descripción de venta
- **Log del cálculo del lomo**: Salida completa de `spine_width.py` con fecha/hora
- **Captura del archivo .docx**: Número de páginas visible en el documento Word
- **Validación del tipo de papel**: Confirmación de si es blanco/negro o color

### Scripts a ejecutar

1. **Cálculo del ancho del lomo** (requisito obligatorio):
   ```bash
   python spine_width.py <total_paginas>
   # Para papel color:
   python spine_width.py <total_paginas> --page-thickness 0.0033
   ```
   Guardar salida en: `bios/x/kdp/logs/spine-calculation-<fecha>.log`

2. **Verificación de archivos KDP**:
   ```bash
   ls -lh bios/x/kdp/ > bios/x/kdp/logs/files-check-<fecha>.log
   ```

3. **Conteo de palabras clave**:
   ```bash
   # Verificar que metadata.md contenga exactamente 15 keywords
   grep -c "keyword" bios/x/kdp/metadata.md
   ```

### Formato de registro en metadata.md

Ejemplo requerido:
```markdown
- **Ancho del lomo (<páginas> páginas, papel <tipo>, calculado el <fecha> <hora>, fuente: <origen>)**: <valor> cm
```

Ejemplo concreto:
```markdown
- **Ancho del lomo (135 páginas, papel blanco, calculado el 2025-10-06 14:30, fuente: contado manualmente en docx)**: 0.94 cm
```

## Relacionados
- [kdp.md](kdp.md) - Optimización general para KDP y ventas
- [automation.md](automation.md) - Scripts de automatización
- [workflow.md](workflow.md) - Flujo completo de trabajo
- [quality.md](quality.md) - Control de calidad editorial
- [GLOSARIO.md](../GLOSARIO.md) - Glosario unificado de términos del proyecto

