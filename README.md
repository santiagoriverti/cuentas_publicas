# Cuentas Publicas Argentina - Sector Publico Base Caja 2020-2026

Datos fiscales del Sector Publico Nacional (Secretaria de Hacienda) consolidados en un unico dataset tidy.

---

## Abrir en Google Colab

| Notebook | Descripcion | Link |
|---|---|---|
| **01 - Consolidacion** | Carga los datos desde GitHub y exporta un Excel unificado | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb) |
| **02 - Analisis Fiscal** | Visualizaciones del resultado primario, gasto, transferencias a provincias | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb) |

---

## Fuente de datos

**Secretaria de Hacienda - Ministerio de Economia**  
https://www.argentina.gob.ar/economia/sechacienda/infoestadistica

- **AIF** - Sector Publico Base Caja (Esquema Ahorro-Inversion-Financiamiento)
- **IMIG** - Informe Mensual de Ingresos y Gastos

Cobertura: **enero 2020 - abril 2026** (75 archivos Excel)

---

## Datasets en este repositorio

| Archivo | Descripcion | Registros |
|---|---|---|
| `output/aif_consolidado.csv` | AIF mensual/acumulado por subsector institucional | ~8.000 |
| `output/imig_consolidado.csv` | IMIG - detalle funcional de ingresos y gastos | ~650 |

### Columnas de aif_consolidado.csv

| Columna | Descripcion |
|---|---|
| `fecha` | Primer dia del mes (YYYY-MM-DD) |
| `periodo` | `mensual` o `acumulado` |
| `concepto_codigo` | Codigo normalizado (ej. `XIV_RESULTADO_PRIMARIO`) |
| `subsector` | Subsector institucional (ver tabla abajo) |
| `valor_millones_pesos` | En millones de ARS corrientes |

### Subsectores disponibles

| Codigo | Descripcion |
|---|---|
| `tesoro_nacional` | Tesoro Nacional |
| `rec_afectados` | Recursos Afectados |
| `org_descentralizados` | Organismos Descentralizados |
| `inst_seg_social` | Instituciones de Seguridad Social (ANSES) |
| `ex_cajas_prov` | Ex-Cajas Provinciales (hasta 2025) |
| `total_adm_nacional` | Total Administracion Nacional |
| `pami_fdos_otros` | PAMI + Fondos Fiduciarios y Otros |
| `total_general` | Total Sector Publico (desde 2026) |

### Principales conceptos normalizados

| Codigo | Descripcion |
|---|---|
| `I_INGRESOS_CORRIENTES` | Ingresos corrientes totales |
| `II_GASTOS_CORRIENTES` | Gastos corrientes totales |
| `II2_INTERESES` | Intereses de deuda |
| `II3_PRESTACIONES_SEG_SOCIAL` | Jubilaciones, pensiones y otros |
| `II4b1_TRANSF_PROVINCIAS_CABA` | Transferencias corrientes a provincias |
| `V2a_TRANSF_CAPITAL_PROVINCIAS` | Transferencias de capital a provincias |
| `XIV_RESULTADO_PRIMARIO` | Resultado primario (excluye intereses) |
| `XV_RESULTADO_FINANCIERO` | Resultado financiero (incluye intereses) |

---

## Uso rapido

```python
import pandas as pd

REPO = 'https://raw.githubusercontent.com/santiagoriverti/cuentas_publicas/main'
df = pd.read_csv(f'{REPO}/output/aif_consolidado.csv', parse_dates=['fecha'])

# Resultado primario mensual - Total Administracion Nacional
resultado = df[
    (df['concepto_codigo'] == 'XIV_RESULTADO_PRIMARIO') &
    (df['subsector'] == 'total_adm_nacional') &
    (df['periodo'] == 'mensual')
].set_index('fecha')['valor_millones_pesos']

print(resultado.tail(12))
```

---

## Como reproducir los datasets localmente

```bash
git clone https://github.com/santiagoriverti/cuentas_publicas.git
cd cuentas_publicas
pip install -r requirements.txt

# Copiar el ZIP de Hacienda a data/raw/
# cp /ruta/al/sector_publico.zip.zip data/raw/

python src/consolidate.py
```

---

## Estructura del repositorio

```
cuentas_publicas/
├── data/raw/                      # ZIP y Excel originales (gitignored)
├── output/
│   ├── aif_consolidado.csv        # Dataset AIF consolidado
│   └── imig_consolidado.csv       # Dataset IMIG consolidado
├── src/
│   ├── aif_parser.py              # Parser AIF
│   ├── imig_parser.py             # Parser IMIG
│   └── consolidate.py             # Script principal
├── notebooks/
│   ├── 01_consolidar.ipynb        # Carga datos + exporta Excel
│   └── 02_analisis_fiscal.ipynb   # Visualizaciones y analisis
├── .claude/memory/project.md      # Memoria del proyecto
└── requirements.txt
```

---

## Notas metodologicas

- Todos los valores en **millones de ARS corrientes** (no ajustados por inflacion)
- Desde 2026 los archivos AIF eliminan la columna EX-CAJAS PROVINCIALES; para series largas usar `total_adm_nacional`
- Los datos son "ejecucion provisoria" de Hacienda; pueden diferir levemente de publicaciones definitivas

---

Datos originales: Ministerio de Economia Argentina (dominio publico). Codigo: MIT License.
