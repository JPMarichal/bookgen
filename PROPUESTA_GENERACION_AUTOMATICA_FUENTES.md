# Propuesta: Sistema Automático de Generación de Fuentes

## Problema Identificado

El sistema actual requiere que los usuarios proporcionen manualmente 40-60 URLs de fuentes, cuando las reglas originales establecían que el sistema debía generar automáticamente estas fuentes usando IA.

## Solución Propuesta: Sistema Híbrido Inteligente

### Fase 1: Generación Automática con IA
```python
class AutomaticSourceGenerator:
    """Generador automático de fuentes usando múltiples estrategias de IA"""
    
    def __init__(self):
        self.openrouter_client = OpenRouterClient()
        self.source_validator = SourceValidationService()
        self.search_strategies = [
            WikipediaStrategy(),
            AcademicDatabaseStrategy(), 
            GovernmentArchiveStrategy(),
            BiographyWebsiteStrategy(),
            NewsArchiveStrategy()
        ]
    
    def generate_sources_for_character(self, character_name: str) -> List[SourceItem]:
        """
        Genera automáticamente fuentes de alta calidad para un personaje
        
        Args:
            character_name: Nombre del personaje histórico
            
        Returns:
            Lista de fuentes validadas y de alta calidad
        """
        
        # 1. Análisis inicial del personaje con IA
        character_analysis = self._analyze_character_with_ai(character_name)
        
        # 2. Generación de estrategias de búsqueda
        search_queries = self._generate_search_strategies(character_analysis)
        
        # 3. Búsqueda automática usando múltiples estrategias
        candidate_sources = []
        for strategy in self.search_strategies:
            sources = strategy.search(character_name, search_queries)
            candidate_sources.extend(sources)
        
        # 4. Validación y filtrado automático
        validated_sources = self._validate_and_filter(candidate_sources, character_name)
        
        # 5. Garantizar diversidad y calidad
        final_sources = self._ensure_quality_distribution(validated_sources)
        
        return final_sources
```

### Componentes del Sistema

#### 1. Estrategias de Búsqueda Inteligente

```python
class WikipediaStrategy(SourceStrategy):
    """Estrategia para fuentes de Wikipedia en múltiples idiomas"""
    
    def search(self, character: str, context: CharacterAnalysis) -> List[SourceItem]:
        # Buscar en Wikipedia principal + páginas relacionadas
        # Ejemplo: Einstein -> Teoría de la Relatividad, Nobel, etc.
        pass

class AcademicDatabaseStrategy(SourceStrategy):
    """Búsqueda en bases de datos académicas"""
    
    def search(self, character: str, context: CharacterAnalysis) -> List[SourceItem]:
        # Buscar en:
        # - Archive.org (academic papers)
        # - Google Scholar (si disponible vía API)
        # - Jstor (contenido abierto)
        # - Project Gutenberg (textos históricos)
        pass

class GovernmentArchiveStrategy(SourceStrategy):
    """Archivos gubernamentales y oficiales"""
    
    def search(self, character: str, context: CharacterAnalysis) -> List[SourceItem]:
        # - Biblioteca del Congreso (loc.gov)
        # - Archivos nacionales (.gov)
        # - UNESCO, etc.
        pass

class BiographyWebsiteStrategy(SourceStrategy):
    """Sitios especializados en biografías"""
    
    def search(self, character: str, context: CharacterAnalysis) -> List[SourceItem]:
        # - Britannica
        # - Biography.com
        # - Nobel Prize (si aplica)
        # - History.com
        pass
```

#### 2. Análisis IA del Personaje

```python
def _analyze_character_with_ai(self, character_name: str) -> CharacterAnalysis:
    """
    Usa IA para analizar el personaje y generar estrategias de búsqueda
    """
    
    prompt = f"""
    Analiza el personaje histórico "{character_name}" y proporciona:
    
    1. Periodo histórico (siglo, años clave)
    2. Nacionalidad y lugares relevantes  
    3. Campo profesional (ciencia, política, arte, etc.)
    4. Eventos y logros más importantes
    5. Personas y conceptos relacionados
    6. Fuentes primarias probables (cartas, discursos, documentos)
    7. Instituciones relevantes (universidades, gobiernos, organizaciones)
    8. Términos de búsqueda óptimos en inglés y español
    
    Formato JSON para procesamiento automático.
    """
    
    response = self.openrouter_client.complete(prompt)
    return CharacterAnalysis.from_json(response)
```

#### 3. Validación Automática Multi-Nivel

```python
def _validate_and_filter(self, candidates: List[SourceItem], character: str) -> List[SourceItem]:
    """
    Validación automática en múltiples niveles
    """
    
    validated = []
    
    for source in candidates:
        # Nivel 1: Validación técnica básica
        basic_result = self.source_validator.validate_single_source(
            source, character, check_accessibility=True
        )
        
        if not basic_result.is_valid:
            continue
            
        # Nivel 2: Análisis de contenido con IA
        content_quality = self._analyze_content_quality_with_ai(source, character)
        
        if content_quality.relevance_score >= 0.7:
            # Nivel 3: Verificación de credibilidad del dominio
            credibility = self._assess_domain_credibility(source.url)
            
            if credibility >= 0.8:
                validated.append(source)
    
    return validated
```

