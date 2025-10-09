import os
import sys
import re
import unicodedata
import argparse


def remove_diacritics(text):
    """Remove diacritics from text"""
    normalized = unicodedata.normalize('NFD', text)
    without_diacritics = ''.join(
        char for char in normalized
        if unicodedata.category(char) != 'Mn'
    )
    return unicodedata.normalize('NFC', without_diacritics)


def normalize_name(name):
    """Normalize name to lowercase with underscores"""
    normalized = re.sub(r'[^\w\s]', '', name, flags=re.UNICODE)
    normalized = re.sub(r'\s+', '_', normalized.lower())
    return normalized.strip('_')


def find_first_uncompleted(lines):
    """Find first personaje without ✅"""
    for i, line in enumerate(lines):
        if '✅' not in line:
            line_original = line.strip()
            match = re.match(r'^(?P<num>\d+\.\s+)?(?P<nombre>[^✅]+?)\s*(✅)?$', line_original)
            if match:
                numero = match.group('num') or ''
                nombre = match.group('nombre').strip()
                if nombre:
                    return i, numero, nombre
    return None, None, None


def mark_personaje(coleccion_path, personaje):
    """Mark personaje with ✅ in collection file"""
    with open(coleccion_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    encontrado = False
    for i, line in enumerate(lines):
        match = re.match(r'^(?P<num>\d+\.\s+)?(?P<nombre>[^✅]+?)(\s*✅)?$', line)
        if match:
            numero = match.group('num') or ''
            nombre = match.group('nombre').strip()
            
            if nombre == personaje:
                if '✅' not in lines[i]:
                    lines[i] = f"{numero}{nombre} ✅\n".strip() + '\n'
                    with open(coleccion_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                encontrado = True
                break
    
    if not encontrado:
        print(f"⚠️  Personaje no encontrado en la colección: {personaje}")
    
    return encontrado


def concatenate_files(personaje, coleccion_path):
    """Main concatenation logic"""
    # Normalize personaje name
    personaje_norm = normalize_name(personaje)
    
    # Check directory exists
    base_dir = os.path.join("bios", personaje_norm)
    if not os.path.exists(base_dir):
        print(f"⚠️  Directorio no encontrado: {base_dir}")
        sys.exit(1)
    
    # Create output filename
    file_safe_name = remove_diacritics(f"La biografia de {personaje}").replace('  ', ' ').strip()
    # Output goes to output/markdown/ subdirectory
    output_dir = os.path.join(base_dir, "output", "markdown")
    os.makedirs(output_dir, exist_ok=True)
    outfile = os.path.join(output_dir, f"{file_safe_name}.md")
    
    # Files in fixed order - now from subdirectories
    sections_dir = os.path.join(base_dir, "sections")
    chapters_dir = os.path.join(base_dir, "chapters")
    
    files = [
        # Sections
        (sections_dir, "prologo.md"),
        (sections_dir, "introduccion.md"),
        (sections_dir, "cronologia.md"),
        # Chapters
        (chapters_dir, "capitulo-01.md"), (chapters_dir, "capitulo-02.md"),
        (chapters_dir, "capitulo-03.md"), (chapters_dir, "capitulo-04.md"),
        (chapters_dir, "capitulo-05.md"), (chapters_dir, "capitulo-06.md"),
        (chapters_dir, "capitulo-07.md"), (chapters_dir, "capitulo-08.md"),
        (chapters_dir, "capitulo-09.md"), (chapters_dir, "capitulo-10.md"),
        (chapters_dir, "capitulo-11.md"), (chapters_dir, "capitulo-12.md"),
        (chapters_dir, "capitulo-13.md"), (chapters_dir, "capitulo-14.md"),
        (chapters_dir, "capitulo-15.md"), (chapters_dir, "capitulo-16.md"),
        (chapters_dir, "capitulo-17.md"), (chapters_dir, "capitulo-18.md"),
        (chapters_dir, "capitulo-19.md"), (chapters_dir, "capitulo-20.md"),
        # More sections
        (sections_dir, "epilogo.md"),
        (sections_dir, "glosario.md"),
        (sections_dir, "dramatis-personae.md"),
        (sections_dir, "fuentes.md")
    ]
    
    # Concatenate files
    content_parts = []
    for subdir, file in files:
        file_path = os.path.join(subdir, file)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                contenido = f.read()
            content_parts.append(contenido)
            content_parts.append('\n')
        else:
            print(f"⚠️  Archivo faltante: {file}")
    
    # Write output file
    final_content = '\n'.join(content_parts)
    with open(outfile, 'w', encoding='utf-8', newline='') as f:
        f.write(final_content)
    
    print(f"✅ Concatenación completa para: {personaje}")
    print(f"📄 Archivo final: {outfile}")
    
    # Mark personaje as completed
    mark_personaje(coleccion_path, personaje)


def main():
    parser = argparse.ArgumentParser(description='Concatenar archivos de biografía')
    parser.add_argument('-coleccion', default='colecciones/personajes_guerra_fria.md',
                        help='Ruta al archivo de colección')
    parser.add_argument('-personaje', help='Nombre del personaje a procesar')
    
    args = parser.parse_args()
    
    coleccion = args.coleccion
    personaje = args.personaje
    
    # Check collection exists
    if not os.path.exists(coleccion):
        print(f"⚠️  Colección no encontrada: {coleccion}")
        sys.exit(1)
    
    # Read collection
    with open(coleccion, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Resolve personaje
    if not personaje:
        # Find first without ✅
        idx, numero, nombre = find_first_uncompleted(lines)
        if nombre:
            personaje = nombre
            # Mark with ✅
            lines[idx] = f"{numero}{nombre} ✅\n".strip() + '\n'
            with open(coleccion, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        else:
            print("No hay personajes pendientes en la colección.")
            sys.exit(0)
    else:
        # Clean personaje name
        personaje = personaje.strip()
    
    # Concatenate
    concatenate_files(personaje, coleccion)


if __name__ == "__main__":
    main()
