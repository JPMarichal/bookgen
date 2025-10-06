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
