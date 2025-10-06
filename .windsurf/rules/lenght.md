---
trigger: always_on
---

Debes validar la longitud de capítulos y secciones antes de la concatenación y hacer las correcciones necesarias y ajustes que requiera cada uno antes de concatenar. Todos los capítulos y secciones deben cumplir la meta establecida en el plan.

## Objetivo
Ejecutar el loop de verificación de longitudes de manera completamente autónoma, sin intervención humana, hasta que todas las secciones alcancen o superen el 100% de cumplimiento.

## Entradas requeridas
- Archivo CSV de control: `bios/x/control/longitudes.csv`
- Archivos de sección en `bios/x/*.md`
- Nombre normalizado del personaje (minúsculas, guiones bajos)

## Ejecución del script check_lengths.py

### Comando
```bash
python check_lengths.py <personaje>
```
Ejemplo:
```bash
python check_lengths.py joseph_stalin
```

### Proceso del script
1. **Validación inicial**: Verifica que exista `bios/x/control/longitudes.csv`
2. **Lectura de metas**: Carga las longitudes esperadas desde el CSV
3. **Conteo de palabras**: Para cada sección, cuenta palabras reales usando `split()`
4. **Cálculo de porcentajes**: `(longitud_real / longitud_esperada) * 100`
5. **Actualización del CSV**: Guarda resultados actualizados con 4 campos

### Campos del CSV longitudes.csv
El archivo CSV contiene exactamente 4 campos:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| `seccion` | Nombre del archivo sin extensión | `capitulo-01`, `prologo`, `introduccion` |
| `longitud_esperada` | Meta de palabras definida en el plan | `2550`, `1800`, `2400` |
| `longitud_real` | Palabras actuales en el archivo | `2765`, `1973`, `2617` |
| `porcentaje` | Cumplimiento calculado (redondeado a 2 decimales) | `108.43`, `109.61`, `109.04` |

### Interpretación del CSV
- **≥100%**: Sección cumple meta, no requiere ajustes
- **<100%**: Sección requiere expansión inmediata
- **0%**: Archivo no existe o está vacío, requiere redacción completa

## Loop de verificación desatendido

### Construcción de la cola de tareas

Al inicio de cada iteración del loop:

1. **Ejecutar** `python check_lengths.py <personaje>`
2. **Leer** `bios/x/control/longitudes.csv`
3. **Filtrar** secciones con `porcentaje < 100`
4. **Ordenar** por prioridad:
   - Primero: Secciones con 0% (archivos faltantes o vacíos)
   - Segundo: Secciones ordenadas por porcentaje ascendente (las más alejadas de la meta primero)
5. **Crear lista de tareas** interna para procesamiento sin interrupciones

### Checklist por iteración

Cada iteración del loop debe completar:

- [ ] Ejecutar `python check_lengths.py <personaje>`
- [ ] Leer CSV actualizado desde `bios/x/control/longitudes.csv`
- [ ] Identificar todas las secciones con `porcentaje < 100`
- [ ] Priorizar secciones según criterio establecido
- [ ] Para cada sección pendiente:
  - [ ] Calcular palabras faltantes: `(longitud_esperada - longitud_real)`
  - [ ] Expandir contenido agregando:
    - Contexto histórico verificable
    - Detalles sensoriales y emotivos
    - Descripciones de ambiente y época
    - Análisis de motivaciones y consecuencias
  - [ ] Mantener rigor académico y tono narrativo-literario
  - [ ] Guardar cambios en el archivo `.md`
- [ ] Registrar iteración en log (ver sección de Logging)
- [ ] Volver a ejecutar verificación (nueva iteración)

### Ajustes de contenido

Para expandir secciones que no cumplen meta (<100%):

**Estrategias permitidas**:
- Ampliar contexto histórico, sociopolítico y cultural
- Añadir descripciones sensoriales (visuales, auditivas, ambientales)
- Profundizar en análisis de motivaciones y consecuencias
- Incluir detalles verificables de fuentes disponibles
- Desarrollar atmósfera y tono emocional envolvente

**Restricciones**:
- NO usar citas directas textuales
- NO añadir datos no verificables o ficticios
- NO repetir contenido (evitar redundancia)
- NO cambiar el enfoque temático del capítulo/sección
- Mantener coherencia narrativa con secciones adyacentes

## Logging del proceso

