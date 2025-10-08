#!/usr/bin/env python
"""
Demo script for Word export functionality
Tests the Word exporter service with a sample biography
"""
import os
import sys
import tempfile
from pathlib import Path

from src.services.word_exporter import WordExporter
from src.config.export_config import ExportConfig
from src.api.models.export import DocumentMetadata
from datetime import datetime


def create_sample_biography(output_dir: str) -> str:
    """Create a sample biography markdown file"""
    biography_content = """
# Prólogo

Esta es la biografía de un personaje histórico importante.

# Introducción

Winston Churchill fue uno de los líderes más influyentes del siglo XX.

# Capítulo 1: Primeros Años

Winston Leonard Spencer Churchill nació el 30 de noviembre de 1874 en el Palacio de Blenheim.

# Capítulo 2: Carrera Política Temprana

Churchill comenzó su carrera política a principios del siglo XX.

# Capítulo 3: Primera Guerra Mundial

Durante la Primera Guerra Mundial, Churchill ocupó varios cargos importantes.

# Capítulo 4: Los Años de Entreguerras

Entre las dos guerras mundiales, Churchill continuó su carrera política.

# Capítulo 5: Segunda Guerra Mundial

El momento más importante de su vida llegó durante la Segunda Guerra Mundial.

# Epílogo

Churchill dejó un legado duradero en la historia mundial.

# Glosario

**PM**: Primer Ministro  
**WWII**: Segunda Guerra Mundial

# Fuentes

- Churchill, Winston S. "The Second World War"
- Gilbert, Martin. "Churchill: A Life"
"""
    
    bio_file = os.path.join(output_dir, "churchill", "La biografía de Churchill.md")
    os.makedirs(os.path.dirname(bio_file), exist_ok=True)
    
    with open(bio_file, 'w', encoding='utf-8') as f:
        f.write(biography_content)
    
    return bio_file


def main():
    """Main demo function"""
    print("=" * 60)
    print("Word Export Service Demo")
    print("=" * 60)
    print()
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Working directory: {tmpdir}")
        print()
        
        # Create sample biography
        print("1. Creating sample biography markdown...")
        bio_file = create_sample_biography(tmpdir)
        print(f"   ✓ Created: {bio_file}")
        print()
        
        # Check file size
        file_size = os.path.getsize(bio_file)
        print(f"   Biography size: {file_size} bytes")
        print()
        
        # Initialize exporter
        print("2. Initializing Word exporter...")
        
        # Configure output directory
        output_dir = os.path.join(tmpdir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        config = ExportConfig(
            output_directory=output_dir,
            word_template_path=os.path.join(
                os.path.dirname(__file__), 
                "wordTemplate", 
                "reference.docx"
            )
        )
        
        exporter = WordExporter(config)
        print("   ✓ Exporter initialized")
        print()
        
        # Validate environment
        print("3. Validating environment...")
        is_valid, issues = exporter.validate_environment()
        
        if is_valid:
            print("   ✓ Environment is valid")
        else:
            print("   ⚠ Environment has issues:")
            for issue in issues:
                print(f"     - {issue}")
        print()
        
        # Check Pandoc
        print("4. Checking Pandoc installation...")
        from src.utils.pandoc_wrapper import PandocWrapper
        pandoc = PandocWrapper()
        if pandoc.is_available():
            print(f"   ✓ Pandoc is available: {pandoc.get_version()}")
        else:
            print("   ✗ Pandoc is NOT available")
            print("   Please install Pandoc to use Word export")
            return
        print()
        
        # Prepare metadata
        print("5. Preparing document metadata...")
        metadata = DocumentMetadata(
            title="La biografía de Winston Churchill",
            author="BookGen Sistema Automatizado",
            subject="Biografía de Winston Churchill",
            description="Una biografía completa de Winston Churchill",
            keywords="Churchill, biografía, historia, Segunda Guerra Mundial",
            date=datetime.now().strftime("%Y-%m-%d")
        )
        print("   ✓ Metadata prepared")
        print()
        
        # Export to Word
        print("6. Exporting to Word with TOC...")
        try:
            result = exporter.export_to_word_with_toc(
                markdown_file=bio_file,
                toc_title="Contenido",
                toc_depth=1,
                metadata=metadata
            )
            
            if result.success:
                print(f"   ✓ Export successful!")
                print(f"   Output file: {result.output_file}")
                print(f"   File size: {result.file_size} bytes ({result.file_size_mb:.2f} MB)")
                print(f"   Has TOC: {result.has_toc}")
                print(f"   TOC entries: {result.toc_entries}")
                print(f"   Pandoc version: {result.pandoc_version}")
                print(f"   Template used: {result.template_used}")
                print()
                
                # Verify the file exists
                if os.path.exists(result.output_file):
                    print(f"   ✓ Output file verified: {result.output_file}")
                    actual_size = os.path.getsize(result.output_file)
                    print(f"   Actual file size: {actual_size} bytes")
                else:
                    print(f"   ✗ Output file not found: {result.output_file}")
                
            else:
                print(f"   ✗ Export failed: {result.error_message}")
                
        except Exception as e:
            print(f"   ✗ Error during export: {e}")
            import traceback
            traceback.print_exc()
        
        print()
        print("=" * 60)
        print("Demo complete!")
        print("=" * 60)


if __name__ == "__main__":
    main()
