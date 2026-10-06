"""
Control de calidad mensual del indice macro, ANTES de publicar.

Uso:
    python scripts/control_calidad.py                 # revisa
    python scripts/control_calidad.py --guardar       # revisa y, si no hay ALERTAS, guarda el indice
                                                      # del mes en output/indice_macro.csv (para commitear)
    python scripts/control_calidad.py --contra HEAD~1 # comparar las series contra otra version de git

Revisa:
A. data/reference/macro_mensual.csv contra su ultima version commiteada (git):
   - columnas que faltan o aparecen;
   - series que perdieron meses (el ultimo dato retrocedio) o que no sumaron datos;
   - revisiones de valores ya publicados (algunas son normales: EMAE y SIPA desestacionalizados, PIB);
   - saltos atipicos en los meses nuevos (variacion mensual en z robusto contra la historia de la serie).
B. el indice del NB03 (_local_run/indice_macro.xlsx) contra el ultimo publicado (output/indice_macro.csv):
   - revisiones del indice en meses ya publicados;
   - ultimo mes, rango de sensibilidad y variables sin dato propio (arrastradas).

Sale con codigo 1 si hay ALERTAS (revisar a mano antes de publicar; los avisos son informativos).
"""

import argparse
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MACRO = "data/reference/macro_mensual.csv"
PUBLICADO = ROOT / "output" / "indice_macro.csv"

# Umbrales
REV_AVISO, REV_ALERTA = 0.005, 0.05   # revision relativa de un valor historico (0,5% aviso; 5% alerta)
REV_VIEJO = 24                        # meses: datos de mas de 2 anios alertan desde REV_ALERTA
REV_RECIENTE = 0.25                   # datos recientes: alerta si cambian mas de 25%
SALTO_AVISO, SALTO_ALERTA = 4.0, 6.0  # z robusto de la variacion mensual de un dato nuevo
IDX_AVISO, IDX_ALERTA = 0.03, 0.10    # revision del indice ya publicado (en z)

alertas, avisos = [], []


def alerta(msg):
    alertas.append(msg)
    print(f"  ALERTA  {msg}")


def aviso(msg):
    avisos.append(msg)
    print(f"  aviso   {msg}")


def leer_git(ref, ruta):
    r = subprocess.run(["git", "show", f"{ref}:{ruta}"], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"No se pudo leer {ruta} en {ref}: {r.stderr.decode(errors='replace')}")
    return pd.read_csv(io.BytesIO(r.stdout), index_col="fecha", parse_dates=["fecha"])


def revisar_series(ref, ruta):
    print(f"\nA. Series macro: {ruta} vs {MACRO} en {ref}")
    nuevo = pd.read_csv(ruta, index_col="fecha", parse_dates=["fecha"])
    viejo = leer_git(ref, MACRO)
    if nuevo.equals(viejo):
        print(f"  sin cambios respecto de {ref} (si ya commiteaste el mes, usar --contra HEAD~1)")
        return
    sin_nuevos, con_nuevos = [], []
    for c in sorted(set(viejo.columns) - set(nuevo.columns)):
        alerta(f"falta la columna {c}")
    for c in sorted(set(nuevo.columns) - set(viejo.columns)):
        aviso(f"columna nueva {c}")
    filas = []
    for c in [c for c in nuevo.columns if c in viejo.columns]:
        n, v = nuevo[c].dropna(), viejo[c].dropna()
        if n.empty:
            alerta(f"{c}: quedo vacia")
            continue
        un, uv = n.index.max(), v.index.max() if not v.empty else None
        if uv is not None and un < uv:
            alerta(f"{c}: el ultimo dato retrocedio ({uv:%Y-%m} -> {un:%Y-%m})")
        # revisiones de valores que ya estaban
        comun = n.index.intersection(v.index)
        escala = max(v.abs().median() * 0.05, 1e-9)  # evita dividir por valores cercanos a 0
        rel = ((n[comun] - v[comun]).abs() / np.maximum(v[comun].abs(), escala))
        rev = rel[rel > REV_AVISO]
        if not rev.empty:
            corte = (un if uv is None else uv) - pd.DateOffset(months=REV_VIEJO)
            viejos = rev[rev.index < corte]
            filas.append({"serie": c, "meses revisados": len(rev), "desde": rev.index.min().strftime("%Y-%m"),
                          "max %": rev.max() * 100, "mes del max": rev.idxmax().strftime("%Y-%m"),
                          "max % (> 2 anios)": viejos.max() * 100 if not viejos.empty else 0.0})
            if not viejos.empty and viejos.max() > REV_ALERTA:
                alerta(f"{c}: revision de {viejos.max() * 100:.1f}% en {viejos.idxmax():%Y-%m} (dato de mas de 2 anios)")
            # el ultimo mes de la version anterior suele estar incompleto (series diarias): va al control de saltos
            recientes = rev[(rev.index >= corte) & (rev.index != uv)]
            if not recientes.empty and recientes.max() > REV_RECIENTE:
                alerta(f"{c}: revision de {recientes.max() * 100:.0f}% en {recientes.idxmax():%Y-%m}")
        nuevos = n.index.difference(v.index)
        (con_nuevos if len(nuevos) else sin_nuevos).append(f"{c} ({un:%Y-%m})")
        # saltos en los meses nuevos y en el ultimo mes anterior si cambio (series diarias: mes incompleto)
        if uv is not None and uv in n.index and rel.get(uv, 0) > REV_AVISO:
            nuevos = nuevos.union(pd.DatetimeIndex([uv]))
        if len(nuevos) == 0:
            continue
        if (n > 0).all():
            d = np.log(n).diff().dropna()
        else:  # flujos que pueden ser negativos (resultado fiscal): cambio relativo al nivel de 12 meses
            d = (n.diff() / n.abs().rolling(12, min_periods=6).mean().shift(1)).dropna()
        hist = d[d.index < nuevos.min()]
        if len(hist) < 24:
            continue
        q1, q3 = hist.quantile([0.25, 0.75])
        esc = (q3 - q1) / 1.349
        if esc <= 0:
            continue
        for f in nuevos:
            if f in d.index:
                z = (d[f] - hist.median()) / esc
                if abs(z) > SALTO_ALERTA:
                    alerta(f"{c}: salto atipico en {f:%Y-%m} (z {z:+.1f} de la variacion mensual)")
                elif abs(z) > SALTO_AVISO:
                    aviso(f"{c}: salto grande en {f:%Y-%m} (z {z:+.1f})")
    print(f"  con datos nuevos: {', '.join(con_nuevos) or '-'}")
    print(f"  sin datos nuevos (informativo; series con rezago o que no cambian): {', '.join(sin_nuevos) or '-'}")
    if filas:
        print("\n  Revisiones de datos ya publicados (> 0,5%; EMAE/SIPA desestacionalizados y PIB se revisan siempre):")
        print(pd.DataFrame(filas).round(2).to_string(index=False))