### Ubicación del log
```
bios/x/control/length-check.log
```

### Formato de registro

Cada iteración debe registrar:

```
[TIMESTAMP] === ITERACIÓN N ===
[TIMESTAMP] Ejecutando: python check_lengths.py <personaje>
[TIMESTAMP] Secciones pendientes: N
[TIMESTAMP] --- Procesando: <seccion> ---
[TIMESTAMP]   Palabras antes: <longitud_real_anterior>
[TIMESTAMP]   Meta esperada: <longitud_esperada>
[TIMESTAMP]   Porcentaje antes: <porcentaje_anterior>%
[TIMESTAMP]   Estrategia: <descripción_breve>
[TIMESTAMP]   Palabras después: <longitud_real_nueva>
[TIMESTAMP]   Porcentaje después: <porcentaje_nuevo>%
[TIMESTAMP]   Resultado: [CUMPLIDO|PENDIENTE|MEJORADO]
[TIMESTAMP] === FIN ITERACIÓN N ===
```

### Ejemplo de log real
```
[2024-01-15 14:23:01] === ITERACIÓN 1 ===
[2024-01-15 14:23:01] Ejecutando: python check_lengths.py harry_s_truman
[2024-01-15 14:23:02] Secciones pendientes: 3
[2024-01-15 14:23:02] --- Procesando: capitulo-10 ---
[2024-01-15 14:23:02]   Palabras antes: 2301
[2024-01-15 14:23:02]   Meta esperada: 2550
[2024-01-15 14:23:02]   Porcentaje antes: 90.24%
[2024-01-15 14:23:02]   Estrategia: Expandir contexto de la Guerra de Corea y decisiones diplomáticas
[2024-01-15 14:23:35]   Palabras después: 2589
[2024-01-15 14:23:35]   Porcentaje después: 101.53%
[2024-01-15 14:23:35]   Resultado: CUMPLIDO
[2024-01-15 14:23:35] === FIN ITERACIÓN 1 ===
```

### Información mínima por iteración
- **Timestamp**: Fecha y hora en formato ISO o legible
- **Número de iteración**: Contador secuencial
- **Sección trabajada**: Nombre exacto del archivo
- **Palabras antes**: Longitud real antes de ajustes
- **Palabras después**: Longitud real después de ajustes
- **Porcentaje antes/después**: Cumplimiento calculado
- **Resultado**: Estado final (CUMPLIDO/PENDIENTE/MEJORADO)

## Criterios de terminación

### Condición de éxito
El loop termina cuando **TODAS** las secciones cumplen:
```
porcentaje >= 100.0
```

### Validación final
Al terminar el loop:
- [ ] Ejecutar `python check_lengths.py <personaje>` una última vez
- [ ] Verificar que CSV muestra 100% o más en todas las filas
- [ ] Registrar en log: `[TIMESTAMP] ✅ TODAS LAS SECCIONES COMPLETAS - TERMINANDO LOOP`
- [ ] Proceder a paso siguiente del workflow (concatenación)

## Protocolo de reintentos y escalada

### Límite de iteraciones
- **Máximo de iteraciones sin éxito**: 10 iteraciones
- **Criterio de iteración sin éxito**: Al menos una sección sigue <100% después del ajuste

### Verificación de progreso
Cada iteración debe verificar:
```
¿Hubo mejora en al menos una sección?
SI → Continuar loop (incrementar contador)
NO → Verificar si se alcanzó límite de iteraciones
```

### Acciones de escalada

Si se alcanzan 10 iteraciones sin completar todas las secciones:

1. **Registrar en log**:
   ```
   [TIMESTAMP] ⚠️ LÍMITE DE ITERACIONES ALCANZADO (10)
   [TIMESTAMP] Secciones pendientes: <lista_secciones>
   [TIMESTAMP] Escalando problema...
   ```

2. **Revisar estrategia**:
   - Identificar si las secciones requieren más fuentes
   - Verificar si las metas son realistas según disponibilidad de información
   - Considerar ajuste de metas en `longitudes.csv` si está justificado

3. **Notificación**:
   - Registrar situación en archivo `bios/x/control/escalation.log`
   - Incluir: secciones problemáticas, porcentajes alcanzados, iteraciones consumidas
   - Detener loop y solicitar revisión humana del plan de trabajo

