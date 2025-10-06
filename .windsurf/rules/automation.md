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
- Variables de configuración desde `.env`:
  - `CHAPTERS_NUMBER`: Número de capítulos (por defecto: 20)
  - `TOTAL_WORDS`: Meta global de palabras (por defecto: 51000)
  - `WORDS_PER_CHAPTER`: Meta de palabras por capítulo (por defecto: 2550)

### Leer variables desde .env

**En Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
chapters = int(os.getenv('CHAPTERS_NUMBER', '20'))
total_words = int(os.getenv('TOTAL_WORDS', '51000'))
words_per_chapter = int(os.getenv('WORDS_PER_CHAPTER', '2550'))
```

**En PowerShell:**
```powershell
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        Set-Variable -Name $matches[1] -Value $matches[2]
    }
}
# Usar: $CHAPTERS_NUMBER, $TOTAL_WORDS, $WORDS_PER_CHAPTER
```

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
- **Lomo**: El ancho del lomo debe calcularse y documentarse usando `python spine_width.py <total_paginas>`. El valor y la fecha/hora deben registrarse en `bios/x/kdp/metadata.md`.
- **Directorio inexistente**: Script termina con `⚠️ Directorio no encontrado: {directorio}` si `bios/x/` no existe.
- **Salida esperada**: Archivo Markdown en `bios/x/La biografía de X.md` con todas las secciones concatenadas.
- **Salida final**: Archivo Word en `docx/x/La biografía de X.docx` con formato aplicado.

## Validaciones automatizables

### Checklist de verificación

Antes de ejecutar scripts de automatización, un agente debe verificar:

- [ ] Verificar que el directorio `bios/x/` exista
- [ ] Verificar que todos los archivos de sección estén presentes (prologo.md hasta fuentes.md)
- [ ] Ejecutar `python concat.py <personaje>` y verificar salida sin errores
- [ ] Verificar que el archivo concatenado `bios/x/La biografía de X.md` se haya generado
- [ ] Verificar que la plantilla Word `wordTemplate/reference.docx` exista
- [ ] Ejecutar conversión Pandoc y verificar salida sin errores
- [ ] Verificar que el archivo Word `docx/x/La biografía de X.docx` se haya generado
- [ ] Verificar que el personaje esté marcado con ✅ en `colecciones/`
- [ ] Verificar que no haya warnings de archivos faltantes en la salida

### Evidencia a conservar

Para cada verificación completada, adjuntar:

- **Log de concatenación**: Salida completa de `python concat.py <personaje>`
- **Archivo concatenado**: `bios/x/La biografía de X.md` generado
- **Log de conversión Pandoc**: Salida del comando Pandoc con timestamp
- **Archivo Word final**: `docx/x/La biografía de X.docx`
- **Lista de archivos procesados**: Todos los `.md` incluidos en la concatenación
- **Estado en colección**: Captura mostrando ✅ junto al personaje

### Scripts a ejecutar

1. **Concatenación de secciones**:
   ```bash
   python concat.py <personaje> 2>&1 | tee bios/x/logs/concat-<fecha>.log
   ```

2. **Conversión a Word**:
   ```bash
   pandoc "bios/x/La biografía de X.md" \
     -o "docx/x/La biografía de X.docx" \
     --reference-doc=wordTemplate/reference.docx \
     2>&1 | tee bios/x/logs/pandoc-<fecha>.log
   ```

3. **Verificación de archivos completos**:
   ```bash
   # Listar todos los .md en bios/x/
   ls -1 bios/x/*.md > bios/x/logs/files-list-<fecha>.log
   ```

4. **Cálculo del ancho del lomo** (post-generación):
   ```bash
   python spine_width.py <total_paginas> 2>&1 | tee bios/x/kdp/logs/spine-<fecha>.log
   ```

## Fallbacks/Escalada
- Si falta algún archivo de sección, el script continúa pero reporta advertencia. Revisar manualmente qué archivos faltan.
- Si el directorio `bios/x/` no existe, detener proceso y verificar que se haya completado la fase de redacción.
- Si Pandoc falla, verificar que la plantilla `wordTemplate/reference.docx` exista y que Pandoc esté instalado.
- Si la conversión Word falla, revisar sintaxis Markdown en el archivo concatenado (tablas mal formadas, encabezados incorrectos).

## Relacionados
- [structure.md](structure.md) - Orden de secciones y archivos
- [quality.md](quality.md) - Validaciones antes de concatenar
- [workflow.md](workflow.md) - Flujo completo de trabajo
- [GLOSARIO.md](../GLOSARIO.md) - Glosario unificado de términos del proyecto

## Directorios
- `colecciones/` → lista de personajes por colección
- `esquemas/` → planes de trabajo y fuentes
- `bios/` → capítulos y secciones individuales (estructura: `bios/x/`)
- `docx/` → versiones finales en Word (estructura: `docx/x/`)