def revisar_indice(excel):
    print(f"\nB. Indice: {excel.relative_to(ROOT) if excel.is_relative_to(ROOT) else excel} vs {PUBLICADO.relative_to(ROOT)}")
    if not excel.exists():
        alerta(f"no existe {excel}: correr antes `python scripts/run_notebooks_local.py 03`")
        return None
    x = pd.read_excel(excel, sheet_name=None, index_col=0)
    ind, arr = x["Indice"], x["Arrastrados"]
    ult = ind.index.max()
    fila = ind.loc[ult]
    hace = ind.loc[ult - pd.DateOffset(months=12)]
    print(f"  ultimo mes {ult:%Y-%m}: indice {fila['indice']:+.3f} (hace 12 meses {hace['indice']:+.3f}) | "
          f"rango de sensibilidad {fila['banda_min']:+.2f} a {fila['banda_max']:+.2f}")
    if fila["banda_min"] < 0 < fila["banda_max"]:
        aviso("el rango de sensibilidad cruza el 0: comunicar el signo del mes como no concluyente")
    sin_dato = [c for c in arr.columns if arr.loc[ult, c] == 1]
    print(f"  variables arrastradas en {ult:%Y-%m} ({len(sin_dato)} de {arr.shape[1]}): {', '.join(sin_dato) or '-'}")
    if PUBLICADO.exists():
        pub = pd.read_csv(PUBLICADO, index_col="fecha", parse_dates=["fecha"])
        comun = ind.index.intersection(pub.index)
        d = (ind.loc[comun, "indice"] - pub.loc[comun, "indice"]).abs().dropna()
        nuevos = ind.index.difference(pub.index)
        print(f"  publicado hasta {pub.index.max():%Y-%m}; meses nuevos: {', '.join(f'{m:%Y-%m}' for m in nuevos) or '-'}")
        if len(d):
            print(f"  revision del indice publicado: max {d.max():.3f} ({d.idxmax():%Y-%m}), "
                  f"{(d > IDX_AVISO).sum()} meses > {IDX_AVISO}")
            if d.max() > IDX_ALERTA:
                alerta(f"el indice ya publicado cambia hasta {d.max():.2f} ({d.idxmax():%Y-%m}): explicar (datos revisados o metodologia)")
            elif d.max() > IDX_AVISO:
                aviso(f"el indice ya publicado cambia hasta {d.max():.2f} ({d.idxmax():%Y-%m})")
    else:
        aviso(f"no existe {PUBLICADO.name}: se crea con --guardar")
    return ind


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guardar", action="store_true", help="si no hay ALERTAS, guarda output/indice_macro.csv")
    ap.add_argument("--contra", default="HEAD", help="version de git contra la que comparar las series")
    ap.add_argument("--excel", default=str(ROOT / "_local_run" / "indice_macro.xlsx"))
    ap.add_argument("--macro", default=str(ROOT / MACRO), help="CSV de series a revisar (por defecto el del repo)")
    a = ap.parse_args()

    revisar_series(a.contra, Path(a.macro))
    ind = revisar_indice(Path(a.excel))

    print(f"\nResultado: {len(alertas)} ALERTAS, {len(avisos)} avisos")
    if a.guardar:
        if alertas:
            print("No se guarda output/indice_macro.csv: resolver o justificar las ALERTAS primero.")
        elif ind is not None:
            ind.round(3).rename_axis("fecha").to_csv(PUBLICADO)
            print(f"Guardado: {PUBLICADO.relative_to(ROOT)} ({ind.index.min():%Y-%m} a {ind.index.max():%Y-%m})")
    sys.exit(1 if alertas else 0)


if __name__ == "__main__":
    main()
