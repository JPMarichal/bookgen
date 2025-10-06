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

- [ ] Subtítulo creado: breve, descriptivo e interesante
- [ ] 10 categorías propuestas para Amazon.mx
- [ ] 15 palabras clave SEO incluidas
- [ ] Ancho del lomo calculado con `python spine_width.py <pages>`
- [ ] Número de páginas registrado en metadata.md
- [ ] Tipo de papel especificado (blanco/color)
- [ ] Valor del ancho del lomo copiado a metadata.md
- [ ] Fecha y hora del cálculo registrada
- [ ] Validación: el número de páginas coincide con el archivo .docx final
- [ ] Descripción de venta (descripcion.md) generada y revisada