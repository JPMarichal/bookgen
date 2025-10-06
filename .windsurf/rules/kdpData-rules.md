---
trigger: manual
---

Ninguno de los items siguientes se refiere en forma alguna a los archivos de sistema o metodología de redacción. Se concentran en el contenido del libro mismo, en una orientación a la publicación y venta.

Subtítulo: una sentencia muy breve descriptiva e interesante.

Categorías propuestas: las 10 categorías en español más apropiadas para el libro según el esquema de Amazon.mx

Descripción de venta para Amazon KDP: Esta descripción se dirige directamente al lector (segunda persona del singular). Usa keywords de seo. Incluye la guía de contenido de las secciones y capítulos, uno por uno, semejante a un índice. Promueve en la descripción todos los puntos fuertes que hacen único a este ejemplar. 

Palabras clave: 15 palabras clave seo, dirigidas a facilitar el hallazgo del libro en la plataforma de Amazon.

Ancho del lomo: El ancho del lomo se calcula **exclusivamente** mediante `spine_width.py`. No uses cálculos manuales.

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

El archivo metadata.md contendrá el subtítulo, las categorías propuestas, palabras clave, y el ancho del lomo.

### Contenido de metadata.md

El archivo `bios/x/kdp/metadata.md` debe incluir:

1. **Subtítulo**: Una sentencia muy breve descriptiva e interesante.
2. **Categorías propuestas**: Las 10 categorías en español más apropiadas para el libro según el esquema de Amazon.mx.
3. **Palabras clave**: 15 palabras clave SEO, dirigidas a facilitar el hallazgo del libro en la plataforma de Amazon.
4. **Ancho del lomo**: El valor calculado mediante `spine_width.py`, incluyendo:
   - Número total de páginas utilizado
   - Tipo de papel (blanco y negro estándar, o especificar si es color u otro)
   - Valor calculado en centímetros
   - Fecha y hora del cálculo (formato ISO 8601: `YYYY-MM-DD HH:MM:SS`)

**Ejemplo de formato para el ancho del lomo en metadata.md**:
```markdown
- **Ancho del lomo (150 páginas, papel blanco)**: 0.43 cm
- **Fecha de cálculo**: 2024-01-15 14:30:00
```

O para interiores a color:
```markdown
- **Ancho del lomo (200 páginas, papel color)**: 0.66 cm  
  _(calculado con --page-thickness 0.0033)_
- **Fecha de cálculo**: 2024-01-15 14:35:00
```

El nombre del autor es Juan Pablo Marichal Catalán.

### Checklist para creación de metadata KDP

Antes de finalizar la creación de archivos KDP, verifica:

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