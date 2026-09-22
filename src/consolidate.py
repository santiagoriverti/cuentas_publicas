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
        all_imig.extend(imig_parser.parse_mensualizacion(name, data))

    print("\n[3/3] Consolidando y guardando...")
    output_dir.mkdir(parents=True, exist_ok=True)

    if all_aif:
        df_aif = pd.DataFrame(all_aif)
        df_aif["fecha"] = pd.to_datetime(df_aif["fecha"], format="%Y-%m", errors="coerce")
        df_aif = df_aif.sort_values(["fecha", "periodo", "subsector", "concepto_codigo"])
        df_aif = df_aif.drop_duplicates(subset=["fecha", "periodo", "concepto_codigo", "subsector"])
        df_aif = _derivar_mensuales_aif(df_aif)
        out = output_dir / "aif_consolidado.csv"
        df_aif.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"  AIF: {len(df_aif):,} registros -> {out}")
    else:
        print("  [WARN] Sin registros AIF")
        df_aif = None

    if all_imig:
        df_imig = pd.DataFrame(all_imig)
        df_imig["fecha"] = pd.to_datetime(df_imig["fecha"], format="%Y-%m", errors="coerce")
        df_imig = _una_fuente_por_mes_imig(df_imig)
        df_imig = df_imig.sort_values(["fecha", "concepto_codigo"])
        df_imig = df_imig.drop_duplicates(
            subset=["fecha", "concepto_codigo", "nivel_jerarquia", "fuente_archivo"]
        )
        out = output_dir / "imig_consolidado.csv"
        df_imig.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"  IMIG: {len(df_imig):,} registros -> {out}")
    else:
        print("  [WARN] Sin registros IMIG")
        df_imig = None

    _print_summary(df_aif, df_imig)


