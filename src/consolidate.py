"""
Script principal de consolidacion.
Lee todos los Excel del ZIP + archivos Excel sueltos en data/raw/ y genera CSVs.

Para agregar nuevos meses: copiar el Excel a data/raw/ y correr:
    python src/consolidate.py
"""

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import aif_parser
import imig_parser


def iter_sources(zip_path: Path, raw_dir: Path):
    """
    Genera (nombre, bytes) para cada archivo Excel a procesar.
    Fuentes:
      1. Todos los .xls/.xlsx dentro del ZIP
      2. Archivos .xls/.xlsx sueltos en raw_dir que NO esten en el ZIP
         (archivos nuevos agregados manualmente para completar meses faltantes)
    """
    # Nombres del ZIP
    zip_names = set()
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as z:
            zip_names = {n for n in z.namelist()
                         if n.lower().endswith((".xls", ".xlsx"))}

    # Archivos sueltos en raw_dir (excluye datos de referencia como IPC.xlsx)
    EXCLUIR = {"IPC.xlsx"}
    extra_files = {
        f.name: f
        for f in raw_dir.glob("*")
        if f.suffix.lower() in (".xls", ".xlsx")
        and f.name not in zip_names
        and f.name not in EXCLUIR
    }

    print(f"  ZIP : {len(zip_names)} archivos Excel")
    print(f"  Sueltos en data/raw/: {len(extra_files)} archivos adicionales")
    if extra_files:
        for n in sorted(extra_files):
            print(f"    + {n}")

    # Yield desde ZIP
    if zip_path.exists():
        with zipfile.ZipFile(zip_path, "r") as z:
            for name in sorted(zip_names):
                yield name, z.read(name)

    # Yield desde archivos sueltos
    for name, path in sorted(extra_files.items()):
        yield name, path.read_bytes()


def process(zip_path: Path, raw_dir: Path, output_dir: Path):
    print(f"\n[1/3] Leyendo fuentes de datos...")
    sources = list(iter_sources(zip_path, raw_dir))
    print(f"  Total: {len(sources)} archivos a procesar")

    print("\n[2/3] Parseando archivos...")
    all_aif, all_imig = [], []

    for name, data in sources:
        print(f"\n-> {name}")
        all_aif.extend(aif_parser.parse_file(name, data))
        all_imig.extend(imig_parser.parse_file(name, data))

    print("\n[3/3] Consolidando y guardando...")
    output_dir.mkdir(parents=True, exist_ok=True)

    if all_aif:
        df_aif = pd.DataFrame(all_aif)
        df_aif["fecha"] = pd.to_datetime(df_aif["fecha"], format="%Y-%m", errors="coerce")
        df_aif = df_aif.sort_values(["fecha", "periodo", "subsector", "concepto_codigo"])
        df_aif = df_aif.drop_duplicates(subset=["fecha", "periodo", "concepto_codigo", "subsector"])
        out = output_dir / "aif_consolidado.csv"
        df_aif.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"  AIF: {len(df_aif):,} registros -> {out}")
    else:
        print("  [WARN] Sin registros AIF")
        df_aif = None

    if all_imig:
        df_imig = pd.DataFrame(all_imig)
        df_imig["fecha"] = pd.to_datetime(df_imig["fecha"], format="%Y-%m", errors="coerce")
        df_imig = df_imig.sort_values(["fecha", "concepto_codigo"])
        df_imig = df_imig.drop_duplicates(subset=["fecha", "concepto_codigo", "fuente_archivo"])
        out = output_dir / "imig_consolidado.csv"
        df_imig.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"  IMIG: {len(df_imig):,} registros -> {out}")
    else:
        print("  [WARN] Sin registros IMIG")
        df_imig = None

    _print_summary(df_aif, df_imig)


def _print_summary(df_aif, df_imig):
    print("\n" + "=" * 60)
    print("RESUMEN DE COBERTURA")
    print("=" * 60)

    if df_aif is not None:
        mensual = df_aif[df_aif["periodo"] == "mensual"]
        print(f"\nAIF - Sector Publico Base Caja")
        print(f"  Rango : {df_aif['fecha'].min().strftime('%Y-%m')} - {df_aif['fecha'].max().strftime('%Y-%m')}")
        print(f"  Meses mensuales: {mensual['fecha'].nunique()}")
        print(f"  Conceptos unicos: {df_aif['concepto_codigo'].nunique()}")
        # Mostrar meses faltantes en la serie mensual
        if len(mensual) > 0:
            todas = pd.date_range(mensual["fecha"].min(), mensual["fecha"].max(), freq="MS")
            cubiertas = set(mensual["fecha"].dt.to_period("M").unique())
            faltantes = [d for d in todas if d.to_period("M") not in cubiertas]
            if faltantes:
                print(f"  Meses SIN datos: {[d.strftime('%Y-%m') for d in faltantes]}")
            else:
                print(f"  Cobertura mensual: completa")

    if df_imig is not None:
        print(f"\nIMIG - Ingresos y Gastos Mensual")
        print(f"  Rango : {df_imig['fecha'].min().strftime('%Y-%m')} - {df_imig['fecha'].max().strftime('%Y-%m')}")
        print(f"  Registros: {len(df_imig):,}")
        print(f"  Conceptos unicos: {df_imig['concepto_codigo'].nunique()}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Consolida datos del Sector Publico - Hacienda AR")
    parser.add_argument("--zip", default="data/raw/sector_publico.zip.zip",
                        help="Ruta al ZIP con los Excel originales")
    parser.add_argument("--output", default="output",
                        help="Carpeta de salida para los CSV")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    zip_path = Path(args.zip) if Path(args.zip).is_absolute() else root / args.zip
    raw_dir  = root / "data" / "raw"
    output_dir = root / args.output

    if not zip_path.exists():
        print(f"ERROR: No se encontro el ZIP en {zip_path}")
        print("Copia el ZIP a data/raw/sector_publico.zip.zip o pasa la ruta con --zip")
        sys.exit(1)

    process(zip_path, raw_dir, output_dir)


if __name__ == "__main__":
    main()