4. **Acción sugerida para escalación**:
   - Abrir issue en el repositorio con título: `[Escalación] Loop de verificación no completado: <personaje>`
   - Incluir en issue: CSV actual, log completo, análisis de secciones problemáticas
   - Etiquetar: `escalation`, `length-verification`, `needs-review`

## Pseudo-código de ejecución autónoma

```python
def autonomous_length_verification_loop(personaje):
    """
    Loop de verificación completamente autónomo.
    NO requiere intervención humana durante ejecución.
    """
    max_iterations = 10
    iteration = 0
    log_file = f"bios/{personaje}/control/length-check.log"
    
    while iteration < max_iterations:
        iteration += 1
        log(f"=== ITERACIÓN {iteration} ===")
        
        # Ejecutar script de verificación
        run_command(f"python check_lengths.py {personaje}")
        
        # Leer CSV actualizado
        csv_data = read_csv(f"bios/{personaje}/control/longitudes.csv")
        
        # Construir cola de tareas
        pending = [row for row in csv_data if row['porcentaje'] < 100]
        
        if not pending:
            log("✅ TODAS LAS SECCIONES COMPLETAS - TERMINANDO LOOP")
            return True  # Éxito
        
        log(f"Secciones pendientes: {len(pending)}")
        
        # Priorizar: 0% primero, luego por porcentaje ascendente
        pending.sort(key=lambda x: (x['porcentaje'] == 0, x['porcentaje']))
        
        # Procesar cada sección pendiente
        for section in pending:
            log(f"--- Procesando: {section['seccion']} ---")
            log(f"  Palabras antes: {section['longitud_real']}")
            log(f"  Meta esperada: {section['longitud_esperada']}")
            log(f"  Porcentaje antes: {section['porcentaje']}%")
            
            # Calcular palabras faltantes
            words_needed = section['longitud_esperada'] - section['longitud_real']
            
            # Expandir contenido (proceso de IA)
            expand_section_content(
                personaje=personaje,
                section=section['seccion'],
                words_needed=words_needed,
                strategy="contexto histórico, detalles verificables, tono envolvente"
            )
            
            # Verificar resultado
            run_command(f"python check_lengths.py {personaje}")
            updated_data = read_csv(f"bios/{personaje}/control/longitudes.csv")
            updated_section = find_section(updated_data, section['seccion'])
            
            log(f"  Palabras después: {updated_section['longitud_real']}")
            log(f"  Porcentaje después: {updated_section['porcentaje']}%")
            
            if updated_section['porcentaje'] >= 100:
                log(f"  Resultado: CUMPLIDO")
            else:
                log(f"  Resultado: PENDIENTE")
        
        log(f"=== FIN ITERACIÓN {iteration} ===")
    
    # Si llegamos aquí, se alcanzó el límite
    log("⚠️ LÍMITE DE ITERACIONES ALCANZADO (10)")
    escalate_to_human_review(personaje, csv_data, log_file)
    return False  # Escalación

# Ejecución
if __name__ == "__main__":
    personaje = sys.argv[1]
    success = autonomous_length_verification_loop(personaje)
    if success:
        print("Procediendo a concatenación...")
    else:
        print("Requiere revisión humana.")
```

## Flujo de ejecución paso a paso

### Paso 1: Inicio del loop
- Ejecutar primera verificación
- Construir lista completa de secciones pendientes
- NO solicitar confirmación al usuario
- NO mostrar reportes intermedios

### Paso 2: Iteración continua
- Para cada sección en cola:
  - Leer estado actual del CSV
  - Expandir contenido según estrategias permitidas
  - Guardar cambios automáticamente
  - Registrar en log
- Pasar inmediatamente a siguiente sección
- NO pausar entre secciones

### Paso 3: Re-verificación
- Al completar todas las secciones de la iteración
- Ejecutar `check_lengths.py` nuevamente
- Actualizar cola de tareas
- Si quedan pendientes: nueva iteración
- Si todas completas: terminar loop

### Paso 4: Finalización
- Registrar finalización exitosa en log
- Continuar automáticamente al paso siguiente del workflow
- NO solicitar intervención humana

## Relacionados
- [quality.md](quality.md) - Control de calidad editorial
- [structure.md](structure.md) - Estructura de secciones
- [workflow.md](workflow.md) - Flujo completo de biografías
- [automation.md](automation.md) - Scripts de automatización