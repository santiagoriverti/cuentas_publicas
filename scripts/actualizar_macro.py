"""
Descarga las series macro externas del indice macroeconomico (notebook 03) y las guarda en
data/reference/macro_mensual.csv (una fila por mes, valores crudos sin transformar).

Uso:
    python scripts/actualizar_macro.py

Fuentes (todas publicas, sin clave):
- datos.gob.ar (API Series de Tiempo): EMAE, SIPA, indice de salarios, desocupacion EPH,
  exportaciones/importaciones, PIB nominal trimestral.
- BCRA API v4 (estadisticas/monetarias): reservas, tipo de cambio A3500, BADLAR, prestamos al
  sector privado, expectativa de inflacion REM, inflacion mensual (historica, pre-2017).
- BCRA ITCRMSerie.xlsx: tipo de cambio real multilateral (promedio mensual).
- argentinadatos.com: riesgo pais (EMBI) y dolar contado con liquidacion.

Si una fuente falla se conserva la columna que ya estaba en el CSV (aviso por pantalla), asi una
caida puntual de una API no borra datos.

Agregacion a mensual: series diarias -> promedio del mes, salvo stocks (reservas) -> ultimo dato
del mes. Trimestrales (desocupacion, PIB) -> mismo valor en los 3 meses del trimestre.
"""

import io
from pathlib import Path

import pandas as pd
import requests
import urllib3

urllib3.disable_warnings()  # el certificado de api.bcra.gob.ar no valida en algunas PCs

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "data" / "reference" / "macro_mensual.csv"
DESDE = "2003-01-01"

DATOS_GOB = "https://apis.datos.gob.ar/series/api/series/"
BCRA = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"
ITCRM_XLSX = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/ITCRMSerie.xlsx"
ARG_DATOS = "https://api.argentinadatos.com/v1"

# columna -> (id serie datos.gob.ar, trimestral?)
SERIES_DATOS_GOB = {
    "emae_desest":         ("143.3_NO_PR_2004_A_31", False),       # EMAE desestacionalizado, 2004=100
    "sipa_asal_priv":      ("151.1_AARIADOTAC_2012_M_26", False),  # asalariados privados registrados, desest. (miles)
    "salario_registrado":  ("149.1_TL_REGIADO_OCTU_0_16", False),  # indice de salarios, empleo registrado
    "desocupacion":        ("42.3_EPH_PUNTUATAL_0_M_30", True),    # tasa de desocupacion EPH (%)
    "expo_usd":            ("74.3_IET_0_M_16", False),             # exportaciones (M USD)
    "impo_usd":            ("74.3_IIT_0_M_25", False),             # importaciones (M USD)
    "pib_nominal_anualizado": ("166.2_PPIB_0_0_3", True),          # PIB precios corrientes (M$), trimestre ANUALIZADO (x4)
}

# columna -> (idVariable BCRA, agregacion mensual)
SERIES_BCRA = {
    "reservas_usd":      (1, "last"),   # reservas internacionales brutas (M USD)
    "a3500":             (5, "mean"),   # tipo de cambio mayorista de referencia ($/USD)
    "badlar":            (7, "mean"),   # BADLAR bancos privados (% TNA)
    "prestamos_privados": (26, "mean"), # prestamos al sector privado (M$)
    "rem_12m":           (29, "last"),  # REM: mediana inflacion esperada proximos 12 meses (%)
    "inflacion_mensual": (27, "last"),  # inflacion mensual (%); el NB03 la usa solo antes de 2017
}


def _mensual(s: pd.Series, how: str) -> pd.Series:
    s = s.sort_index()
    return s.resample("MS").last() if how == "last" else s.resample("MS").mean()


def datos_gob(sid: str, trimestral: bool) -> pd.Series:
    r = requests.get(DATOS_GOB, params={"ids": sid, "format": "csv", "limit": 5000,
                                        "start_date": DESDE}, timeout=60)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text), parse_dates=["indice_tiempo"])
    s = df.set_index("indice_tiempo").iloc[:, 0].dropna()
    if trimestral:  # repetir el valor del trimestre en sus 3 meses
        s = pd.concat([s.rename(lambda d: d + pd.DateOffset(months=k)) for k in range(3)]).sort_index()
    return s


def bcra(var_id: int, how: str) -> pd.Series:
    filas, offset = [], 0
    while True:
        r = requests.get(f"{BCRA}/{var_id}", params={"desde": DESDE, "limit": 3000, "offset": offset},
                         timeout=60, verify=False)
        r.raise_for_status()
        det = r.json()["results"][0]["detalle"]
        filas += det
        if len(det) < 3000:
            break
        offset += 3000
    df = pd.DataFrame(filas)
    s = df.set_index(pd.to_datetime(df["fecha"]))["valor"].astype(float)
    return _mensual(s, how)


def itcrm() -> pd.Series:
    r = requests.get(ITCRM_XLSX, timeout=120, verify=False)
    r.raise_for_status()
    df = pd.read_excel(io.BytesIO(r.content), sheet_name="ITCRM y bilaterales", header=1)
    df.columns = [str(c).strip() for c in df.columns]  # el encabezado trae "ITCRM " con espacio
    df = df[pd.to_datetime(df["Período"], errors="coerce").notna()]
    s = df.set_index(pd.to_datetime(df["Período"]))["ITCRM"].astype(float)
    return _mensual(s[s.index >= DESDE], "mean")


def arg_datos(path: str, campo: str) -> pd.Series:
    r = requests.get(f"{ARG_DATOS}/{path}", timeout=60)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    s = df.set_index(pd.to_datetime(df["fecha"]))[campo].astype(float)
    return _mensual(s[s.index >= DESDE], "mean")


def main():
    previo = (pd.read_csv(OUT_FILE, parse_dates=["fecha"], index_col="fecha")
              if OUT_FILE.exists() else pd.DataFrame())

    tareas = {col: (lambda a=args: datos_gob(*a)) for col, args in SERIES_DATOS_GOB.items()}
    tareas |= {col: (lambda a=args: bcra(*a)) for col, args in SERIES_BCRA.items()}
    tareas["itcrm"] = itcrm
    tareas["riesgo_pais"] = lambda: arg_datos("finanzas/indices/riesgo-pais", "valor")
    tareas["ccl"] = lambda: arg_datos("cotizaciones/dolares/contadoconliqui", "venta")

    cols, fallas = {}, []
    for col, fn in tareas.items():
        try:
            cols[col] = fn()
            s = cols[col].dropna()
            print(f"  {col:24} {s.index.min():%Y-%m} .. {s.index.max():%Y-%m}  ({len(s)} meses)")
        except Exception as e:  # noqa: BLE001 - cualquier falla de red/formato
            fallas.append(col)
            print(f"  {col:24} FALLO ({type(e).__name__}: {e})")
            if col in previo:
                cols[col] = previo[col].dropna()
                print(f"  {'':24} se conserva la version anterior")

    df = pd.DataFrame(cols)
    df.index.name = "fecha"
    df = df[df.index >= DESDE].sort_index()
    df.round(6).to_csv(OUT_FILE)
    print(f"Guardado: {OUT_FILE.relative_to(ROOT)} ({len(df)} meses x {df.shape[1]} series)")
    if fallas:
        print(f"ATENCION: fallaron {', '.join(fallas)}")


if __name__ == "__main__":
    main()
