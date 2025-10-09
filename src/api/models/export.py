"""
Data models for Word export service
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class DocumentMetadata:
    """Metadata for exported Word document"""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[str] = None
    date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Convert metadata to dictionary for Pandoc"""
        metadata = {}
        if self.title:
            metadata['title'] = self.title
        if self.author:
            metadata['author'] = self.author
        if self.subject:
            metadata['subject'] = self.subject
        if self.description:
            metadata['description'] = self.description
        if self.keywords:
            metadata['keywords'] = self.keywords
        if self.date:
            metadata['date'] = self.date
        return metadata


@dataclass
class DocumentInfo:
    """Information about an exported Word document"""
    has_toc: bool
    toc_entries: int
    metadata: Dict[str, Any]
    file_size: int
    page_count: Optional[int] = None
    
    @classmethod
    def from_file(cls, file_path: str, has_toc: bool = False, toc_entries: int = 0) -> "DocumentInfo":
        """
        Create DocumentInfo from a Word file
        
        Args:
            file_path: Path to the Word document
            has_toc: Whether document has TOC (default from export result)
            toc_entries: Number of TOC entries (default from export result)
            
        Returns:
            DocumentInfo instance
        """
        import os
        
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        # Try to extract metadata from the document
        metadata = {}
        try:
            from docx import Document
            doc = Document(file_path)
            core_props = doc.core_properties
            
            if core_props.title:
                metadata['title'] = core_props.title
            if core_props.author:
                metadata['author'] = core_props.author
            if core_props.subject:
                metadata['subject'] = core_props.subject
            if core_props.keywords:
                metadata['keywords'] = core_props.keywords
            if core_props.created:
                metadata['created'] = core_props.created.isoformat()
            if core_props.modified:
                metadata['modified'] = core_props.modified.isoformat()
        except ImportError:
            # python-docx not available
            pass
        except Exception:
            # If file can't be read, use empty metadata
            pass
        
        return cls(
            has_toc=has_toc,
            toc_entries=toc_entries,
            metadata=metadata,
            file_size=file_size
        )


@dataclass
class WordExportResult:
    """Result of Word document export operation"""
    success: bool
    output_file: str
    file_size: int
    has_toc: bool
    toc_entries: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    pandoc_version: Optional[str] = None
    template_used: Optional[str] = None
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)
    
    @property
    def is_valid(self) -> bool:
        """Check if export is valid (successful with file)"""
        return self.success and self.file_size > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'success': self.success,
            'output_file': self.output_file,
            'file_size': self.file_size,
            'file_size_mb': round(self.file_size_mb, 2),
            'has_toc': self.has_toc,
            'toc_entries': self.toc_entries,
            'metadata': self.metadata,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat(),
            'pandoc_version': self.pandoc_version,
            'template_used': self.template_used,
        }


@dataclass
class WordExportError(Exception):
    """Exception raised during Word export"""
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


@dataclass
class ZipExportResult:
    """Result of ZIP export operation for publication files"""
    success: bool
    zip_path: Optional[str] = None
    zip_size: Optional[int] = None
    included_files: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def zip_size_mb(self) -> float:
        """Get ZIP size in megabytes"""
        if self.zip_size is None:
            return 0.0
        return self.zip_size / (1024 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'success': self.success,
            'zip_path': self.zip_path,
            'zip_size': self.zip_size,
            'zip_size_mb': round(self.zip_size_mb, 2),
            'included_files': self.included_files,
            'file_count': len(self.included_files),
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat(),
        }
