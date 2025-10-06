---
trigger: always_on
---

# Flujo técnico de automatización

## Objetivo
Automatizar la concatenación de archivos Markdown en el orden correcto y la conversión final a formato Word para publicación en KDP, asegurando que el flujo técnico sea consistente y reproducible.

## Entradas requeridas
- Directorio `bios/x/` con todos los archivos de secciones (.md) del personaje.
- Nombre del personaje (normalizado o como argumento `-personaje`).
- Archivo de colección en `colecciones/` con lista de personajes.
- Plantilla de Word en `wordTemplate/reference.docx` para conversión con Pandoc.

## Pasos automáticos
1. Ejecutar script de concatenación:
   ```
   python concat.py -personaje "nombre_personaje"
   ```
2. El script `concat.py` concatena archivos en orden fijo:
   - prólogo.md
   - introduccion.md
   - cronologia.md
   - capitulo-01.md hasta capitulo-20.md
   - epilogo.md
   - glosario.md
   - dramatis-personae.md
   - fuentes.md
3. Generar archivo consolidado en `bios/x/La biografía de X.md`.
4. Convertir a Word usando Pandoc:
   ```
   pandoc "bios\x\La biografía de X.md" -o "bios\x\La biografía de X.docx" --reference-doc="wordTemplate\reference.docx"
   ```
5. Mover el archivo `.docx` a `docx/x/La biografía de X.docx`.
6. Marcar personaje con ✅ en el archivo de colección correspondiente.

## Validaciones/Logs
- **Concatenación**: Script imprime `✅ Concatenación completa para: {personaje}` y ruta del archivo final.
- **Archivos faltantes**: Script imprime `⚠️ Archivo faltante: {archivo}` por cada archivo que no existe.
- **Directorio inexistente**: Script termina con `⚠️ Directorio no encontrado: {directorio}` si `bios/x/` no existe.
- **Salida esperada**: Archivo Markdown en `bios/x/La biografía de X.md` con todas las secciones concatenadas.
- **Salida final**: Archivo Word en `docx/x/La biografía de X.docx` con formato aplicado.

## Fallbacks/Escalada
- Si falta algún archivo de sección, el script continúa pero reporta advertencia. Revisar manualmente qué archivos faltan.
- Si el directorio `bios/x/` no existe, detener proceso y verificar que se haya completado la fase de redacción.
- Si Pandoc falla, verificar que la plantilla `wordTemplate/reference.docx` exista y que Pandoc esté instalado.
- Si la conversión Word falla, revisar sintaxis Markdown en el archivo concatenado (tablas mal formadas, encabezados incorrectos).

## Relacionados
- [structure.md](structure.md) - Orden de secciones y archivos
- [quality.md](quality.md) - Validaciones antes de concatenar
- [workflow.md](workflow.md) - Flujo completo de trabajo

## Directorios
- `colecciones/` → lista de personajes por colección
- `esquemas/` → planes de trabajo y fuentes
- `bios/` → capítulos y secciones individuales (estructura: `bios/x/`)
- `docx/` → versiones finales en Word (estructura: `docx/x/`)
