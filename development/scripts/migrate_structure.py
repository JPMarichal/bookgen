#!/usr/bin/env python3
"""
Migration script to reorganize character directory structure.

This script consolidates all character information into a unified structure:
- research/ - Research materials (from esquemas/)
- chapters/ - Chapter files
- sections/ - Special sections (prologo, epilogo, etc.)
- output/ - Generated files
  - markdown/ - Concatenated markdown
  - word/ - Word documents
  - kdp/ - KDP assets
- control/ - Quality control (preserved)
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple


def validate_directory_exists(path: str) -> bool:
    """Validate that a directory exists."""
    return os.path.exists(path) and os.path.isdir(path)


def create_new_structure(character_path: Path) -> None:
    """Create the new directory structure for a character."""
    print(f"  Creating new directory structure in {character_path}...")
    
    # Create subdirectories
    subdirs = [
        "research",
        "chapters",
        "sections",
        "output/markdown",
        "output/word",
        "output/kdp"
    ]
    
    for subdir in subdirs:
        dir_path = character_path / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"    ✓ Created {subdir}/")


def move_chapters(character_path: Path) -> List[str]:
    """Move chapter files to chapters/ subdirectory."""
    print(f"  Moving chapter files...")
    moved_files = []
    
    # Find all chapter files in the root
    for i in range(1, 21):
        chapter_file = f"capitulo-{i:02d}.md"
        src = character_path / chapter_file
        if src.exists():
            dst = character_path / "chapters" / chapter_file
            shutil.move(str(src), str(dst))
            moved_files.append(chapter_file)
            print(f"    ✓ Moved {chapter_file} → chapters/")
    
    return moved_files


def move_sections(character_path: Path) -> List[str]:
    """Move section files to sections/ subdirectory."""
    print(f"  Moving section files...")
    moved_files = []
    
    # Section files to move
    section_files = [
        "prologo.md",
        "introduccion.md",
        "cronologia.md",
        "epilogo.md",
        "glosario.md",
        "dramatis-personae.md",
        "fuentes.md"
    ]
    
    for section_file in section_files:
        src = character_path / section_file
        if src.exists():
            dst = character_path / "sections" / section_file
            shutil.move(str(src), str(dst))
            moved_files.append(section_file)
            print(f"    ✓ Moved {section_file} → sections/")
    
    return moved_files


def move_output_markdown(character_path: Path, character_name: str) -> List[str]:
    """Move concatenated markdown to output/markdown/ subdirectory."""
    print(f"  Moving output markdown files...")
    moved_files = []
    
    # Find La biografia de *.md file
    pattern = "La biografia de *.md"
    for md_file in character_path.glob(pattern):
        if md_file.is_file():
            dst = character_path / "output" / "markdown" / md_file.name
            shutil.move(str(md_file), str(dst))
            moved_files.append(md_file.name)
            print(f"    ✓ Moved {md_file.name} → output/markdown/")
    
    return moved_files


def move_kdp_assets(character_path: Path) -> bool:
    """Move KDP directory to output/kdp/."""
    print(f"  Moving KDP assets...")
    
    src_kdp = character_path / "kdp"
    if src_kdp.exists() and src_kdp.is_dir():
        dst_kdp = character_path / "output" / "kdp"
        
        # Move all files from kdp/ to output/kdp/
        for item in src_kdp.iterdir():
            dst_item = dst_kdp / item.name
            shutil.move(str(item), str(dst_item))
            print(f"    ✓ Moved kdp/{item.name} → output/kdp/")
        
        # Remove empty kdp directory
        src_kdp.rmdir()
        print(f"    ✓ Removed empty kdp/ directory")
        return True
    
    return False


def move_docx_files(base_path: Path, character_name: str, character_path: Path) -> List[str]:
    """Move Word files from docx/ to output/word/."""
    print(f"  Moving Word files...")
    moved_files = []
    
    docx_dir = base_path / "docx" / character_name
    if docx_dir.exists() and docx_dir.is_dir():
        dst_word = character_path / "output" / "word"
        
        # Move all docx files
        for docx_file in docx_dir.glob("*.docx"):
            dst_file = dst_word / docx_file.name
            shutil.move(str(docx_file), str(dst_file))
            moved_files.append(docx_file.name)
            print(f"    ✓ Moved docx/{character_name}/{docx_file.name} → output/word/")
        
        # Remove character directory from docx/
        if not any(docx_dir.iterdir()):
            docx_dir.rmdir()
            print(f"    ✓ Removed empty docx/{character_name}/ directory")
    
    return moved_files


def move_research_files(base_path: Path, character_name: str, character_path: Path) -> List[str]:
    """Move research files from esquemas/ to research/."""
    print(f"  Moving research files...")
    moved_files = []
    
    esquemas_dir = base_path / "esquemas"
    if esquemas_dir.exists():
        # Look for files matching pattern: {character_name} - *.md
        for esquema_file in esquemas_dir.glob(f"{character_name} - *.md"):
            # Determine destination filename
            if "fuentes" in esquema_file.name.lower():
                dst_name = "fuentes.md"
            elif "plan de trabajo" in esquema_file.name.lower():
                dst_name = "plan-de-trabajo.md"
            else:
                # Keep original name
                dst_name = esquema_file.name.replace(f"{character_name} - ", "")
            
            dst = character_path / "research" / dst_name
            shutil.move(str(esquema_file), str(dst))
            moved_files.append(esquema_file.name)
            print(f"    ✓ Moved esquemas/{esquema_file.name} → research/{dst_name}")
    
    return moved_files


def migrate_character(base_path: Path, character_name: str) -> Tuple[bool, dict]:
    """
    Migrate a single character's files to new structure.
    
    Args:
        base_path: Base path of the repository
        character_name: Normalized character name
        
    Returns:
        Tuple of (success, stats_dict)
    """
    print(f"\n{'='*60}")
    print(f"Migrating: {character_name}")
    print(f"{'='*60}")
    
    character_path = base_path / "bios" / character_name
    
    if not character_path.exists():
        print(f"  ⚠️  Character directory not found: {character_path}")
        return False, {}
    
    stats = {
        'character': character_name,
        'chapters_moved': [],
        'sections_moved': [],
        'output_moved': [],
        'kdp_moved': False,
        'docx_moved': [],
        'research_moved': []
    }
    
    try:
        # Create new structure
        create_new_structure(character_path)
        
        # Move files
        stats['chapters_moved'] = move_chapters(character_path)
        stats['sections_moved'] = move_sections(character_path)
        stats['output_moved'] = move_output_markdown(character_path, character_name)
        stats['kdp_moved'] = move_kdp_assets(character_path)
        stats['docx_moved'] = move_docx_files(base_path, character_name, character_path)
        stats['research_moved'] = move_research_files(base_path, character_name, character_path)
        
        print(f"\n✅ Migration complete for {character_name}")
        return True, stats
        
    except Exception as e:
        print(f"\n❌ Error migrating {character_name}: {e}")
        import traceback
        traceback.print_exc()
        return False, stats


def cleanup_empty_directories(base_path: Path) -> None:
    """Remove empty directories after migration."""
    print(f"\n{'='*60}")
    print(f"Cleaning up empty directories")
    print(f"{'='*60}")
    
    # Remove esquemas/ if empty
    esquemas_dir = base_path / "esquemas"
    if esquemas_dir.exists() and not any(esquemas_dir.iterdir()):
        esquemas_dir.rmdir()
        print(f"  ✓ Removed empty esquemas/ directory")
    
    # Remove docx/ if empty
    docx_dir = base_path / "docx"
    if docx_dir.exists() and not any(docx_dir.iterdir()):
        docx_dir.rmdir()
        print(f"  ✓ Removed empty docx/ directory")


def validate_migration(base_path: Path, character_name: str) -> bool:
    """Validate that migration was successful."""
    character_path = base_path / "bios" / character_name
    
    # Check that new directories exist
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
            print(f"  ⚠️  Missing directory: {required_dir}")
            return False
    
    # Check that old structure files are gone
    old_files = list(character_path.glob("capitulo-*.md"))
    if old_files:
        print(f"  ⚠️  Found {len(old_files)} chapter files still in root")
        return False
    
    return True


def print_summary(all_stats: List[dict]) -> None:
    """Print migration summary."""
    print(f"\n{'='*60}")
    print(f"MIGRATION SUMMARY")
    print(f"{'='*60}")
    
    for stats in all_stats:
        char = stats['character']
        print(f"\n{char}:")
        print(f"  Chapters moved: {len(stats['chapters_moved'])}")
        print(f"  Sections moved: {len(stats['sections_moved'])}")
        print(f"  Output files moved: {len(stats['output_moved'])}")
        print(f"  KDP assets moved: {'Yes' if stats['kdp_moved'] else 'No'}")
        print(f"  Word files moved: {len(stats['docx_moved'])}")
        print(f"  Research files moved: {len(stats['research_moved'])}")


def main():
    """Main migration entry point."""
    print("=" * 60)
    print("DIRECTORY STRUCTURE MIGRATION")
    print("Consolidating character information into unified structure")
    print("=" * 60)
    
    # Get base path
    base_path = Path(__file__).parent.parent.resolve()
    print(f"\nBase path: {base_path}")
    
    # Characters to migrate
    characters = ['harry_s_truman', 'joseph_stalin', 'winston_churchill']
    
    # Migrate each character
    all_stats = []
    success_count = 0
    
    for character in characters:
        success, stats = migrate_character(base_path, character)
        if success:
            success_count += 1
            all_stats.append(stats)
            
            # Validate migration
            if validate_migration(base_path, character):
                print(f"  ✓ Validation passed for {character}")
            else:
                print(f"  ⚠️  Validation failed for {character}")
    
    # Cleanup
    cleanup_empty_directories(base_path)
    
    # Print summary
    print_summary(all_stats)
    
    # Final result
    print(f"\n{'='*60}")
    print(f"FINAL RESULT")
    print(f"{'='*60}")
    print(f"Successfully migrated: {success_count}/{len(characters)} characters")
    
    if success_count == len(characters):
        print("\n✅ All migrations completed successfully!")
        return 0
    else:
        print(f"\n⚠️  {len(characters) - success_count} migrations failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
