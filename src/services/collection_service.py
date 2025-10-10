"""
Collection Service
Manages collection files and detects next character to process
"""
import os
import re
import logging
import unicodedata
from typing import Optional, Tuple, List
from pathlib import Path

logger = logging.getLogger(__name__)


class CollectionService:
    """Service for managing biography collections"""
    
    def __init__(self, collections_base_path: str = "colecciones"):
        """
        Initialize collection service
        
        Args:
            collections_base_path: Base path for collection files
        """
        self.collections_base_path = collections_base_path
        logger.info(f"CollectionService initialized with base path: {collections_base_path}")
    
    def find_first_uncompleted(self, collection_file: str) -> Tuple[Optional[int], Optional[str], Optional[str]]:
        """
        Find first character without completion mark (✅) in collection file
        
        Args:
            collection_file: Path to collection file (relative to collections_base_path)
            
        Returns:
            Tuple of (line_index, line_number, character_name) or (None, None, None) if all completed
        """
        collection_path = self._get_collection_path(collection_file)
        
        if not os.path.exists(collection_path):
            logger.error(f"Collection file not found: {collection_path}")
            raise FileNotFoundError(f"Collection file not found: {collection_file}")
        
        logger.info(f"Reading collection file: {collection_path}")
        
        with open(collection_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            # Skip lines that already have completion mark
            if '✅' in line:
                continue
            
            line_stripped = line.strip()
            
            # Try to match pattern: optional number + name
            # Examples: "1.1. Joseph Stalin" or "Dwight D. Eisenhower"
            match = re.match(r'^(?P<num>\d+\.?\d*\.\s+)?(?P<nombre>[^✅]+?)(\s*✅)?$', line_stripped)
            
            if match:
                numero = match.group('num') or ''
                nombre = match.group('nombre').strip()
                
                if nombre:
                    logger.info(f"Found uncompleted character at line {i}: {nombre}")
                    return i, numero, nombre
        
        logger.info("No uncompleted characters found in collection")
        return None, None, None
    
    def mark_as_completed(self, collection_file: str, character_name: str) -> bool:
        """
        Mark a character as completed (add ✅) in the collection file
        
        Args:
            collection_file: Path to collection file (relative to collections_base_path)
            character_name: Name of the character to mark
            
        Returns:
            True if character was found and marked, False otherwise
        """
        collection_path = self._get_collection_path(collection_file)
        
        if not os.path.exists(collection_path):
            logger.error(f"Collection file not found: {collection_path}")
            raise FileNotFoundError(f"Collection file not found: {collection_file}")
        
        logger.info(f"Marking character '{character_name}' as completed in {collection_path}")
        
        with open(collection_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        encontrado = False
        for i, line in enumerate(lines):
            # Match pattern with or without completion mark
            match = re.match(r'^(?P<num>\d+\.?\d*\.\s+)?(?P<nombre>[^✅]+?)(\s*✅)?$', line.strip())
            
            if match:
                nombre = match.group('nombre').strip()
                
                # Check if this is the character we're looking for
                if nombre.lower() == character_name.lower():
                    # Add completion mark if not already present
                    if '✅' not in line:
                        lines[i] = line.rstrip() + ' ✅\n'
                        encontrado = True
                        logger.info(f"Marked character '{character_name}' as completed")
                    break
        
        if encontrado:
            # Write back to file
            with open(collection_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        else:
            logger.warning(f"Character '{character_name}' not found in collection")
        
        return encontrado
    
    def list_collections(self) -> List[str]:
        """
        List all available collection files
        
        Returns:
            List of collection file names
        """
        if not os.path.exists(self.collections_base_path):
            logger.warning(f"Collections directory not found: {self.collections_base_path}")
            return []
        
        collections = []
        for file in os.listdir(self.collections_base_path):
            if file.endswith('.md'):
                collections.append(file)
        
        logger.info(f"Found {len(collections)} collection files")
        return sorted(collections)
    
    def get_collection_stats(self, collection_file: str) -> dict:
        """
        Get statistics about a collection file
        
        Args:
            collection_file: Path to collection file
            
        Returns:
            Dictionary with statistics
        """
        collection_path = self._get_collection_path(collection_file)
        
        if not os.path.exists(collection_path):
            raise FileNotFoundError(f"Collection file not found: {collection_file}")
        
        with open(collection_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total = 0
        completed = 0
        
        for line in lines:
            line_stripped = line.strip()
            match = re.match(r'^(?P<num>\d+\.?\d*\.\s+)?(?P<nombre>[^✅]+?)(\s*✅)?$', line_stripped)
            
            if match:
                nombre = match.group('nombre').strip()
                if nombre:
                    total += 1
                    if '✅' in line:
                        completed += 1
        
        return {
            'collection_file': collection_file,
            'total_characters': total,
            'completed': completed,
            'remaining': total - completed,
            'completion_percentage': round((completed / total * 100) if total > 0 else 0, 2)
        }
    
    @staticmethod
    def normalize_character_name(name: str) -> str:
        """
        Normalize character name for use as identifier
        
        Args:
            name: Character name
            
        Returns:
            Normalized name (lowercase with underscores)
        """
        # Remove special characters and diacritics
        normalized = re.sub(r'[^\w\s]', '', name, flags=re.UNICODE)
        # Replace spaces with underscores
        normalized = re.sub(r'\s+', '_', normalized.lower())
        return normalized.strip('_')
    
    def _get_collection_path(self, collection_file: str) -> str:
        """
        Get full path to collection file
        
        Args:
            collection_file: Collection file name
            
        Returns:
            Full path to collection file
        """
        # If already absolute path, return as-is
        if os.path.isabs(collection_file):
            return collection_file
        
        # Otherwise, join with base path
        return os.path.join(self.collections_base_path, collection_file)
