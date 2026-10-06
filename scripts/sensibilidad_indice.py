"""
Analisis de sensibilidad y validacion del indice macroeconomico (notebook 03).

Uso:
    python scripts/sensibilidad_indice.py [ruta a indice_macro.xlsx]   (por defecto _local_run/indice_macro.xlsx)

1. Reproduce el indice desde las hojas Variables / Arrastrados / Metodologia del Excel del NB03
   (y verifica que coincide con la hoja Indice).
2. Lo recalcula con variantes metodologicas razonables (pesos, normalizacion, tope, composicion,
   sacar un pilar o una variable) y mide que conclusiones se sostienen: promedio por gestion, ranking,
   ultimo mes.
3. Lo contrasta con una cronologia externa de recesiones: regla del Indice Lider de la UTDT
   (recesion = 6 o mas caidas mensuales seguidas del EMAE tendencia-ciclo de INDEC). Tambien sin el
   pilar Actividad, para que la validacion no sea circular.

Salida: _local_run/sensibilidad_indice.xlsx + resumen por pantalla.
"""

import io
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
EXCEL = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_local_run" / "indice_macro.xlsx"
OUT = ROOT / "_local_run" / "sensibilidad_indice.xlsx"
EMAE_TC = "143.3_NO_PR_2004_A_28"  # EMAE tendencia-ciclo (INDEC, datos.gob.ar)

CLIP_Z, MIN_PILARES = 3.0, 4  # iguales al NB03
GOBIERNOS = [("2003-05-25", "N. Kirchner"), ("2007-12-10", "C. Fernandez"), ("2011-12-10", "C. Fernandez II"),
             ("2015-12-10", "Macri"), ("2019-12-10", "A. Fernandez"), ("2023-12-10", "Milei")]
CORTAS = ["recaudacion_ia", "sipa_ia", "salario_real_ia", "salario_real_vs_maximo"]  # empiezan despues de 2012


def indice(X, OBS, meta, pesos="pilar", clip=CLIP_Z, stat="robusto", ventana=None, sin=()):
    """Mismo calculo que la celda 4 del NB03, con variantes."""
    cols = [c for c in X.columns if c not in sin]
    X, OBS, meta = X[cols], OBS[cols], meta.loc[cols]
    base = X.where(OBS)
    if ventana is not None:
        base = base.loc[ventana[0]:ventana[1]]
    if stat == "robusto":
        centro = base.median()
        escala = (base.quantile(0.75) - base.quantile(0.25)) / 1.349
    else:  # media y desvio estandar
        centro, escala = base.mean(), base.std()
    Z = (X - centro) / escala * meta["signo"]
    if clip:
        Z = Z.clip(-clip, clip)
    if pesos == "variable":
        return Z.mean(axis=1).where(Z.notna().sum(axis=1) >= 8)
    P = Z.T.groupby(meta["pilar"]).mean().T
    return P.mean(axis=1).where(P.notna().sum(axis=1) >= MIN_PILARES)


def gestion(idx):
    ini = [pd.Timestamp(g) for g, _ in GOBIERNOS]
    # el mes va a quien gobierno la mayor parte (asuncion hasta el dia 15 -> mes propio), como en el NB03
    lab = pd.Series(index=idx, dtype=object)
    for (g, nombre), d in zip(GOBIERNOS, ini):
        desde = d.to_period("M").to_timestamp() if d.day <= 15 else (d + pd.offsets.MonthBegin(1))
        lab[lab.index >= desde] = nombre
    return lab


def recesiones(tc):
    """Regla UTDT: 6 o mas caidas mensuales consecutivas del EMAE tendencia-ciclo. Devuelve los meses en
    recesion (del mes siguiente al pico hasta el valle) y la lista de episodios (pico, valle)."""
    cae = tc.diff() < 0
    rec, episodios, i = pd.Series(False, index=tc.index), [], 0
    v = cae.to_numpy()
    while i < len(v):
        if v[i]:
            j = i
            while j + 1 < len(v) and v[j + 1]:
                j += 1
            if j - i + 1 >= 6:
                rec.iloc[i:j + 1] = True
                episodios.append((tc.index[i - 1], tc.index[j]))
            i = j + 1
        else:
            i += 1
    return rec, episodios


def auc(score, y):
    # P(un mes de recesion tiene indice MAS BAJO que un mes de expansion); 0,5 = sin poder
    s_r, s_e = score[y], score[~y]
    return float((s_r.to_numpy()[:, None] < s_e.to_numpy()[None, :]).mean())


