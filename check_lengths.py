import os
import sys
import csv

def count_words(text):
    return len(text.split())

def main():
    if len(sys.argv) < 2:
        print("Uso: python check_lengths.py <personaje>")
        sys.exit(1)

    personaje = sys.argv[1]
    base_dir = os.path.join("bios", personaje)
    control_dir = os.path.join(base_dir, "control")
    csv_file = os.path.join(control_dir, "longitudes.csv")

    if not os.path.exists(csv_file):
        print(f"❌ No se encontró {csv_file}. Debe generarse en la planeación.")
        sys.exit(1)

    # Leer CSV existente
    rows = []
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    # Recalcular longitudes reales
    for row in rows:
        seccion = row["seccion"]
        file_path = os.path.join(base_dir, f"{seccion}.md")

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            real = count_words(text)
            esperado = int(row["longitud_esperada"])
            porcentaje = round((real / esperado) * 100, 2) if esperado > 0 else 0
        else:
            real = 0
            porcentaje = 0

        row["longitud_real"] = str(real)
        row["porcentaje"] = str(porcentaje)

    # Guardar CSV actualizado
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["seccion","longitud_esperada","longitud_real","porcentaje"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Archivo actualizado: {csv_file}")

if __name__ == "__main__":
    main()
