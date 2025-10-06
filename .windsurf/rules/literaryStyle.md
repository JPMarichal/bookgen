---
trigger: always_on
---

# Estilo literario y emocional

## Objetivo
Definir el tono emocional, literario y sensorial de la narrativa para lograr que el lector viva la historia de forma inmersiva, sintiendo que está presente en los acontecimientos y comprendiendo profundamente las motivaciones de los personajes. Complementa los lineamientos técnicos de style.md.

## Entradas requeridas
- Contenido histórico verificado con contexto sociopolítico y cultural.
- Comprensión de motivaciones, sentimientos y circunstancias del personaje.
- Conocimiento del ambiente, época y lugares relevantes.

## Pasos automáticos
1. Incorporar descripciones sensoriales en narraciones clave:
   - Texturas, olores, sonidos, sensaciones táctiles.
   - Ambiente visual de lugares y escenas importantes.
2. Usar adjetivos precisos y variados para enriquecer descripciones.
3. Emplear conectores literarios que den fluidez emocional.
4. Integrar planteamientos reflexivos ocasionales que inviten al lector a conectar con dilemas o decisiones del personaje.
5. Mostrar antecedentes y repercusiones de acciones para crear comprensión profunda.
6. Narrar de forma que el lector sienta estar viviendo la historia, no solo leyéndola.

## Validaciones/Logs
- **Tono general**: Narrativo con toque literario, emotivo y poético, sin llegar al apasionamiento.
- **Profundidad académica**: Mantener rigor histórico con estilo accesible y envolvente.
- **Inmersión sensorial**: Incluir descripciones de texturas, olores, sensaciones, ambiente.
- **Adjetivos y conectores**: Uso variado para enriquecer narrativa sin saturar.
- **Reflexiones**: Planteamientos ocasionales que ayuden al lector a comprender razonamientos y sentimientos detrás de conductas.
- **Antecedentes y repercusiones**: Contextualizar acciones para crear comprensión natural.
- **Resultado esperado**: El lector debe sentir que ha vivido una novela apasionante, no solo leído historia.
- **Emoción equilibrada**: Involucrar emocionalmente sin caer en dramatismo excesivo.

## Fallbacks/Escalada
- Si la narrativa resulta demasiado académica o seca: incorporar más elementos sensoriales, descripciones ambientales y reflexiones emocionales.
- Si el tono se vuelve demasiado apasionado: moderar adjetivos extremos y mantener equilibrio con rigor histórico.
- Si falta inmersión: añadir detalles de época, descripciones de lugares, texturas del entorno.
- Si el lector no conecta emocionalmente: profundizar en motivaciones internas del personaje, mostrar dilemas humanos universales.

## Validaciones automatizables

### Checklist de verificación

Al validar el estilo literario y emocional, un agente debe verificar:

- [ ] Verificar presencia de descripciones sensoriales en secciones narrativas clave
- [ ] Verificar uso de adjetivos precisos y variados (no repetitivos)
- [ ] Verificar presencia de conectores literarios que den fluidez
- [ ] Verificar que se incluyan reflexiones ocasionales sobre dilemas del personaje
- [ ] Verificar contextualización de acciones (antecedentes y repercusiones)
- [ ] Verificar equilibrio entre rigor académico y tono envolvente
- [ ] Verificar ausencia de dramatismo excesivo o apasionamiento
- [ ] Verificar que la narrativa sea inmersiva (no solo descriptiva)

### Evidencia a conservar

Para cada verificación completada, adjuntar:

- **Muestra de descripciones sensoriales**: Extractos representativos por capítulo
- **Análisis de vocabulario**: Lista de adjetivos y conectores utilizados
- **Muestra de reflexiones**: Extractos donde se muestran dilemas o motivaciones
- **Evaluación de tono**: Análisis cualitativo del equilibrio emocional

### Scripts a ejecutar

1. **Búsqueda de elementos sensoriales** (manual con keywords):
   ```bash
   # Buscar términos sensoriales (olor, sonido, textura, etc.)
   grep -i -E "(olor|aroma|sonido|textura|sabor|visión|contemplar)" bios/x/*.md \
     > bios/x/logs/literary-sensorial-<fecha>.log
   ```

2. **Análisis de adjetivos** (requiere procesamiento manual o NLP):
   ```bash
   # Extraer adjetivos comunes y verificar variedad
   # Guardar en: bios/x/logs/literary-adjectives-<fecha>.log
   ```

3. **Búsqueda de reflexiones**:
   ```bash
   # Buscar construcciones reflexivas
   grep -i -E "(pensaba|sentía|comprendía|cuestionaba|dilema|motivación)" bios/x/*.md \
     > bios/x/logs/literary-reflections-<fecha>.log
   ```

## Relacionados
- [style.md](style.md) - Lineamientos técnicos y formales (complementario)
- [quality.md](quality.md) - Validación de coherencia narrativa
- [research.md](research.md) - Fuentes para contexto emocional y cultural verificable