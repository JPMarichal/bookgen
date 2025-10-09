# Escenarios de Prueba - BookGen API

Este documento describe escenarios de prueba completos para validar el funcionamiento de la API de BookGen.

## 📋 Tabla de Contenido

- [Escenarios Básicos](#escenarios-básicos)
- [Escenarios de Flujo Completo](#escenarios-de-flujo-completo)
- [Escenarios de Error](#escenarios-de-error)
- [Escenarios de Performance](#escenarios-de-performance)
- [Escenarios de Validación](#escenarios-de-validación)

---

## Escenarios Básicos

### Escenario 1: Verificación de Salud de la API

**Objetivo:** Confirmar que la API está operativa y respondiendo correctamente.

**Pasos:**
1. Ejecutar `GET /health`
2. Verificar status code 200
3. Verificar que `status = "healthy"`
4. Ejecutar `GET /api/v1/status`
5. Verificar que `status = "operational"`

**Criterios de Éxito:**
- ✅ Ambos endpoints responden con 200 OK
- ✅ Health check retorna status "healthy"
- ✅ API status retorna status "operational"
- ✅ Configuración del sistema es visible

**Resultado Esperado:**
```json
{
  "status": "healthy",
  "timestamp": "<ISO-8601>",
  "environment": "development"
}
```

---

### Escenario 2: Verificación de Métricas

**Objetivo:** Confirmar que el sistema está exponiendo métricas correctamente.

**Pasos:**
1. Ejecutar `GET /metrics`
2. Verificar status code 200
3. Verificar formato Prometheus
4. Verificar presencia de métricas clave

**Criterios de Éxito:**
- ✅ Endpoint responde con 200 OK
- ✅ Content-Type es "text/plain"
- ✅ Métricas incluyen: uptime, cpu, memory, disk
- ✅ Formato válido de Prometheus

**Métricas Esperadas:**
- `bookgen_uptime_seconds`
- `bookgen_cpu_percent`
- `bookgen_memory_percent`
- `bookgen_jobs_total`

---

## Escenarios de Flujo Completo

### Escenario 3: Generación de Biografía - Modo Automático (Happy Path)

**Objetivo:** Generar una biografía completa usando modo automático desde inicio hasta descarga.

**Pasos:**

1. **Health Check**
   ```
   GET /health
   → Verificar que API está disponible
   ```

2. **Crear Trabajo de Biografía**
   ```json
   POST /api/v1/biographies/generate
   {
     "character": "Albert Einstein",
     "chapters": 5,
     "total_words": 5000,
     "mode": "automatic",
     "min_sources": 40,
     "temperature": 0.7
   }
   → Guardar job_id de la respuesta
   ```

3. **Monitorear Progreso (Polling)**
   ```
   GET /api/v1/biographies/{job_id}/status
   → Repetir cada 10 segundos hasta status = "completed"
   ```

4. **Descargar Resultado**
   ```
   GET /api/v1/biographies/{job_id}/download
   → Verificar que se descarga el archivo
   ```

**Criterios de Éxito:**
- ✅ Trabajo creado con status "pending" (202 Accepted)
- ✅ job_id es un UUID válido
- ✅ Status transiciona: pending → in_progress → completed
- ✅ Progress aumenta de 0% a 100%
- ✅ download_url disponible cuando completed
- ✅ Archivo descargado contiene los capítulos generados
- ✅ Tiempo total < 5 minutos para 5 capítulos

**Timeline Esperado:**
- 0s: Job creado (pending)
- 5s: Job iniciado (in_progress, 0%)
- 35s: Capítulo 1 completado (20%)
- 65s: Capítulo 2 completado (40%)
- 95s: Capítulo 3 completado (60%)
- 125s: Capítulo 4 completado (80%)
- 155s: Capítulo 5 completado (100%)
- 160s: Job completado

---

### Escenario 4: Generación de Biografía - Modo Manual

**Objetivo:** Generar biografía con fuentes provistas manualmente por el usuario.

**Pre-requisitos:**
- Tener al menos 10 URLs válidas de fuentes

**Pasos:**

1. **Preparar Fuentes**
   ```json
   {
     "sources": [
       "https://en.wikipedia.org/wiki/Marie_Curie",
       "https://www.nobelprize.org/prizes/physics/1903/marie-curie/biographical/",
       // ... 8 fuentes más
     ]
   }
   ```

2. **Validar Fuentes (Opcional pero Recomendado)**
   ```json
   POST /api/v1/sources/validate
   {
     "sources": [...],
     "check_accessibility": true
   }
   → Verificar que todas las fuentes son válidas
   ```

3. **Crear Trabajo**
   ```json
   POST /api/v1/biographies/generate
   {
     "character": "Marie Curie",
     "chapters": 10,
     "total_words": 10000,
     "mode": "manual",
     "sources": [...]
   }
   ```

4. **Monitorear y Descargar** (igual que Escenario 3)

**Criterios de Éxito:**
- ✅ Validación de fuentes pasa (si se ejecuta)
- ✅ Trabajo acepta las fuentes manuales
- ✅ source_count = número de fuentes provistas
- ✅ sources_generated_automatically = false
- ✅ Generación se completa exitosamente

---

### Escenario 5: Generación de Biografía - Modo Híbrido

**Objetivo:** Combinar fuentes manuales con generación automática.

**Pasos:**

1. **Proporcionar Algunas Fuentes**
   ```json
   POST /api/v1/biographies/generate
   {
     "character": "Leonardo da Vinci",
     "chapters": 15,
     "total_words": 15000,
     "mode": "hybrid",
     "sources": [
       "https://en.wikipedia.org/wiki/Leonardo_da_Vinci",
       "https://www.britannica.com/biography/Leonardo-da-Vinci"
     ],
     "min_sources": 40
   }
   ```

2. **Verificar Respuesta**
   - Verificar que source_count >= 40
   - Verificar que incluye fuentes del usuario + auto-generadas

3. **Completar Flujo** (monitorear y descargar)

**Criterios de Éxito:**
- ✅ Sistema acepta 2 fuentes del usuario
- ✅ Sistema genera ~38 fuentes adicionales
- ✅ Total de fuentes >= min_sources (40)
- ✅ sources_generated_automatically = true
- ✅ Metadatos muestran conteo de user vs auto sources

---

### Escenario 6: Flujo Completo con WebSocket

**Objetivo:** Generar biografía y recibir notificaciones en tiempo real vía WebSocket.

**Pasos:**

1. **Conectar WebSocket**
   ```bash
   wscat -c "ws://localhost:8000/ws/notifications?user_id=test_user"
   → Recibir confirmación de conexión
   ```

2. **Crear Trabajo de Biografía**
   ```json
   POST /api/v1/biographies/generate
   {
     "character": "Nikola Tesla",
     "chapters": 10,
     "total_words": 10000,
     "mode": "automatic"
   }
   → Guardar job_id
   ```

3. **Reconectar WebSocket con job_id**
   ```bash
   wscat -c "ws://localhost:8000/ws/notifications?user_id=test_user&job_id={job_id}"
   ```

4. **Monitorear Notificaciones**
   - Recibir actualizaciones de progreso cada capítulo
   - Recibir notificación de completion

5. **Descargar cuando complete**

**Criterios de Éxito:**
- ✅ WebSocket conecta exitosamente
- ✅ Recibe confirmación de conexión
- ✅ Recibe updates de progreso en tiempo real
- ✅ Recibe notificación de completion
- ✅ download_url incluido en mensaje de completion

**Mensajes Esperados:**
1. Connection confirmation
2. Progress updates (10 veces, uno por capítulo)
3. Completion notification

---

## Escenarios de Error

### Escenario 7: Fuentes Insuficientes - Modo Manual

**Objetivo:** Verificar que el sistema rechaza requests con muy pocas fuentes en modo manual.

**Pasos:**

1. **Intentar Crear Trabajo con Pocas Fuentes**
   ```json
   POST /api/v1/biographies/generate
   {
     "character": "Test Character",
     "mode": "manual",
     "sources": [
       "https://example.com/source1",
       "https://example.com/source2"
     ]
   }
   ```

**Criterios de Éxito:**
- ✅ Request es rechazado con 400 Bad Request
- ✅ Mensaje de error explica mínimo de fuentes requerido
- ✅ Detail: "Manual mode requires at least 10 sources"

**Resultado Esperado:**
```json
{
  "detail": "Source generation failed: Manual mode requires at least 10 sources, got 2"
}
```

---

### Escenario 8: Job No Encontrado

**Objetivo:** Verificar manejo de job_id inválido.

**Pasos:**

1. **Intentar Obtener Status de Job Inexistente**
   ```
   GET /api/v1/biographies/00000000-0000-0000-0000-000000000000/status
   ```

2. **Intentar Descargar Job Inexistente**
   ```
   GET /api/v1/biographies/00000000-0000-0000-0000-000000000000/download
   ```

**Criterios de Éxito:**
- ✅ Ambos requests retornan 404 Not Found
- ✅ Mensaje de error claro: "Job {job_id} not found"

---

### Escenario 9: Descarga Prematura

**Objetivo:** Verificar que no se puede descargar una biografía antes de que esté completa.

**Pasos:**

1. **Crear Trabajo**
   ```json
   POST /api/v1/biographies/generate
   {
     "character": "Test Character",
     "chapters": 20,
     "mode": "automatic"
   }
   ```

2. **Intentar Descargar Inmediatamente**
   ```
   GET /api/v1/biographies/{job_id}/download
   ```

**Criterios de Éxito:**
- ✅ Request retorna 400 Bad Request
- ✅ Detail indica status actual: "Job is not completed yet. Current status: pending"

---

### Escenario 10: URLs Inválidas en Validación

**Objetivo:** Verificar detección de URLs mal formadas.

**Pasos:**

1. **Validar Fuentes con URLs Inválidas**
   ```json
   POST /api/v1/sources/validate
   {
     "sources": [
       {
         "title": "Invalid Source",
         "url": "not-a-url",
         "source_type": "url"
       },
       {
         "title": "Missing Protocol",
         "url": "www.example.com",
         "source_type": "url"
       }
     ],
     "check_accessibility": true
   }
   ```

**Criterios de Éxito:**
- ✅ Request completa con 200 OK (no error, pero fuentes inválidas)
- ✅ valid_sources = 0
- ✅ invalid_sources = 2
- ✅ Issues incluyen "Invalid URL format"

---

### Escenario 11: Rate Limiting

**Objetivo:** Verificar que el rate limiting funciona correctamente.

**Pasos:**

1. **Ejecutar Múltiples Requests Rápidos**
   ```bash
   for i in {1..70}; do
     curl http://localhost:8000/health
   done
   ```

2. **Verificar Respuesta de Rate Limit**

**Criterios de Éxito:**
- ✅ Primeros 60 requests retornan 200 OK
- ✅ Requests 61-70 retornan 429 Too Many Requests
- ✅ Mensaje: "Rate limit exceeded"
- ✅ Después de 1 minuto, requests vuelven a funcionar

---

## Escenarios de Performance

### Escenario 12: Generación de Biografía Larga

**Objetivo:** Validar que el sistema puede generar biografías extensas.

**Pasos:**

1. **Crear Trabajo Grande**
   ```json
   POST /api/v1/biographies/generate
   {
     "character": "Winston Churchill",
     "chapters": 20,
     "total_words": 51000,
     "mode": "automatic"
   }
   ```

2. **Monitorear Progreso**
   - Verificar que progress se actualiza correctamente
   - Medir tiempo por capítulo

**Criterios de Éxito:**
- ✅ Trabajo se completa exitosamente
- ✅ Todos los 20 capítulos generados
- ✅ Total words ≈ 51000 (±10%)
- ✅ Tiempo total < 15 minutos
- ✅ Sin errores de timeout
- ✅ Archivo descargable contiene todos los capítulos

**Métricas Esperadas:**
- Tiempo por capítulo: ~30-40 segundos
- Tiempo total: ~10-13 minutos
- Words por capítulo: ~2550

---

### Escenario 13: Generación Automática de Fuentes a Gran Escala

**Objetivo:** Verificar que la generación automática puede producir 60+ fuentes.

**Pasos:**

1. **Generar Muchas Fuentes**
   ```json
   POST /api/v1/sources/generate-automatic
   {
     "character_name": "Napoleon Bonaparte",
     "min_sources": 60,
     "max_sources": 80,
     "min_relevance": 0.7,
     "min_credibility": 80.0
   }
   ```

**Criterios de Éxito:**
- ✅ Genera entre 60-80 fuentes
- ✅ Todas las fuentes pasan validación
- ✅ average_relevance >= 0.7
- ✅ average_credibility >= 80.0
- ✅ Tiempo de generación < 30 segundos
- ✅ Diversidad de tipos de fuentes

---

### Escenario 14: Validación Avanzada de Muchas Fuentes

**Objetivo:** Verificar performance de validación avanzada con muchas fuentes.

**Pasos:**

1. **Generar 50 Fuentes Primero**
   ```json
   POST /api/v1/sources/generate-automatic
   { "character_name": "Marie Curie", "min_sources": 50, "max_sources": 50 }
   → Guardar fuentes generadas
   ```

2. **Validar con Análisis Avanzado**
   ```json
   POST /api/v1/sources/validate-advanced
   {
     "biography_topic": "Marie Curie",
     "sources": [...50 sources...],
     "check_accessibility": true,
     "min_relevance": 0.7,
     "min_credibility": 80.0
   }
   ```

**Criterios de Éxito:**
- ✅ Validación completa en < 60 segundos
- ✅ Todas las fuentes analizadas
- ✅ Scores de relevancia calculados
- ✅ Scores de credibilidad calculados
- ✅ Recomendaciones provistas

---

## Escenarios de Validación

### Escenario 15: Validación de Fuentes Mixtas

**Objetivo:** Validar mezcla de fuentes buenas y malas.

**Pasos:**

1. **Validar Lista Mixta**
   ```json
   POST /api/v1/sources/validate
   {
     "sources": [
       {
         "title": "Wikipedia Article",
         "url": "https://en.wikipedia.org/wiki/Test",
         "source_type": "url"
       },
       {
         "title": "Invalid URL",
         "url": "not-valid",
         "source_type": "url"
       },
       {
         "title": "Broken Link",
         "url": "https://example.com/404-page",
         "source_type": "url"
       },
       {
         "title": "Valid Book",
         "author": "John Doe",
         "source_type": "book",
         "publication_date": "2020"
       }
     ],
     "check_accessibility": true
   }
   ```

**Criterios de Éxito:**
- ✅ Request completa con 200 OK
- ✅ 2 fuentes válidas, 2 inválidas
- ✅ Issues detallados para cada fuente
- ✅ Summary correcto con porcentajes

---

### Escenario 16: Generación Híbrida con Fuentes Inválidas

**Objetivo:** Verificar que el sistema filtra fuentes inválidas del usuario en modo híbrido.

**Pasos:**

1. **Proveer Mezcla de Fuentes Válidas e Inválidas**
   ```json
   POST /api/v1/sources/generate-hybrid
   {
     "character_name": "Isaac Newton",
     "user_sources": [
       "https://en.wikipedia.org/wiki/Isaac_Newton",
       "not-a-valid-url",
       "https://www.britannica.com/biography/Isaac-Newton",
       "broken-link"
     ],
     "auto_complete": true,
     "target_count": 40
   }
   ```

**Criterios de Éxito:**
- ✅ Sistema acepta solo fuentes válidas (2 de 4)
- ✅ Sistema genera ~38 fuentes adicionales
- ✅ Total final = 40 fuentes válidas
- ✅ Suggestions incluyen info sobre fuentes rechazadas
- ✅ user_source_count = 2 (solo las válidas)

---

## 🎯 Checklist de Testing Completo

Antes de considerar la API como completamente funcional, ejecutar:

### Funcionalidad Básica
- [ ] Escenario 1: Verificación de Salud de la API
- [ ] Escenario 2: Verificación de Métricas

### Flujos Completos
- [ ] Escenario 3: Generación Automática (Happy Path)
- [ ] Escenario 4: Generación Manual
- [ ] Escenario 5: Generación Híbrida
- [ ] Escenario 6: Flujo con WebSocket

### Manejo de Errores
- [ ] Escenario 7: Fuentes Insuficientes
- [ ] Escenario 8: Job No Encontrado
- [ ] Escenario 9: Descarga Prematura
- [ ] Escenario 10: URLs Inválidas
- [ ] Escenario 11: Rate Limiting

### Performance
- [ ] Escenario 12: Biografía Larga (20 capítulos)
- [ ] Escenario 13: Generación de 60+ Fuentes
- [ ] Escenario 14: Validación de 50+ Fuentes

### Validación
- [ ] Escenario 15: Validación de Fuentes Mixtas
- [ ] Escenario 16: Generación Híbrida con Inválidas

---

## 📊 Métricas de Éxito

### KPIs del Sistema

| Métrica | Target | Crítico |
|---------|--------|---------|
| Tiempo por capítulo | < 40s | < 60s |
| Generación de 40 fuentes | < 15s | < 30s |
| Validación de 50 fuentes | < 60s | < 120s |
| Uptime de la API | > 99% | > 95% |
| Rate de éxito de generación | > 95% | > 90% |

### Tiempos de Respuesta

| Endpoint | Target | Máximo |
|----------|--------|--------|
| GET /health | < 100ms | < 500ms |
| GET /api/v1/status | < 200ms | < 1s |
| POST /biographies/generate | < 1s | < 5s |
| GET /biographies/{id}/status | < 200ms | < 1s |
| POST /sources/validate | < 5s | < 15s |
| POST /sources/generate-automatic | < 15s | < 30s |

---

## 🔄 Testing Continuo

### Regression Testing
Ejecutar todos los escenarios después de:
- Cambios en el código de la API
- Actualizaciones del modelo IA
- Cambios en configuración
- Nuevas versiones de dependencias

### Load Testing
Ejecutar periódicamente:
- 100 requests concurrentes a /health
- 10 generaciones de biografía simultáneas
- 50 validaciones de fuentes simultáneas

### Monitoring
Verificar continuamente:
- Métricas de Prometheus
- Logs de errores
- Tiempos de respuesta
- Rate de éxito/fallo

---

**Última actualización:** Enero 2025  
**Versión de la API:** v1  
**Total de Escenarios:** 16
