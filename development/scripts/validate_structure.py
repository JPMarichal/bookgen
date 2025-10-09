#!/usr/bin/env python3
"""
Validation script to verify directory structure after migration.

This script checks that all character directories follow the new structure:
- research/ - Research materials
- chapters/ - Chapter files
- sections/ - Special sections
- output/ - Generated files
  - markdown/ - Concatenated markdown
  - word/ - Word documents
  - kdp/ - KDP assets
- control/ - Quality control (optional)
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple


def validate_character_structure(character_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate that a character directory has the correct structure.
    
    Args:
        character_path: Path to character directory
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Required directories
    required_dirs = [
        "research",
        "chapters",
        "sections",
        "output/markdown",
        "output/word",
        "output/kdp"
    ]
    
    for required_dir in required_dirs:
        dir_path = character_path / required_dir
        if not dir_path.exists():
            issues.append(f"Missing directory: {required_dir}")
    
    # Check that no chapter files exist in root
    for chapter_file in character_path.glob("capitulo-*.md"):
        if chapter_file.is_file():
            issues.append(f"Chapter file in root: {chapter_file.name}")
    
    # Check that no section files exist in root
    section_files = [
        "prologo.md", "introduccion.md", "cronologia.md",
        "epilogo.md", "glosario.md", "dramatis-personae.md", "fuentes.md"
    ]
    for section_file in section_files:
        if (character_path / section_file).exists():
            issues.append(f"Section file in root: {section_file}")
    
    # Check that old output file doesn't exist in root
    for md_file in character_path.glob("La biografia de *.md"):
        if md_file.is_file():
            issues.append(f"Output markdown in root: {md_file.name}")
    
    # Check for old kdp/ directory in root
    if (character_path / "kdp").exists():
        issues.append(f"Old kdp/ directory still exists in root")
    
    return len(issues) == 0, issues


def count_files(directory: Path, pattern: str = "*") -> int:
    """Count files matching pattern in directory."""
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def print_character_stats(character_name: str, character_path: Path) -> None:
    """Print statistics for a character directory."""
    print(f"\n{character_name}:")
    print(f"  Chapters: {count_files(character_path / 'chapters', '*.md')}")
    print(f"  Sections: {count_files(character_path / 'sections', '*.md')}")
    print(f"  Research files: {count_files(character_path / 'research', '*.md')}")
    print(f"  Output markdown: {count_files(character_path / 'output' / 'markdown', '*.md')}")
    print(f"  Output word: {count_files(character_path / 'output' / 'word', '*.docx')}")
    print(f"  KDP assets: {count_files(character_path / 'output' / 'kdp', '*')}")
    
    # Check for control directory
    if (character_path / 'control').exists():
        print(f"  Control files: {count_files(character_path / 'control', '*')}")


def main():
    """Main validation entry point."""
    print("=" * 60)
    print("DIRECTORY STRUCTURE VALIDATION")
    print("=" * 60)
    
    # Get base path
    base_path = Path(__file__).parent.parent.resolve()
    bios_path = base_path / "bios"
    
    if not bios_path.exists():
        print(f"❌ Bios directory not found: {bios_path}")
        return 1
    
    # Find all character directories
    character_dirs = [d for d in bios_path.iterdir() if d.is_dir()]
    
    if not character_dirs:
        print(f"❌ No character directories found in {bios_path}")
        return 1
    
    print(f"\nFound {len(character_dirs)} character directories")
    
    # Validate each character
    all_valid = True
    validation_results = []
    
    for character_dir in sorted(character_dirs):
        character_name = character_dir.name
        is_valid, issues = validate_character_structure(character_dir)
        
        validation_results.append({
            'character': character_name,
            'valid': is_valid,
            'issues': issues,
            'path': character_dir
        })
        
        if not is_valid:
            all_valid = False
    
    # Print validation results
    print(f"\n{'='*60}")
    print("VALIDATION RESULTS")
    print(f"{'='*60}")
    
    for result in validation_results:
        if result['valid']:
            print(f"\n✅ {result['character']}: VALID")
        else:
            print(f"\n❌ {result['character']}: INVALID")
            for issue in result['issues']:
                print(f"    - {issue}")
    
    # Print statistics
    print(f"\n{'='*60}")
    print("STATISTICS")
    print(f"{'='*60}")
    
    for result in validation_results:
        print_character_stats(result['character'], result['path'])
    
    # Check for obsolete directories
    print(f"\n{'='*60}")
    print("OBSOLETE DIRECTORIES CHECK")
    print(f"{'='*60}")
    
    obsolete_dirs = ['esquemas', 'docx']
    found_obsolete = False
    
    for obsolete_dir in obsolete_dirs:
        obsolete_path = base_path / obsolete_dir
        if obsolete_path.exists():
            print(f"  ⚠️  Found obsolete directory: {obsolete_dir}/")
            found_obsolete = True
    
    if not found_obsolete:
        print("  ✓ No obsolete directories found")
    
    # Final summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    valid_count = sum(1 for r in validation_results if r['valid'])
    print(f"Valid characters: {valid_count}/{len(validation_results)}")
    
    if all_valid and not found_obsolete:
        print("\n✅ All validations passed!")
        return 0
    else:
        print("\n⚠️  Some validations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
