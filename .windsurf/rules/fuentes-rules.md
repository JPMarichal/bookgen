---
trigger: always_on
---

La bibliografía debe ser verificable (APA/Chicago + URLs). Todas las fuentes deben ser online, existir, ser relevantes y congruentes y devolver 200 (no 404, 403, 500 u otros códigos de error). No basta con que devuelvan código 200, su contenido debe cumplir con lo prometido y ser relevante; no conducir, por ejemplo, a un homepage general donde el usuario se desoriente.

## Validaciones automatizables

### Checklist de verificación

Al verificar fuentes, un agente debe verificar:

- [ ] Verificar que todas las URLs devuelvan código HTTP 200
- [ ] Verificar que el contenido de cada URL sea relevante al tema indicado
- [ ] Verificar que las URLs no redirijan a páginas genéricas (homepages)
- [ ] Verificar que las URLs no devuelvan códigos de error (404, 403, 500)
- [ ] Verificar que las fuentes usen formato académico consistente (APA o Chicago)
- [ ] Verificar que cada fuente incluya toda la información requerida (autor, título, fecha, editorial/dominio)

### Evidencia a conservar

Para cada verificación completada, adjuntar:

- **Log de verificación HTTP**: Listado de todas las URLs con sus códigos de respuesta
- **Capturas de contenido**: Screenshots o descripción del contenido relevante de cada URL
- **Reporte de formato**: Análisis de consistencia en el formato de citación
- **Lista de URLs válidas**: Todas las URLs que pasaron la verificación

### Scripts a ejecutar

1. **Verificación de códigos HTTP**:
   ```bash
   # Script para verificar todas las URLs en esquemas/X - fuentes.md
   # Ejemplo con curl:
   grep -Eo "https?://[^\s]+" "esquemas/X - fuentes.md" | \
     while read url; do \
       echo "$url: $(curl -s -o /dev/null -w '%{http_code}' "$url")"; \
     done > esquemas/logs/http-verification-<personaje>-<fecha>.log
   ```

2. **Extracción de URLs**:
   ```bash
   grep -Eo "https?://[^\s]+" "esquemas/X - fuentes.md" > esquemas/logs/urls-list-<personaje>-<fecha>.log
   ```

## Relacionados

- [research.md](research.md) - Estándares de investigación y fuentes
- [quality.md](quality.md) - Control de calidad editorial
- [workflow.md](workflow.md) - Flujo completo de trabajo
