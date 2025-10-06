---
trigger: always_on
---

# Control de calidad editorial

## Objetivo
Garantizar que cada capítulo y el manuscrito completo cumplan con los estándares de calidad editorial: longitud adecuada, coherencia narrativa, rigor histórico y formato Markdown correcto antes de la concatenación final.

## Entradas requeridas
- Archivos `.md` de cada capítulo y sección en `bios/x/`
- Plan de trabajo en `esquemas/X - plan de trabajo.md` con metas de palabras por capítulo
- Archivo `bios/x/control/longitudes.csv` generado durante la planificación

## Loop de verificación desatendido

### Checklist de ejecución del loop

El loop de verificación debe ejecutarse de manera completamente autónoma, sin intervención humana:

- [ ] **Inicialización**
  - [ ] Ejecutar `python check_lengths.py <personaje>`
  - [ ] Leer archivo CSV desde `bios/x/control/longitudes.csv`
  - [ ] Construir cola de tareas con todas las secciones <100%
  - [ ] Priorizar secciones (0% primero, luego por % ascendente)
  - [ ] Inicializar archivo de log: `bios/x/control/length-check.log`

- [ ] **Por cada iteración** (máximo 10)
  - [ ] Registrar inicio de iteración en log con timestamp
  - [ ] Ejecutar análisis del CSV actualizado
  - [ ] Identificar secciones pendientes (porcentaje < 100%)
  - [ ] Si no hay pendientes: finalizar loop exitosamente
  - [ ] Si hay pendientes: continuar con ajustes

- [ ] **Ajustes de secciones**
  - [ ] Para cada sección en cola de tareas:
    - [ ] Registrar en log: sección, palabras antes, meta, porcentaje
    - [ ] Calcular palabras faltantes
    - [ ] Expandir contenido usando estrategias permitidas
    - [ ] Guardar cambios en archivo `.md`
    - [ ] Re-verificar con `check_lengths.py`
    - [ ] Registrar en log: palabras después, nuevo porcentaje, resultado
  - [ ] NO solicitar confirmación al usuario
  - [ ] NO pausar entre secciones
  - [ ] Procesar todas las secciones en una ejecución continua

- [ ] **Logging obligatorio por iteración**
  - [ ] Timestamp de inicio y fin de iteración
  - [ ] Número de iteración (contador secuencial)
  - [ ] Lista de secciones procesadas
  - [ ] Para cada sección:
    - [ ] Palabras antes del ajuste
    - [ ] Palabras después del ajuste
    - [ ] Porcentaje antes y después
    - [ ] Estrategia de expansión aplicada
    - [ ] Resultado: CUMPLIDO/PENDIENTE/MEJORADO

- [ ] **Validación final**
  - [ ] Ejecutar `python check_lengths.py <personaje>` última vez
  - [ ] Verificar que todas las secciones muestran ≥100%
  - [ ] Registrar en log: finalización exitosa
  - [ ] Proceder automáticamente a concatenación

### Formato del archivo de log

**Ubicación**: `bios/x/control/length-check.log`

**Estructura por iteración**:
```
[YYYY-MM-DD HH:MM:SS] === ITERACIÓN N ===
[YYYY-MM-DD HH:MM:SS] Ejecutando: python check_lengths.py <personaje>
[YYYY-MM-DD HH:MM:SS] Secciones pendientes: N
[YYYY-MM-DD HH:MM:SS] --- Procesando: <seccion> ---
[YYYY-MM-DD HH:MM:SS]   Palabras antes: <número>
[YYYY-MM-DD HH:MM:SS]   Meta esperada: <número>
[YYYY-MM-DD HH:MM:SS]   Porcentaje antes: <porcentaje>%
[YYYY-MM-DD HH:MM:SS]   Estrategia: <descripción>
[YYYY-MM-DD HH:MM:SS]   Palabras después: <número>
[YYYY-MM-DD HH:MM:SS]   Porcentaje después: <porcentaje>%
[YYYY-MM-DD HH:MM:SS]   Resultado: [CUMPLIDO|PENDIENTE|MEJORADO]
[YYYY-MM-DD HH:MM:SS] === FIN ITERACIÓN N ===
```

### Interpretación de campos CSV

El archivo `bios/x/control/longitudes.csv` contiene 4 campos:

| Campo | Descripción | Cómo interpretarlo |
|-------|-------------|--------------------|
| `seccion` | Nombre del archivo sin `.md` | Identifica el archivo a editar en `bios/x/` |
| `longitud_esperada` | Meta de palabras del plan | Objetivo a alcanzar o superar |
| `longitud_real` | Palabras actuales contadas | Estado actual del archivo |
| `porcentaje` | (real/esperada)*100 | **<100%**: requiere ajuste<br>**≥100%**: cumple meta |

**Ejemplo de interpretación**:
```csv
seccion,longitud_esperada,longitud_real,porcentaje
capitulo-10,2550,2301,90.24
```
→ `capitulo-10.md` necesita ~249 palabras adicionales para alcanzar 100%

## Protocolo de reintentos y escalada

