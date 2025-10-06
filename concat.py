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
    outfile = os.path.join(base_dir, f"{file_safe_name}.md")
    
    # Files in fixed order
    files = [
        "prologo.md",
        "introduccion.md",
        "cronologia.md",
        "capitulo-01.md", "capitulo-02.md", "capitulo-03.md", "capitulo-04.md", "capitulo-05.md",
        "capitulo-06.md", "capitulo-07.md", "capitulo-08.md", "capitulo-09.md", "capitulo-10.md",
        "capitulo-11.md", "capitulo-12.md", "capitulo-13.md", "capitulo-14.md", "capitulo-15.md",
        "epilogo.md",
        "glosario.md",
        "dramatis-personae.md",
        "fuentes.md"
    ]
    
    # Concatenate files
    content_parts = []
    for file in files:
        file_path = os.path.join(base_dir, file)
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
