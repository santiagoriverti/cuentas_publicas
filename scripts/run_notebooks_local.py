"""
Ejecuta los notebooks contra los archivos LOCALES del repo (sin push ni Colab).

Uso:
    python scripts/run_notebooks_local.py            # NB01 y NB02
    python scripts/run_notebooks_local.py 02         # solo NB02

Los notebooks leen los datos desde GitHub (raw.githubusercontent.com). Este script copia
cada notebook a _local_run/ con una celda inicial que redirige esas URLs a los archivos
del disco, desactiva el `!pip install` y lo ejecuta con nbconvert. Sirve para verificar
cambios ANTES de hacer push. Salidas (PNG, Excel, ZIP, notebook ejecutado) en _local_run/.

Requiere: pip install nbconvert ipykernel matplotlib
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_local_run"
NOTEBOOKS = {"01": "01_consolidar", "02": "02_analisis_fiscal"}

PATCH = f'''
import requests, pandas as _pd
_ROOT = {ROOT.as_posix()!r}
_PREF = ('https://raw.githubusercontent.com/santiagoriverti/cuentas_publicas/main',
         'https://github.com/santiagoriverti/cuentas_publicas/raw/main')
def _loc(u):
    for p in _PREF:
        if isinstance(u, str) and u.startswith(p):
            return _ROOT + u[len(p):]
    return u
class _R:
    def __init__(s, path):
        s.content = open(path, 'rb').read(); s.status_code = 200
        s.text = s.content.decode('utf-8', 'replace')
    def raise_for_status(s): pass
_rg = requests.get
requests.get = lambda u, *a, **k: _R(_loc(u)) if _loc(u) != u else _rg(u, *a, **k)
_rc = _pd.read_csv;   _pd.read_csv   = lambda u, *a, **k: _rc(_loc(u), *a, **k)
_re = _pd.read_excel; _pd.read_excel = lambda u, *a, **k: _re(_loc(u), *a, **k)
'''


def preparar(nb: str) -> Path:
    j = json.load(open(ROOT / "notebooks" / f"{nb}.ipynb", encoding="utf-8"))
    for c in j["cells"]:
        if c["cell_type"] == "code":
            s = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
            c["source"] = s.replace("!pip install", "pass  # pip install")
    j["cells"].insert(0, {"cell_type": "code", "metadata": {}, "execution_count": None,
                          "outputs": [], "source": PATCH})
    dst = OUT / f"{nb}.ipynb"
    json.dump(j, open(dst, "w", encoding="utf-8"))
    return dst


def main():
    OUT.mkdir(exist_ok=True)
    elegidos = sys.argv[1:] or list(NOTEBOOKS)
    for k in elegidos:
        nb = NOTEBOOKS[k]
        src = preparar(nb)
        print(f"Ejecutando {nb} ...")
        r = subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook",
                            "--execute", "--ExecutePreprocessor.timeout=900",
                            "--output", f"{nb}_ejecutado.ipynb", src.name],
                           cwd=OUT, capture_output=True, text=True,
                           env={**__import__("os").environ, "PYTHONUTF8": "1"})
        if r.returncode != 0:
            print(r.stderr[-3000:])
            raise SystemExit(f"ERROR ejecutando {nb}")
        print(f"  OK -> {OUT.name}/{nb}_ejecutado.ipynb")
    print("Salidas:", ", ".join(sorted(p.name for p in OUT.iterdir()
                                       if p.suffix in (".zip", ".xlsx", ".png"))))


if __name__ == "__main__":
    main()
