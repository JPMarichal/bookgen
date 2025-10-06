---
trigger: always_on
---

# Lineamientos de estilo narrativo

## Objetivo
Establecer estándares técnicos y formales de escritura para el manuscrito: estructura de encabezados, formato de párrafos, uso de recursos Markdown y vocabulario apropiado. Complementa las directrices emocionales y literarias definidas en literaryStyle.md.

## Entradas requeridas
- Conocimiento de sintaxis Markdown (encabezados, tablas, listas).
- Contenido histórico verificado desde fuentes.
- Capítulos en redacción o revisión.

## Pasos automáticos
1. Aplicar estructura de encabezados en cada capítulo:
   - `#` para título del capítulo: `# Capítulo N: [nombre]`
   - `##` para subtítulos temáticos que agrupen párrafos
   - `###` para subdivisiones internas cuando sea necesario
2. Mantener párrafos entre 4-7 líneas en promedio.
3. Incorporar tablas en sintaxis Markdown cuando se presenten datos estructurados.
4. Usar listas (`-` o `*`) para enumeraciones breves.
5. Describir mapas y gráficos como narraciones extensas en prosa (no gráficos).

## Validaciones/Logs
- **Estructura de encabezados**: Máximo 3 niveles (`#`, `##`, `###`).
- **Formato de capítulos**: Cada capítulo inicia con `# Capítulo N: [nombre]`.
- **Subtítulos (`##`)**: Agrupan párrafos temáticamente; número de párrafos varía según conveniencia.
- **Subdivisiones (`###`)**: Para organizar ideas extensas dentro de subtemas.
- **Narración**: Estilo narrativo-literario (envolvente, claro, fluido, ligeramente poético). Emotivo pero sin llegar al apasionamiento.
- **Profundidad académica**: Mantener rigor histórico con tono accesible.
- **No citas directas**: Siempre reescribir en narración propia.
- **No listas de datos secos**: Incorporar contexto, explicación y emoción.
- **Párrafos**: Entre 4-7 líneas promedio. Evitar bloques excesivamente largos o muy cortos.
- **Recursos Markdown**:
  - Tablas: Sintaxis `| col1 | col2 |`
  - Listas: Con `-` o `*`
  - Mapas: Descripciones largas en prosa, no gráficos
- **Vocabulario**: Preciso, fluido, atractivo. Evitar jergas innecesarias. Equilibrar emoción con rigor histórico.

## Fallbacks/Escalada
- Si un párrafo resulta demasiado largo (>8 líneas): dividir en dos párrafos con transición adecuada.
- Si falta profundidad emocional: referirse a literaryStyle.md para incorporar elementos sensoriales y emotivos.
- Si los datos son demasiado secos: integrar contexto narrativo, explicaciones de causa-efecto, o descripciones ambientales.
- Si hay errores de sintaxis Markdown: revisar tablas, listas y encabezados antes de concatenar.

## Relacionados
- [literaryStyle.md](literaryStyle.md) - Estilo emocional y literario (complementario)
- [structure.md](structure.md) - Estructura general del manuscrito
- [quality.md](quality.md) - Validación de formato y coherencia