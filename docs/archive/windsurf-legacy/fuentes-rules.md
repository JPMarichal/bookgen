---
trigger: always_on
---

# Verificación de fuentes bibliográficas

## Objetivo
Asegurar que todas las fuentes bibliográficas sean verificables, accesibles online y relevantes al contenido indicado, usando formatos académicos consistentes (APA o Chicago).

## Entradas requeridas
- Archivo `esquemas/X - fuentes.md` con bibliografía completa
- Acceso a internet para verificar URLs
- Herramienta para verificación HTTP (curl, wget o equivalente)

## Pasos automáticos
1. Extraer todas las URLs del archivo de fuentes
2. Verificar código HTTP de cada URL (debe ser 200)
3. Validar que el contenido de la URL sea relevante al tema indicado
4. Confirmar que las URLs no redirijan a páginas genéricas (homepages)
5. Verificar formato académico consistente (APA o Chicago)
6. Confirmar que cada fuente incluya toda la información requerida (autor, título, fecha, editorial/dominio)

## Validaciones/Logs
- **URLs válidas**: Todas deben devolver código HTTP 200
- **Contenido relevante**: No basta con código 200, el contenido debe cumplir con lo prometido
- **Sin redirecciones genéricas**: URLs no deben conducir a homepages donde el usuario se desoriente
- **Formato académico**: Consistencia en citación (APA o Chicago)
- **Información completa**: Cada fuente debe incluir autor, título, fecha, editorial/dominio
- **Logs generados**: Archivos en `esquemas/logs/` con resultados de verificación

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

## Fallbacks/Escalada
- Si una URL devuelve código de error (404, 403, 500): reemplazar con fuente alternativa verificable
- Si el contenido de la URL no es relevante: buscar fuente alternativa con mismo tema y formato académico
- Si una URL redirige a homepage genérica: buscar URL específica del artículo o usar fuente física con referencia completa
- Si el formato de citación es inconsistente: estandarizar todas las fuentes al mismo formato (APA o Chicago)
- Si faltan datos en la citación: investigar y completar información faltante (autor, fecha, editorial)

## Relacionados
- [research.md](research.md) - Estándares de investigación y fuentes
- [quality.md](quality.md) - Control de calidad editorial
- [workflow.md](workflow.md) - Flujo completo de trabajo
- [GLOSARIO.md](../GLOSARIO.md) - Glosario unificado de términos del proyecto

