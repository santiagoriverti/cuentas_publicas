"""
Modulo de deflacion: convierte series en pesos corrientes a pesos constantes
usando el IPC Nivel General del INDEC.

Uso:
    from src.deflate import load_ipc, deflate_series

El IPC esta en data/reference/IPC.xlsx o descargable desde GitHub.
"""

import io
from pathlib import Path

import pandas as pd
import requests


IPC_LOCAL  = Path(__file__).parent.parent / "data" / "reference" / "IPC.xlsx"
IPC_GITHUB = "https://github.com/santiagoriverti/cuentas_publicas/raw/main/data/reference/IPC.xlsx"


def load_ipc() -> pd.Series:
    """
    Carga el IPC Nivel General y retorna una Serie con indice datetime mensual.
    Busca primero en local, luego descarga desde GitHub.
    """
    if IPC_LOCAL.exists():
        df = pd.read_excel(IPC_LOCAL, usecols=["date", "Nivel general"])
    else:
        print("IPC no encontrado localmente, descargando desde GitHub...")
        resp = requests.get(IPC_GITHUB)
        resp.raise_for_status()
        df = pd.read_excel(io.BytesIO(resp.content), usecols=["date", "Nivel general"])

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    ipc = df["Nivel general"].rename("ipc")
    print(f"IPC cargado: {ipc.index.min().strftime('%Y-%m')} a {ipc.index.max().strftime('%Y-%m')}")
    return ipc


def deflate_series(serie: pd.Series, ipc: pd.Series,
                   base_date: str = None) -> pd.Series:
    """
    Convierte una serie nominal a pesos constantes del periodo base.

    Args:
        serie     : Serie con indice datetime mensual y valores en MM ARS nominales
        ipc       : Serie del IPC Nivel General (indice datetime mensual)
        base_date : Periodo de referencia, ej. '2026-04'. Si None, usa el ultimo mes del IPC.

    Returns:
        Serie en pesos constantes del periodo base.
    """
    if base_date is None:
        base_date = ipc.index.max()
    else:
        base_date = pd.Timestamp(base_date)

    ipc_base = ipc.loc[base_date]

    # Alinear IPC con la serie (frecuencia mensual)
    serie_monthly = serie.copy()
    serie_monthly.index = serie_monthly.index.to_period("M").to_timestamp()
    ipc_monthly   = ipc.copy()
    ipc_monthly.index = ipc_monthly.index.to_period("M").to_timestamp()

    ipc_aligned = ipc_monthly.reindex(serie_monthly.index)
    real = serie_monthly * (ipc_base / ipc_aligned)
    return real


def deflate_df(df: pd.DataFrame, value_col: str,
               date_col: str, ipc: pd.Series,
               base_date: str = None) -> pd.DataFrame:
    """
    Agrega columna 'valor_real' a un DataFrame con valores deflactados.

    Args:
        df        : DataFrame con columnas de fecha y valor nominal
        value_col : Nombre de la columna con valores nominales
        date_col  : Nombre de la columna de fecha
        ipc       : Serie del IPC
        base_date : Periodo de referencia (default: ultimo mes del IPC)

    Returns:
        DataFrame con columna adicional 'valor_real' y 'base_deflacion'
    """
    if base_date is None:
        base_date = ipc.index.max().strftime("%Y-%m")

    base_ts  = pd.Timestamp(base_date)
    ipc_base = ipc.loc[base_ts]

    df = df.copy()
    fechas = pd.to_datetime(df[date_col]).dt.to_period("M").dt.to_timestamp()
    ipc_aligned = ipc.reindex(fechas.values).values

    df["valor_real"]     = df[value_col] * (ipc_base / ipc_aligned)
    df["base_deflacion"] = base_date
    return df
