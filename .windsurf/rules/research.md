---
trigger: always_on
---

# Estándares de investigación y fuentes

## Objetivo
Establecer metodología rigurosa de investigación y documentación de fuentes bibliográficas verificables, asegurando que todo contenido histórico esté respaldado por fuentes académicas o primarias confiables antes de iniciar la redacción.

## Entradas requeridas
- Nombre del personaje seleccionado desde `colecciones/`.
- Acceso a fuentes bibliográficas online verificables (primarias, secundarias, terciarias).
- Conocimiento del periodo histórico y contexto del personaje.

## Pasos automáticos
1. Crear archivo `esquemas/X - fuentes.md` antes de comenzar redacción.
2. Compilar mínimo 2-3 fuentes verificables por capítulo planificado.
3. Clasificar fuentes en categorías:
   - **Primarias**: documentos originales, discursos, cartas, testimonios directos.
   - **Secundarias**: biografías académicas, estudios históricos, análisis especializados.
   - **Terciarias**: enciclopedias, artículos divulgativos, resúmenes generales.
4. Formatear cada fuente según estándar académico (APA o Chicago).
5. Incluir dominio completo o URL para fuentes online.
6. Verificar que todas las URLs sean accesibles (código 200, contenido relevante).

## Validaciones/Logs
- **Archivo de fuentes**: Debe existir `esquemas/X - fuentes.md` antes de iniciar redacción.
- **Cantidad mínima**: Al menos 2-3 fuentes por capítulo (40-60 fuentes para 20 capítulos).
- **Formato académico**: Consistencia en formato de citación (APA o Chicago).
- **URLs verificables**: Todas las fuentes online deben:
  - Devolver código HTTP 200 (no 404, 403, 500).
  - Contener contenido relevante al tema prometido.
  - No redirigir a páginas genéricas o no relacionadas.
- **Uso durante redacción**: Todas las afirmaciones históricas relevantes deben rastrearse a fuentes listadas.
- **No invención**: Cero datos inventados o no verificables.
- **No citas textuales**: Siempre narración propia, sin comillas ni citas directas.

## Fallbacks/Escalada
- Si no se encuentran suficientes fuentes para un capítulo: buscar fuentes alternativas o ajustar extensión del capítulo en el plan.
- Si una URL no es accesible: reemplazar con fuente alternativa verificable o usar fuente física con referencia completa.
- Si las fuentes son insuficientes para cubrir un periodo: documentarlo en el plan y ajustar expectativas de profundidad para ese capítulo.

## Relacionados
- [fuentes-rules.md](fuentes-rules.md) - Reglas específicas de verificación de fuentes
- [workflow.md](workflow.md) - Integración de fuentes en el flujo de trabajo
- [quality.md](quality.md) - Validación de rigor histórico

## Formato de ejemplo
```
Pérez, Juan. *Historia contemporánea*. Editorial Alfa, 2019.
Smith, John. *Biography of Lincoln*. Oxford Press, 2005.
https://www.britannica.com/topic/Simón-Bolívar
```
