---
trigger: always_on
---

# Flujo técnico de automatización

## Directorios
- colecciones/ → lista de personajes.
- esquemas/ → planes de trabajo y fuentes.
- bios/ → capítulos y secciones.
- docx/ → versiones finales en Word.

## Scripts
- concat.py concatena en orden fijo:
  - prólogo, introducción, cronología, capítulos 1–N (N según `CHAPTERS_NUMBER` de `.env`), epílogo, glosario, dramatis personae, fuentes.

## Conversión
- Usar Pandoc con plantilla de Word:
  pandoc "bios\x\La biografía de X.md" -o "bios\x\La biografía de X.docx" --reference-doc="wordTemplate\reference.docx"

## Marcado
- Una vez generado el libro, marcar personaje con ✅ en colecciones.txt.

## Carga de variables desde .env

Los parámetros de conteo (`CHAPTERS_NUMBER`, `TOTAL_WORDS`, `WORDS_PER_CHAPTER`) se almacenan en el archivo `.env` en la raíz del proyecto con formato `KEY: VALUE`.

### PowerShell
```powershell
# Cargar variables desde .env
$envVars = @{}
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*([^:]+):\s*(.+)\s*$') {
        $envVars[$matches[1].Trim()] = $matches[2].Trim()
    }
}

# Usar las variables
$chaptersNumber = [int]$envVars['CHAPTERS_NUMBER']
$totalWords = [int]$envVars['TOTAL_WORDS']
$wordsPerChapter = [int]$envVars['WORDS_PER_CHAPTER']

Write-Host "Capítulos: $chaptersNumber, Total palabras: $totalWords, Palabras por capítulo: $wordsPerChapter"
```

### Python
```python
# Opción 1: Parser simple (sin dependencias)
def load_env(filepath='.env'):
    env_vars = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and ':' in line:
                key, value = line.split(':', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars

env = load_env()
chapters_number = int(env['CHAPTERS_NUMBER'])
total_words = int(env['TOTAL_WORDS'])
words_per_chapter = int(env['WORDS_PER_CHAPTER'])

# Opción 2: Con python-dotenv (requiere instalación)
# from dotenv import dotenv_values
# env = dotenv_values('.env')
# chapters_number = int(env['CHAPTERS_NUMBER'])
```