def _una_fuente_por_mes_imig(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cada mes IMIG aparece en varios archivos: su publicacion original, la columna
    comparativa (mismo mes del ano anterior, con valores REVISADOS) del archivo del
    ano siguiente, y la hoja Mensualizacion. Para que la serie sea determinista y
    homogenea, cada mes se toma de UNA sola fuente, por prioridad:
      0 = publicacion original (mes mas reciente de su archivo)
      1 = hoja Mensualizacion (completa meses no publicados, ej. mar/jul-2026)
      2 = columna comparativa de otro archivo (unica fuente para 2019)
    """
    df = df.copy()
    es_mens = df["fuente_archivo"].str.endswith(imig_parser.MENSUALIZACION_TAG)
    mes_propio = df.groupby("fuente_archivo")["fecha"].transform("max")
    df["_prio"] = 2
    df.loc[~es_mens & (df["fecha"] == mes_propio), "_prio"] = 0
    df.loc[es_mens, "_prio"] = 1
    # Fuente elegida por mes: menor prioridad; empate -> nombre de archivo (determinista)
    elegida = (df[["fecha", "_prio", "fuente_archivo"]].drop_duplicates()
               .sort_values(["fecha", "_prio", "fuente_archivo"])
               .drop_duplicates("fecha"))
    df = df.merge(elegida[["fecha", "fuente_archivo"]], on=["fecha", "fuente_archivo"])
    return df.drop(columns="_prio")


def _derivar_mensuales_aif(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reconstruye meses AIF mensuales faltantes a partir de las hojas Acumulado:
      a) mens(M) = acum(M) - acum(M-1)                      (acum(0) = 0)
      b) mens(M) = acum(M+1) - acum(M-1) - mens(M+1)        (si falta acum(M))
    Validado exacto (dif 0,0 M$) contra abr/may/jun-2026 publicados.
    Caso de uso: jul-2026 (Hacienda publico jun y ago pero no jul).
    fuente_archivo queda como 'derivado: ...' para trazabilidad.
    """
    k = ["concepto_codigo", "subsector"]
    mens = df[df["periodo"] == "mensual"]
    acum = df[df["periodo"] == "acumulado"]
    if mens.empty or acum.empty:
        return df

    def serie(sub, fecha):
        x = sub[sub["fecha"] == fecha]
        return x.set_index(k)["valor_millones_pesos"] if len(x) else None

    todas = pd.date_range(mens["fecha"].min(), mens["fecha"].max(), freq="MS")
    presentes = set(mens["fecha"])
    nuevos = []
    for f in todas:
        if f in presentes:
            continue
        prev = f - pd.DateOffset(months=1)
        nxt = f + pd.DateOffset(months=1)
        a_prev = pd.Series(0.0) if f.month == 1 else serie(acum, prev)
        a_f, a_nxt, m_nxt = serie(acum, f), serie(acum, nxt), serie(mens, nxt)
        if a_prev is None:
            continue
        if a_f is not None:
            val = a_f - a_prev if f.month > 1 else a_f
            desc = f"derivado: acum {f:%Y-%m} - acum {prev:%Y-%m}"
            base = acum[acum["fecha"] == f]
        elif a_nxt is not None and m_nxt is not None and nxt.year == f.year:
            val = (a_nxt - a_prev - m_nxt) if f.month > 1 else (a_nxt - m_nxt)
            desc = f"derivado: acum {nxt:%Y-%m} - acum {prev:%Y-%m} - mens {nxt:%Y-%m}"
            base = acum[acum["fecha"] == nxt]
        else:
            continue
        val = val.dropna().round(6)
        rec = base.set_index(k).loc[val.index].reset_index()
        rec["valor_millones_pesos"] = val.values
        rec["fecha"], rec["anio"], rec["mes"] = f, f.year, f.month
        rec["periodo"] = "mensual"
        rec["fuente_archivo"] = desc
        print(f"  [DERIVADO] AIF {f:%Y-%m} mensual <- {desc} | {len(rec)} registros")
        nuevos.append(rec[df.columns])

    if nuevos:
        df = pd.concat([df] + nuevos, ignore_index=True)
        df = df.sort_values(["fecha", "periodo", "subsector", "concepto_codigo"])
    return df


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
        # Meses faltantes IMIG (el IMIG suele venir en archivo/hoja aparte del AIF;
        # un hueco aqui = falta el Excel IMIG de ese mes, no es bug de parseo)
        if len(df_imig) > 0:
            todas = pd.date_range(df_imig["fecha"].min(), df_imig["fecha"].max(), freq="MS")
            cubiertas = set(df_imig["fecha"].dt.to_period("M").unique())
            faltantes = [d for d in todas if d.to_period("M") not in cubiertas]
            if faltantes:
                print(f"  Meses SIN datos IMIG: {[d.strftime('%Y-%m') for d in faltantes]}")
                print(f"    (falta el archivo/hoja IMIG de ese mes en data/raw/)")
            else:
                print(f"  Cobertura mensual IMIG: completa")

    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Consolida datos del Sector Publico - Hacienda AR")
    parser.add_argument("--zip", default=None,
                        help="Ruta al ZIP con los Excel originales "
                             "(por defecto autodetecta data/raw/sector_publico*.zip)")
    parser.add_argument("--output", default="output",
                        help="Carpeta de salida para los CSV")
    args = parser.parse_args()

    root = Path(__file__).parent.parent
    raw_dir  = root / "data" / "raw"
    output_dir = root / args.output

    if args.zip:
        zip_path = Path(args.zip) if Path(args.zip).is_absolute() else root / args.zip
    else:
        # Autodeteccion: acepta sector_publico.zip o sector_publico.zip.zip
        # (toma el mas grande si hay varios). Evita tener que pasar --zip a mano.
        candidatos = sorted(raw_dir.glob("sector_publico*.zip"),
                            key=lambda p: p.stat().st_size, reverse=True)
        zip_path = candidatos[0] if candidatos else raw_dir / "sector_publico.zip"
        if candidatos:
            print(f"  [info] ZIP autodetectado: {zip_path.name}")

    if not zip_path.exists():
        print(f"ERROR: No se encontro el ZIP en {zip_path}")
        print("Copia el ZIP a data/raw/ (sector_publico.zip) o pasa la ruta con --zip")
        sys.exit(1)

    process(zip_path, raw_dir, output_dir)


if __name__ == "__main__":
    main()
