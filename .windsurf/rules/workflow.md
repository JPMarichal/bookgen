---
trigger: manual
---

Tu responsabilidad es desarrollar colecciones de biografías de alta demanda para KDP.
Cada libro llevará el título exacto La biografía de X, donde X corresponde al personaje seleccionado.

Selección del personaje

El nombre se toma desde la colección indicada en colecciones/.

Una vez completado el libro, ese nombre se marcará con una palomita (✅) en el archivo de colección.

Fuentes

Antes de redactar, crea esquemas/X - fuentes.md con bibliografía verificable en formato académico.

Incluye al menos dominio o URL para fuentes online.

Las fuentes deben estar listas antes de redactar y usarse en todo el libro.

Planificación

Crea esquemas/X - plan de trabajo.md con:

20 capítulos con título, descripción y meta de palabras equilibrada.

Ajuste de metas para capítulos con menos documentación (ej. infancia).

Redacción batch. Debes planear cuidadosamente tus batches para poder escribir sin limitaciones y de manera ininterrumpida hasta el momento de la concatenación.

Una vez aprobado el plan, crea bios/x/ con todos los archivos.

Redacta hasta el final en batches los siguientes archivos, sin pausas ni resúmenes intermedios:

prologo.md

introduccion.md

cronologia.md

capitulo-01.md … capitulo-20.md

epilogo.md

glosario.md

dramatis-personae.md

fuentes.md

Cada capítulo debe alcanzar la meta definida en el plan (~2,550 palabras promedio).


Estilo narrativo-literario, académico cuando corresponda, pero siempre envolvente.

No uses citas directas. Narración corrida.

Recursos: tablas en Markdown, listas con - o *, mapas como descripciones largas en prosa.

Concatenación automática (script Python)

El archivo final debe ser bios/x/La biografía de X.md.

Usa un script Python fijo para concatenar en el orden correcto.


Ejecutar con:

python concat.py -personaje "joseph_stalin"

Versión final en Word

Convertir con Pandoc usando la plantilla de Word:

pandoc "bios\x\La biografía de X.md" -o "bios\x\La biografía de X.docx" --reference-doc="wordTemplate\reference.docx"


Mover el .docx a docx/x/.

Cierre

Marca con ✅ al personaje en el archivo de colección.