"""
Script principal de consolidación.
Extrae el ZIP, parsea todos los Excel y genera los CSVs de salida.

Uso:
    python src/consolidate.py --zip <ruta_al_zip> [--output <carpeta_output>]
"""

import argparse
import sys
import zipfile
from pathlib import Path

import pandas as pd

# Importar parsers locales
sys.path.insert(0, str(Path(__file__).parent))
import aif_parser
import imig_parser


def process_zip(zip_path: Path, raw_dir: Path, output_dir: Path):
    """Extrae archivos, parsea y guarda CSVs consolidados."""

    # ── Extraer archivos raw ──────────────────────────────────────
    print(f"\n[1/3] Extrayendo archivos de {zip_path.name} -> {raw_dir}")
    with zipfile.ZipFile(zip_path, "r") as z:
        names = [n for n in z.namelist() if n.lower().endswith((".xls", ".xlsx"))]
        print(f"  {len(names)} archivos Excel encontrados")
        for name in names:
            dest = raw_dir / name
            if not dest.exists():
                z.extract(name, raw_dir)

    # ── Parsear AIF e IMIG ────────────────────────────────────────
    print("\n[2/3] Parseando archivos…")
    all_aif = []
    all_imig = []

    with zipfile.ZipFile(zip_path, "r") as z:
        for name in sorted(names):
            data = z.read(name)
            print(f"\n→ {name}")
            aif_recs = aif_parser.parse_file(name, data)
            imig_recs = imig_parser.parse_file(name, data)
            all_aif.extend(aif_recs)
            all_imig.extend(imig_recs)

    # ── Armar DataFrames y deduplicar ────────────────────────────
    print("\n[3/3] Consolidando y guardando…")
    output_dir.mkdir(parents=True, exist_ok=True)

    if all_aif:
        df_aif = pd.DataFrame(all_aif)
        df_aif["fecha"] = pd.to_datetime(df_aif["fecha"], format="%Y-%m", errors="coerce")
        df_aif = df_aif.sort_values(["fecha", "periodo", "subsector", "concepto_codigo"])
        df_aif = df_aif.drop_duplicates(
            subset=["fecha", "periodo", "concepto_codigo", "subsector"]
        )
        out_aif = output_dir / "aif_consolidado.csv"
        df_aif.to_csv(out_aif, index=False, encoding="utf-8-sig")
        print(f"  AIF: {len(df_aif):,} registros → {out_aif}")
    else:
        print("  [WARN] Sin registros AIF")

    if all_imig:
        df_imig = pd.DataFrame(all_imig)
        df_imig["fecha"] = pd.to_datetime(df_imig["fecha"], format="%Y-%m", errors="coerce")
        df_imig = df_imig.sort_values(["fecha", "concepto_codigo"])
        df_imig = df_imig.drop_duplicates(
            subset=["fecha", "concepto_codigo", "fuente_archivo"]
        )
        out_imig = output_dir / "imig_consolidado.csv"
        df_imig.to_csv(out_imig, index=False, encoding="utf-8-sig")
        print(f"  IMIG: {len(df_imig):,} registros → {out_imig}")
    else:
        print("  [WARN] Sin registros IMIG")

    _print_summary(df_aif if all_aif else None, df_imig if all_imig else None)


def _print_summary(df_aif, df_imig):
    print("\n" + "=" * 60)
    print("RESUMEN DE COBERTURA")
    print("=" * 60)

    if df_aif is not None:
        fechas = df_aif["fecha"].dropna().sort_values()
        print(f"\nAIF - Sector Público Base Caja")
        print(f"  Rango: {fechas.min().strftime('%Y-%m')} → {fechas.max().strftime('%Y-%m')}")
        print(f"  Meses cubiertos: {df_aif['fecha'].nunique()}")
        print(f"  Conceptos únicos: {df_aif['concepto_codigo'].nunique()}")
        print(f"  Periodos: {df_aif['periodo'].unique().tolist()}")

    if df_imig is not None:
        fechas = df_imig["fecha"].dropna().sort_values()
        print(f"\nIMIG - Ingresos y Gastos Mensual")
        print(f"  Rango: {fechas.min().strftime('%Y-%m')} → {fechas.max().strftime('%Y-%m')}")
        print(f"  Meses cubiertos: {df_imig['fecha'].nunique()}")
        print(f"  Conceptos únicos: {df_imig['concepto_codigo'].nunique()}")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Consolida datos del Sector Público - Hacienda AR")
    parser.add_argument("--zip", default="data/raw/sector_publico.zip.zip",
                        help="Ruta al archivo ZIP con los Excel")
    parser.add_argument("--output", default="output",
                        help="Carpeta de salida para los CSV")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    zip_path = Path(args.zip) if Path(args.zip).is_absolute() else root / args.zip
    raw_dir = root / "data" / "raw"
    output_dir = root / args.output

    if not zip_path.exists():
        print(f"ERROR: No se encontró el ZIP en {zip_path}")
        print("Copiá el ZIP a data/raw/sector_publico.zip.zip o pasá la ruta con --zip")
        sys.exit(1)

    process_zip(zip_path, raw_dir, output_dir)


if __name__ == "__main__":
    main()
