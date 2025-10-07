"""
Data models for concatenation service
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class TransitionError:
    """Represents a transition error between chapters"""
    chapter_from: int
    chapter_to: int
    severity: str  # 'critical', 'warning', 'info'
    message: str
    suggestion: Optional[str] = None


@dataclass
class CoherenceIssue:
    """Represents a narrative coherence issue"""
    location: str  # e.g., "Chapter 5", "Epilogue"
    issue_type: str  # e.g., "timeline_conflict", "character_inconsistency"
    severity: str
    description: str
    context: Optional[str] = None


@dataclass
class ConcatenationMetrics:
    """Metrics from concatenation analysis"""
    total_words: int
    total_chapters: int
    files_processed: int
    missing_files: List[str] = field(default_factory=list)
    coherence_score: float = 0.0
    transition_quality: float = 0.0
    redundancy_ratio: float = 0.0
    vocabulary_richness: float = 0.0


@dataclass
class ConcatenationResult:
    """Result of biography concatenation"""
    character: str
    output_file: str
    success: bool
    metrics: ConcatenationMetrics
    coherence_score: float
    chronology_valid: bool
    transition_errors: List[TransitionError] = field(default_factory=list)
    coherence_issues: List[CoherenceIssue] = field(default_factory=list)
    redundancies_removed: int = 0
    index_generated: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_high_quality(self) -> bool:
        """Check if concatenation meets high quality standards"""
        return (
            self.coherence_score > 0.8 and
            len(self.transition_errors) == 0 and
            self.chronology_valid
        )


@dataclass
class ChapterContent:
    """Represents content of a single chapter"""
    number: Optional[int]  # None for non-chapter sections
    title: str
    content: str
    file_path: str
    word_count: int
    section_type: str  # 'prologue', 'chapter', 'epilogue', etc.


@dataclass  
class ConcatenationConfig:
    """Configuration for concatenation service"""
    base_path: str = "bios"
    output_filename_template: str = "La biografia de {character}.md"
    enable_transition_generation: bool = True
    enable_redundancy_detection: bool = True
    enable_chronology_validation: bool = True
    min_coherence_score: float = 0.8
    separator_between_sections: str = "\n\n"
    
    # File order configuration
    file_order: List[str] = field(default_factory=lambda: [
        "prologo.md",
        "introduccion.md",
        "cronologia.md",
        *[f"capitulo-{i:02d}.md" for i in range(1, 21)],
        "epilogo.md",
        "glosario.md",
        "dramatis-personae.md",
        "fuentes.md"
    ])