def main():
    x = pd.read_excel(EXCEL, sheet_name=None, index_col=0)
    X, OBS = x["Variables"], x["Arrastrados"] == 0
    meta = x["Metodologia"][["pilar", "signo"]]
    oficial = x["Indice"]["indice"]

    base = indice(X, OBS, meta)
    dif = (base.round(3) - oficial).abs().max()
    print(f"Reproduccion del indice oficial: dif max {dif:.4f} (redondeo a 3 decimales)")
    assert dif <= 0.0015, "no se reproduce el indice del NB03"

    pilares = sorted(meta["pilar"].unique())
    var = {
        "base (v9)": base,
        "pesos por variable": indice(X, OBS, meta, pesos="variable"),
        "normalizacion 2017-hoy (todas)": indice(X, OBS, meta, ventana=("2017-03-01", None)),
        "sin tope": indice(X, OBS, meta, clip=None),
        "tope +/-2": indice(X, OBS, meta, clip=2.0),
        "media y desvio": indice(X, OBS, meta, stat="media"),
        "sin variables cortas": indice(X, OBS, meta, sin=CORTAS),
        "Precios vs meta 10% (ancla)": x["Indice"]["indice_ancla"],
    }
    var |= {f"sin {p}": indice(X, OBS, meta, sin=tuple(meta.index[meta["pilar"] == p])) for p in pilares}
    sin_var = {f"sin {c}": indice(X, OBS, meta, sin=(c,)) for c in meta.index}
    V = pd.DataFrame(var)
    Vv = pd.DataFrame(sin_var)

    # 1. promedio por gestion y ranking
    lab = gestion(V.index)
    G = V.groupby(lab).mean().reindex([g for _, g in GOBIERNOS])
    Gv = Vv.groupby(lab).mean().reindex(G.index)
    R = G.rank(ascending=False).astype(int)
    rango = pd.DataFrame({"base": G["base (v9)"], "min variantes": G.min(axis=1), "max variantes": G.max(axis=1),
                          "min sin 1 variable": Gv.min(axis=1), "max sin 1 variable": Gv.max(axis=1),
                          "puesto base": R["base (v9)"], "puesto min": R.min(axis=1), "puesto max": R.max(axis=1)})
    # pares de gestiones: en cuantas variantes A > B
    todas = pd.concat([G, Gv], axis=1)
    pares = []
    nombres = list(G.index)
    for i, a in enumerate(nombres):
        for b in nombres[i + 1:]:
            gana = (todas.loc[a] > todas.loc[b]).mean()
            pares.append({"A": a, "B": b, "dif base": G.loc[a, "base (v9)"] - G.loc[b, "base (v9)"],
                          "% variantes A > B": gana * 100,
                          "robusto": "si" if gana in (0.0, 1.0) else ("casi" if min(gana, 1 - gana) <= 0.1 else "no")})
    pares = pd.DataFrame(pares)

    # 2. ultimo mes y parecido con la base
    ult = V.index[V["base (v9)"].notna()].max()
    resumen = pd.DataFrame({"ultimo mes": V.loc[ult], "hace 12 meses": V.loc[ult - pd.DateOffset(months=12)],
                            "corr con base": V.corr()["base (v9)"]})

    # 3. validacion contra recesiones (regla UTDT sobre el EMAE tendencia-ciclo)
    r = requests.get("https://apis.datos.gob.ar/series/api/series/", params={"ids": EMAE_TC, "format": "csv", "limit": 5000}, timeout=60)
    r.raise_for_status()
    tc = pd.read_csv(io.StringIO(r.text), parse_dates=["indice_tiempo"]).set_index("indice_tiempo").iloc[:, 0].dropna()
    rec, episodios = recesiones(tc)
    rec = rec.reindex(V.index).fillna(False).astype(bool)
    val = []
    for nombre, s in V.items():
        ok = s.notna() & rec.index.isin(tc.index)
        val.append({"variante": nombre, "media en recesion": s[ok & rec].mean(), "media en expansion": s[ok & ~rec].mean(),
                    "AUC (recesion = indice mas bajo)": auc(s[ok], rec[ok])})
    val = pd.DataFrame(val).set_index("variante")
    epi = []
    for pico, valle in episodios:
        tramo = V.loc[pico:valle, "base (v9)"].dropna()
        sa = V.loc[pico:valle, "sin Actividad"].dropna()
        if tramo.empty:
            continue
        epi.append({"pico": pico.strftime("%Y-%m"), "valle": valle.strftime("%Y-%m"), "meses": len(tramo) - 1,
                    "caida EMAE-TC %": (tc[valle] / tc[pico] - 1) * 100,
                    "indice en el pico": tramo.iloc[0], "indice minimo": tramo.min(), "mes del minimo": tramo.idxmin().strftime("%Y-%m"),
                    "sin Actividad: minimo": sa.min()})
    epi = pd.DataFrame(epi)

    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", 30)
    print(f"\nRecesiones (regla UTDT, EMAE tendencia-ciclo hasta {tc.index.max():%Y-%m}):")
    print(epi.round(2).to_string(index=False))
    print("\nValidacion:")
    print(val.round(2).to_string())
    print(f"\nPromedio por gestion: base y rango en {V.shape[1]} variantes + {Vv.shape[1]} sacando una variable:")
    print(rango.round(2).to_string())
    print("\nComparaciones entre gestiones (todas las variantes):")
    print(pares.round(2).to_string(index=False))
    print(f"\nUltimo mes ({ult:%Y-%m}) por variante:")
    print(resumen.round(2).to_string())

    with pd.ExcelWriter(OUT, engine="openpyxl") as xw:
        pd.DataFrame({"Contenido": [
            f"Sensibilidad y validacion del indice macro (NB03), a partir de {EXCEL.name}.",
            "Variantes: mismo calculo que el NB03 cambiando una decision por vez (pesos, normalizacion, tope, composicion).",
            "Por_gestion: promedio por gestion en cada variante; Rango: base, min y max; Pares: % de variantes en que A > B.",
            "Recesiones: regla del Indice Lider UTDT (6+ caidas mensuales seguidas del EMAE tendencia-ciclo de INDEC).",
            "AUC: probabilidad de que un mes en recesion tenga el indice mas bajo que un mes en expansion (0,5 = azar).",
        ]}).to_excel(xw, sheet_name="Leeme", index=False)
        V.round(3).rename_axis("fecha").to_excel(xw, sheet_name="Variantes")
        G.round(3).to_excel(xw, sheet_name="Por_gestion")
        Gv.round(3).to_excel(xw, sheet_name="Por_gestion_sin_1_var")
        rango.round(3).to_excel(xw, sheet_name="Rango")
        pares.round(3).to_excel(xw, sheet_name="Pares", index=False)
        resumen.round(3).to_excel(xw, sheet_name="Ultimo_mes")
        val.round(3).to_excel(xw, sheet_name="Validacion")
        epi.round(3).to_excel(xw, sheet_name="Recesiones", index=False)
    print(f"\nGuardado: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
