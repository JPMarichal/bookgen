param(
    [string]$coleccion = "colecciones\personajes_guerra_fria.md",
    [string]$personaje
)

if (-not (Test-Path $coleccion)) {
    Write-Host "⚠️  Colección no encontrada: $coleccion"
    exit 1
}

# Leer colección
$lineas = Get-Content $coleccion

# Resolver personaje
if (-not $personaje) {
    for ($i = 0; $i -lt $lineas.Length; $i++) {
        if ($lineas[$i] -notmatch "✅") {
            $lineaOriginal = $lineas[$i].Trim()
            $match = [regex]::Match($lineaOriginal, '^(?<num>\d+\.\s+)?(?<nombre>[^✅]+?)\s*(✅)?$')
            if (-not $match.Success) { continue }

            $numero = $match.Groups['num'].Value
            $nombre = $match.Groups['nombre'].Value.Trim()

            if (-not [string]::IsNullOrWhiteSpace($nombre)) {
                $personaje = $nombre
                $lineas[$i] = ("{0}{1} ✅" -f $numero, $nombre).Trim()
                break
            }
        }
    }

    if (-not $personaje) {
        Write-Host "No hay personajes pendientes en la colección."
        exit
    }

    Set-Content $coleccion $lineas
}
else {
    # Limpiar nombre para búsqueda
    $personaje = $personaje.Trim()
    $encontrado = $false
    for ($i = 0; $i -lt $lineas.Length; $i++) {
        $match = [regex]::Match($lineas[$i], '^(?<num>\d+\.\s+)?(?<nombre>[^✅]+?)(\s*✅)?$')
        if (-not $match.Success) { continue }

        $numero = $match.Groups['num'].Value
        $nombre = $match.Groups['nombre'].Value.Trim()

        if ($nombre -eq $personaje) {
            if ($lineas[$i] -notmatch "✅") {
                $lineas[$i] = ("{0}{1} ✅" -f $numero, $nombre).Trim()
                Set-Content $coleccion $lineas
            }
            $encontrado = $true
            break
        }
    }

    if (-not $encontrado) {
        Write-Host "⚠️  Personaje no encontrado en la colección: $personaje"
    }
}

# Normalizar nombre (minúsculas, guiones bajos)
$personajeNorm = [regex]::Replace($personaje.ToLower(), "[^\p{L}0-9]+", "_").Trim('_')

function Remove-Diacritics([string]$text) {
    $normalized = $text.Normalize([Text.NormalizationForm]::FormD)
    $builder = New-Object System.Text.StringBuilder
    foreach ($ch in $normalized.ToCharArray()) {
        $category = [Globalization.CharUnicodeInfo]::GetUnicodeCategory($ch)
        if ($category -ne [Globalization.UnicodeCategory]::NonSpacingMark) {
            [void]$builder.Append($ch)
        }
    }
    return $builder.ToString().Normalize([Text.NormalizationForm]::FormC)
}

# Directorio base
$dir = "bios\$personajeNorm"
if (-not (Test-Path $dir)) {
    Write-Host "⚠️  Directorio no encontrado: $dir"
    exit 1
}

$fileSafeName = Remove-Diacritics("La biografia de $personaje").Replace('  ', ' ').Trim()
$outfile = Join-Path $dir ("{0}.md" -f $fileSafeName)

# Archivos en orden fijo
$files = @(
    "prologo.md",
    "introduccion.md",
    "cronologia.md",
    "capitulo-01.md","capitulo-02.md","capitulo-03.md","capitulo-04.md","capitulo-05.md",
    "capitulo-06.md","capitulo-07.md","capitulo-08.md","capitulo-09.md","capitulo-10.md",
    "capitulo-11.md","capitulo-12.md","capitulo-13.md","capitulo-14.md","capitulo-15.md",
    "epilogo.md",
    "glosario.md",
    "dramatis-personae.md",
    "fuentes.md"
)

$encoding = New-Object System.Text.UTF8Encoding($false)
$builder = New-Object System.Text.StringBuilder

foreach ($file in $files) {
    $path = Join-Path $dir $file
    if (Test-Path $path) {
        $contenido = Get-Content $path -Raw -Encoding UTF8
        [void]$builder.AppendLine($contenido)
        [void]$builder.AppendLine()
    }
    else {
        Write-Host "⚠️  Archivo faltante: $file"
    }
}

[System.IO.File]::WriteAllText($outfile, $builder.ToString(), $encoding)

Write-Host "✅ Concatenación completa para: $personaje"
Write-Host "📄 Archivo final: $outfile"
