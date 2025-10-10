# Colección Postman para BookGen API

Esta colección proporciona todos los endpoints de la API de BookGen para facilitar el testing y desarrollo.

## 📋 Contenido

- **BookGen_API_Collection.json**: Colección completa de Postman con todos los endpoints
- **BookGen_Environment.json**: Variables de entorno preconfiguradas para uso local
- **examples/**: Ejemplos de uso y escenarios de prueba

## 🚀 Instalación

### Requisitos Previos

1. Tener instalado [Postman](https://www.postman.com/downloads/)
2. BookGen API corriendo localmente en `http://localhost:8000`

### Pasos de Instalación

1. **Importar la Colección**
   - Abre Postman
   - Click en "Import" (botón superior izquierdo)
   - Selecciona el archivo `BookGen_API_Collection.json`
   - Click en "Import"

2. **Importar el Entorno**
   - Click en "Import" nuevamente
   - Selecciona el archivo `BookGen_Environment.json`
   - Click en "Import"

3. **Seleccionar el Entorno**
   - En la esquina superior derecha, selecciona "BookGen Local" del dropdown de entornos
   - Verifica que las variables estén configuradas correctamente

## 🎯 Uso

### Flujo de Trabajo Recomendado

#### 1. Verificar Estado de la API

```
1. Health Check → Verifica que la API esté funcionando
2. API Status → Obtiene configuración actual
3. Prometheus Metrics → Revisa métricas del sistema
```

#### 2. Generar una Biografía (Flujo Completo)

```
1. Generate Biography → Crea un trabajo de generación
   - El test automático guarda el job_id en las variables de entorno
   
2. Get Job Status → Monitorea el progreso
   - Ejecuta múltiples veces hasta que status = "completed"
   
3. Download Biography → Descarga el resultado cuando esté listo
```

#### 3. Trabajar con Fuentes

**Validación Simple:**
```
Sources → Validate Sources
```

**Validación Avanzada con IA:**
```
Sources → Validate Sources (Advanced)
```

**Generación Automática:**
```
Sources → Generate Sources (Automatic)
```

**Modo Híbrido:**
```
Sources → Generate Sources (Hybrid)
```

### Variables de Entorno

La colección utiliza las siguientes variables:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `base_url` | URL base de la API | `http://localhost:8000` |
| `api_version` | Versión de la API | `v1` |
| `job_id` | ID del trabajo actual | (Se actualiza automáticamente) |
| `character` | Nombre del personaje | `harry_s_truman` |
| `websocket_url` | URL de WebSocket | `ws://localhost:8000` |
| `timestamp` | Timestamp generado | (Se genera automáticamente) |

### Modificar Variables

Para cambiar los valores de las variables:

1. Click en el icono de ojo 👁️ junto al selector de entorno
2. Click en "Edit" junto a "BookGen Local"
3. Modifica los valores según necesites
4. Click en "Save"

## 📝 Ejemplos de Requests

### Generar Biografía (Modo Automático)

```json
POST /api/v1/biographies/generate
{
  "character": "Albert Einstein",
  "chapters": 10,
  "total_words": 10000,
  "mode": "automatic",
  "min_sources": 40,
  "quality_threshold": 0.8,
  "temperature": 0.7
}
```

### Generar Biografía (Modo Manual)

```json
POST /api/v1/biographies/generate
{
  "character": "Marie Curie",
  "chapters": 15,
  "total_words": 15000,
  "mode": "manual",
  "sources": [
    "https://en.wikipedia.org/wiki/Marie_Curie",
    "https://www.nobelprize.org/prizes/physics/1903/marie-curie/biographical/",
    "... (mínimo 10 fuentes)"
  ],
  "temperature": 0.7
}
```

### Generar Biografía (Modo Híbrido)

```json
POST /api/v1/biographies/generate
{
  "character": "Leonardo da Vinci",
  "chapters": 20,
  "total_words": 20000,
  "mode": "hybrid",
  "sources": [
    "https://en.wikipedia.org/wiki/Leonardo_da_Vinci",
    "https://www.britannica.com/biography/Leonardo-da-Vinci"
  ],
  "min_sources": 40,
  "quality_threshold": 0.8,
  "temperature": 0.7
}
```

## 🧪 Tests Automáticos

Cada request incluye tests automáticos que:

- ✅ Verifican códigos de estado HTTP
- ✅ Validan estructura de respuestas
- ✅ Extraen y guardan `job_id` automáticamente
- ✅ Verifican tipos de datos esperados
- ✅ Validan rangos y valores específicos

### Ver Resultados de Tests

Después de ejecutar un request:

1. Revisa la pestaña "Test Results" en la parte inferior
2. Verde = Test pasado ✅
3. Rojo = Test fallido ❌

## 🔄 Pre-request Scripts

La colección incluye scripts que se ejecutan antes de cada request:

- **Generate Biography**: Genera un timestamp único
- **Get Job Status**: Valida que job_id esté definido
- **Download Biography**: Valida que job_id esté definido
- **Download Output ZIP**: Define character por defecto si no está configurado

## 🌐 WebSocket Testing

El endpoint de WebSocket (`/ws/notifications`) no puede probarse directamente en Postman con requests HTTP.

### Opciones para Probar WebSocket:

**Opción 1: Cliente WebSocket en línea de comandos**
```bash
npm install -g wscat
wscat -c "ws://localhost:8000/ws/notifications?user_id=test&job_id=123"
```

**Opción 2: Extensión de navegador**
- [Simple WebSocket Client](https://chrome.google.com/webstore/detail/simple-websocket-client/) para Chrome
- URL: `ws://localhost:8000/ws/notifications`

**Opción 3: Código JavaScript**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications?user_id=test');
ws.onmessage = (event) => console.log('Received:', event.data);
ws.send('ping');
```

## 📊 Endpoints Disponibles

### Health & Status
- `GET /health` - Health check básico
- `GET /api/v1/status` - Estado detallado de la API
- `GET /metrics` - Métricas de Prometheus

### Biographies
- `POST /api/v1/biographies/generate` - Generar biografía
- `GET /api/v1/biographies/{job_id}/status` - Estado del trabajo
- `GET /api/v1/biographies/{job_id}/download` - Descargar biografía
- `GET /api/v1/biographies/{character}/download-output` - 🆕 Descargar ZIP completo

### Sources
- `POST /api/v1/sources/validate` - Validar fuentes (básico)
- `POST /api/v1/sources/validate-advanced` - Validar fuentes (avanzado con IA)
- `POST /api/v1/sources/generate-automatic` - Generar fuentes automáticamente
- `POST /api/v1/sources/generate-hybrid` - Generar fuentes en modo híbrido

### WebSocket
- `GET /ws/status` - Estado de conexiones WebSocket
- `WS /ws/notifications` - WebSocket para notificaciones en tiempo real

## 🔧 Configuración para Otros Entornos

### Entorno de Producción

Crea un nuevo entorno en Postman con:

```json
{
  "base_url": "https://api.bookgen.com",
  "api_version": "v1",
  "websocket_url": "wss://api.bookgen.com"
}
```

### Entorno de Staging

```json
{
  "base_url": "https://staging.bookgen.com",
  "api_version": "v1",
  "websocket_url": "wss://staging.bookgen.com"
}
```

## 🐛 Troubleshooting

### Error: "Could not get response"

- ✅ Verifica que BookGen esté corriendo en `http://localhost:8000`
- ✅ Ejecuta `curl http://localhost:8000/health` para verificar
- ✅ Revisa los logs de la aplicación

### Error: "Job not found"

- ✅ Asegúrate de ejecutar "Generate Biography" primero
- ✅ Verifica que la variable `job_id` esté configurada
- ✅ El job_id se guarda automáticamente después de generar una biografía

### Error: "Job is not completed yet"

- ✅ Normal si el trabajo aún está en progreso
- ✅ Espera unos segundos y ejecuta "Get Job Status" nuevamente
- ✅ El tiempo estimado es ~30 segundos por capítulo

### Tests Fallando

- ✅ Verifica que el entorno "BookGen Local" esté seleccionado
- ✅ Revisa que las variables estén correctamente configuradas
- ✅ Asegúrate de que la API esté respondiendo correctamente

## 📚 Recursos Adicionales

- [Documentación Completa de la API](../docs/technical/components/API_DOCUMENTATION.md)
- [Quick Start Guide](../docs/technical/quickstart/QUICKSTART_API.md)
- [Ejemplos de Uso](./examples/sample_requests.md)
- [Escenarios de Prueba](./examples/test_scenarios.md)

## 🤝 Contribuir

Para agregar nuevos endpoints a la colección:

1. Agrega el endpoint en `BookGen_API_Collection.json`
2. Incluye tests automáticos
3. Documenta el endpoint en este README
4. Actualiza los ejemplos si es necesario

## 📝 Notas

- **Rate Limiting**: La API tiene límite de 60 requests por minuto por IP
- **Timeouts**: Los requests largos (ej: generar biografía) pueden tardar varios minutos
- **Auto-save**: El `job_id` se guarda automáticamente después de crear una biografía
- **Variables Collection vs Environment**: Las variables de entorno sobrescriben las de la colección

## 📞 Soporte

Para problemas o preguntas:

1. Revisa la [documentación de la API](../docs/technical/components/API_DOCUMENTATION.md)
2. Consulta los archivos de ejemplo en `./examples/`
3. Verifica los logs de la aplicación
4. Abre un issue en el repositorio

---

**Versión**: 1.0.0  
**Última Actualización**: Enero 2025  
**Compatibilidad**: BookGen API v1