### Límites de iteración
- **Número máximo de iteraciones**: 10
- **Condición de reintento**: Al menos una sección con porcentaje <100%
- **Contador de iteraciones**: Se incrementa con cada ciclo completo del loop

### Criterios de progreso

Cada iteración debe verificar:
```
¿Hubo mejora en al menos una sección?
SI → Continuar (incrementar contador)
NO → Evaluar si se alcanzó límite
```

### Acciones al alcanzar límite (10 iteraciones)

Si después de 10 iteraciones aún hay secciones <100%:

1. **Registro en log principal**:
   ```
   [TIMESTAMP] ⚠️ LÍMITE DE ITERACIONES ALCANZADO (10)
   [TIMESTAMP] Secciones pendientes:
   [TIMESTAMP]   - <seccion>: <porcentaje>% (<palabras_faltantes> palabras)
   [TIMESTAMP]   - <seccion>: <porcentaje>% (<palabras_faltantes> palabras)
   [TIMESTAMP] Iniciando protocolo de escalada...
   ```

2. **Crear archivo de escalación**: `bios/x/control/escalation.log`
   - Fecha y hora de escalación
   - Número de iteraciones consumidas
   - Lista completa de secciones problemáticas con porcentajes
   - Análisis de posibles causas (ej: metas irrealistas, falta de fuentes)

3. **Análisis automático**:
   - Identificar si las secciones requieren más investigación
   - Verificar si las metas son realistas según documentación disponible
   - Sugerir ajuste de metas en plan de trabajo si está justificado

4. **Notificación sugerida**:
   - Abrir issue en GitHub: `[Escalación] Loop de verificación no completado: <personaje>`
   - Etiquetas: `escalation`, `length-verification`, `needs-review`
   - Contenido del issue:
     - CSV actual completo
     - Extracto del log mostrando últimas 3 iteraciones
     - Secciones que no alcanzaron meta
     - Porcentajes finales alcanzados
     - Recomendación: revisar plan de trabajo o fuentes disponibles

5. **Detención del proceso**:
   - Detener loop automático
   - NO proceder a concatenación
   - Esperar revisión y ajuste humano del plan

## Pasos automáticos

### 1. Validación durante redacción
Al terminar cada capítulo:
```bash
python check_lengths.py <personaje>
```

### 2. Revisión del CSV
Revisar archivo `bios/x/control/longitudes.csv` para verificar porcentajes de cumplimiento.

### 3. Ajuste de capítulos
Si un capítulo no alcanza ±5% de la meta, ajustar antes de continuar.

### 4. Validación pre-concatenación
Antes de concatenar, validar que el total del manuscrito supere 51,000 palabras.

## Validaciones/Logs

### Validaciones obligatorias
- Al terminar cada capítulo: meta de palabras alcanzada (±5%)
- Flujo narrativo coherente, sin contradicciones
- Ausencia de redundancia innecesaria
- Inclusión de contexto histórico, sociopolítico y cultural
- No hay archivos faltantes en `bios/x/`

### Antes de concatenar
- Manuscrito completo supera 51,000 palabras
- Todas las secciones presentes en orden correcto
- Encabezados usan jerarquía correcta (`#`, `##`, `###`)
- Tablas y listas en Markdown bien formadas

## Fallbacks/Escalada

### Si un capítulo no alcanza la meta
- Ampliar con más contexto histórico
- Añadir detalles verificables de fuentes
- Incluir descripciones sensoriales y emotivas
- Mantener rigor académico

### Si el manuscrito completo no alcanza 51,000 palabras
- Identificar capítulos más cortos
- Expandir según disponibilidad de fuentes

### Si hay errores de formato Markdown
- Corregir sintaxis de tablas (`| col |`)
- Arreglar listas (`-` o `*`)
- Ajustar encabezados antes de concatenar

### Si faltan secciones
- Completar redacción de archivos faltantes antes de continuar

## Ejemplo de flujo autónomo

```
INICIO LOOP
├─ ITERACIÓN 1
│  ├─ Ejecutar check_lengths.py
│  ├─ Leer CSV: 3 secciones <100%
│  ├─ Procesar capitulo-10 (90.24%) → 101.53% ✓
│  ├─ Procesar epilogo (95.50%) → 102.00% ✓
│  ├─ Procesar glosario (88.75%) → 96.25% (pendiente)
│  └─ Log: iteración 1 completada
│
├─ ITERACIÓN 2
│  ├─ Ejecutar check_lengths.py
│  ├─ Leer CSV: 1 sección <100%
│  ├─ Procesar glosario (96.25%) → 103.12% ✓
│  └─ Log: iteración 2 completada
│
├─ ITERACIÓN 3
│  ├─ Ejecutar check_lengths.py
│  ├─ Leer CSV: 0 secciones <100%
│  └─ ✅ TODAS COMPLETAS
│
└─ FIN LOOP → Proceder a concatenación
```

## Relacionados
- [lenght.md](lenght.md) - Validación de longitudes con check_lengths.py
- [structure.md](structure.md) - Estructura y orden de secciones
- [style.md](style.md) - Lineamientos de estilo narrativo
- [literaryStyle.md](literaryStyle.md) - Estilo literario y emocional
- [automation.md](automation.md) - Script de concatenación