#### 4. Garantía de Calidad y Diversidad

```python
def _ensure_quality_distribution(self, sources: List[SourceItem]) -> List[SourceItem]:
    """
    Garantiza diversidad de tipos de fuente y alta calidad
    """
    
    # Clasificar por tipo y calidad
    categorized = {
        'primary': [],      # Documentos originales, cartas, discursos
        'secondary': [],    # Biografías académicas, estudios
        'tertiary': []      # Enciclopedias, artículos generales
    }
    
    # Distribuir según las reglas originales (2-3 fuentes por capítulo)
    target_distribution = {
        'primary': min(15, len([s for s in sources if s.source_type == 'primary'])),
        'secondary': min(25, len([s for s in sources if s.source_type == 'secondary'])), 
        'tertiary': min(20, len([s for s in sources if s.source_type == 'tertiary']))
    }
    
    # Seleccionar las mejores de cada categoría
    final_sources = []
    for category, target_count in target_distribution.items():
        category_sources = sorted(
            categorized[category], 
            key=lambda x: x.relevance_score, 
            reverse=True
        )[:target_count]
        final_sources.extend(category_sources)
    
    return final_sources
```

### Integración en el API Existente

```python
# Nuevo endpoint en src/api/routers/sources.py

@router.post(
    "/generate-automatic",
    response_model=AutomaticSourceGenerationResponse,
    status_code=status.HTTP_200_OK
)
async def generate_sources_automatically(request: AutomaticSourceGenerationRequest):
    """
    Genera automáticamente fuentes de alta calidad para un personaje
    
    Este endpoint implementa la funcionalidad original de las reglas:
    - Generación automática con IA
    - Validación multi-nivel
    - Garantía de calidad y diversidad
    """
    
    generator = AutomaticSourceGenerator()
    
    # Generar fuentes automáticamente
    sources = generator.generate_sources_for_character(request.character_name)
    
    # Validar resultado final
    validation_result = generator.source_validator.validate_sources(
        biography_topic=request.character_name,
        sources_list=sources,
        check_accessibility=True
    )
    
    # Generar archivo de fuentes académicas
    sources_file_content = generator._format_academic_sources(sources)
    
    return AutomaticSourceGenerationResponse(
        character=request.character_name,
        total_generated=len(sources),
        sources=sources,
        validation_summary=validation_result,
        academic_format=sources_file_content,
        quality_score=validation_result['average_relevance'],
        recommendations=validation_result['recommendations']
    )
```

### Flujo de Usuario Mejorado

```bash
# Opción 1: Generación completamente automática (reglas originales)
curl -X POST http://localhost:8000/api/v1/sources/generate-automatic \
  -H "Content-Type: application/json" \
  -d '{"character_name": "Albert Einstein"}'

# Opción 2: Híbrido - empezar automático, después ajustar manualmente  
curl -X POST http://localhost:8000/api/v1/sources/generate-automatic \
  -H "Content-Type: application/json" \
  -d '{
    "character_name": "Albert Einstein",
    "allow_manual_additions": true,
    "min_sources": 45
  }'

# Opción 3: Manual (como está actualmente)
curl -X POST http://localhost:8000/api/v1/biographies \
  -H "Content-Type: application/json" \
  -d '{
    "character": "Albert Einstein", 
    "sources": [...]
  }'
```

## Beneficios del Sistema Híbrido

### ✅ Recupera la Automatización Original
- El sistema puede generar fuentes completamente automático
- Cumple con las reglas originales de `.windsurf`
- Reduce la carga del usuario

### ✅ Mantiene Alta Calidad  
- Validación multi-nivel con IA
- Garantiza diversidad de tipos de fuente
- Análisis de credibilidad automático

### ✅ Flexibilidad para el Usuario
- Modo completamente automático
- Modo híbrido (automático + ajustes manuales)
- Modo manual (actual) sigue disponible

### ✅ Mejora Continua
- El sistema aprende de validaciones exitosas
- Actualiza estrategias de búsqueda
- Mejora la detección de fuentes de calidad

## Implementación Gradual Sugerida

### Fase 1: Generador Básico (1-2 semanas)
- Implementar WikipediaStrategy y AcademicDatabaseStrategy
- Validación básica automática
- Endpoint `/generate-automatic`

### Fase 2: Análisis IA Avanzado (2-3 semanas)  
- Integración completa con OpenRouter para análisis
- Estrategias de búsqueda más sofisticadas
- Análisis de contenido con IA

### Fase 3: Optimización y Aprendizaje (1-2 semanas)
- Sistema de feedback para mejora continua
- Métricas de calidad automáticas
- Optimización de estrategias de búsqueda

## Conclusión

Esta propuesta recupera la responsabilidad original del sistema de generar fuentes automáticamente, pero lo hace de manera inteligente y con múltiples capas de validación para garantizar la calidad que el sistema actual ha logrado.

El usuario puede elegir el nivel de automatización que prefiere, desde completamente automático hasta manual, manteniendo siempre los estándares de calidad.