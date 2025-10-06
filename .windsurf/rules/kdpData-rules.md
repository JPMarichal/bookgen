---
trigger: manual
---

Ninguno de los items siguientes se refiere en forma alguna a los archivos de sistema o metodología de redacción. Se concentran en el contenido del libro mismo, en una orientación a la publicación y venta.

Subtítulo: una sentencia muy breve descriptiva e interesante.

Categorías propuestas: las 10 categorías en español más apropiadas para el libro según el esquema de Amazon.mx

Descripción de venta para Amazon KDP: Esta descripción se dirige directamente al lector (segunda persona del singular). Usa keywords de seo. Incluye la guía de contenido de las secciones y capítulos, uno por uno, semejante a un índice. Promueve en la descripción todos los puntos fuertes que hacen único a este ejemplar. 

Palabras clave: 15 palabras clave seo, dirigidas a facilitar el hallazgo del libro en la plataforma de Amazon.



Ancho del lomo: El cálculo debe realizarse exclusivamente ejecutando el script:

```bash
python spine_width.py <total_paginas>
```

Donde `<total_paginas>` es el número total de páginas del libro, determinado manualmente por el usuario tras revisar el archivo `.docx` final generado. Este dato es único para cada libro y no debe almacenarse en `.env` ni en variables globales.

Si no se cuenta con el total de páginas al inicio del proceso, debe preguntarse explícitamente al usuario y no avanzar hasta obtenerlo. El proceso de metadatos y cálculo de lomo debe detenerse hasta contar con ese dato.

Opcionalmente, si el material de impresión es diferente (por ejemplo, papel color o gramaje especial), puedes usar:

```bash
python spine_width.py <total_paginas> --page-thickness 0.0033 --precision 3
```

Consulta la documentación de `spine_width.py` para más detalles sobre los parámetros `--page-thickness` y `--precision`.

El resultado debe copiarse manualmente en el archivo `bios/x/kdp/metadata.md` bajo el campo "Ancho del lomo", junto con la fecha y hora del cálculo, y la fuente del número de páginas utilizada (por ejemplo: "contado manualmente en docx").

**Checklist para metadatos KDP**

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

No se permite el cálculo manual ni aproximaciones. Siempre usar el script para asegurar consistencia.

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

Previamente, el libro se ha creado y la versión docx está lista, por lo que no es necesario en este punto volver a esas tareas.

Con los datos anteriores, crearás los siguientes archivos cuando el usuario solicite la creación de datos de kdp o metadata para un personaje específico:

- bios/x/kdp/metadata.md
- bios/x/kdp/descripcion.md

El archivo descripcion.md contendrá la descripción de venta para Amazon KDP únicamente. Deberás revisar todo el libro antes de generar la descripción. La descripción debe ser larga y colmada de términos seo de cola larga. 


El archivo metadata.md contendrá el subtítulo, las categorías propuestas, palabras clave, el ancho del lomo (calculado y documentado como se indica arriba).

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
