# Cuentas Publicas Argentina - Sector Publico Base Caja 2020-2026

Datos fiscales del Sector Publico Nacional (Secretaria de Hacienda) consolidados en un unico dataset tidy.

---

## Abrir en Google Colab

| Notebook | Descripcion | Link |
|---|---|---|
| **01 - Consolidacion** | Carga los datos desde GitHub y exporta un Excel unificado descargable | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb) |
| **02 - Analisis Fiscal** | Graficos en pesos constantes + Excel y ZIP descargables | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb) |

---

## Fuente de datos

**Secretaria de Hacienda - Ministerio de Economia**
https://www.argentina.gob.ar/economia/sechacienda/infoestadistica

- **AIF** - Sector Publico Base Caja (Esquema Ahorro-Inversion-Financiamiento)
- **IMIG** - Informe Mensual de Ingresos y Gastos

Cobertura actual: **enero 2020 - abril 2026** (78 archivos Excel procesados)

---

## Como agregar nuevos meses

Cuando Hacienda publique nuevos datos mensuales:

### Paso 1 — Descargar el nuevo Excel
Ir a: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica
Descargar el archivo del mes (ej. `sector_publico_base_caja_mayo_2026.xlsx`).

### Paso 2 — Copiarlo a la carpeta de datos
```
C:\...\cuentas_publicas\data\raw\
```
El script detecta automaticamente archivos Excel sueltos en esa carpeta, ademas del ZIP original.

### Paso 3 — Regenerar los datasets
```bash
python src/consolidate.py
```
El script muestra al final los meses faltantes detectados automaticamente.

### Paso 4 — Publicar en GitHub
```bash
git add output/aif_consolidado.csv output/imig_consolidado.csv
git commit -m "datos: YYYY-MM"
git push
```

### Paso 5 — Ejecutar en Colab
Los notebooks leen los CSVs directamente de GitHub — no requieren subir archivos.

---

## Datasets en este repositorio

| Archivo | Descripcion | Registros |
|---|---|---|
| `output/aif_consolidado.csv` | AIF mensual/acumulado por subsector institucional | 27.964 |
| `output/imig_consolidado.csv` | IMIG - detalle funcional de ingresos y gastos | 7.950 |
| `data/reference/IPC.xlsx` | IPC Nivel General INDEC (ene-2017 a abr-2026) | - |

**Unico mes sin datos AIF mensual:** Jun-2022 (Hacienda solo publico el acumulado del I Semestre).

### Columnas de aif_consolidado.csv

| Columna | Descripcion |
|---|---|
| `fecha` | Primer dia del mes (YYYY-MM-DD) |
| `periodo` | `mensual` o `acumulado` |
| `concepto_codigo` | Codigo normalizado (ej. `XIV_RESULTADO_PRIMARIO`) |
| `concepto_nivel` | `principal` / `detalle` / `subdetalle` / `micro` |
| `subsector` | Subsector institucional (ver tabla abajo) |
| `valor_millones_pesos` | En millones de ARS corrientes |

### Subsectores

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

### Principales conceptos

| Codigo | Descripcion |
|---|---|
| `I_INGRESOS_CORRIENTES` | Ingresos corrientes totales |
| `II_GASTOS_CORRIENTES` | Gastos corrientes totales |
| `II2_INTERESES` | Intereses de deuda |
| `II3_PRESTACIONES_SEG_SOCIAL` | Jubilaciones, pensiones y prestaciones |
| `II4b1_TRANSF_PROVINCIAS_CABA` | Transferencias corrientes a provincias y CABA |
| `V2a_TRANSF_CAPITAL_PROVINCIAS` | Transferencias de capital a provincias y CABA |
| `XIV_RESULTADO_PRIMARIO` | Resultado primario (excluye intereses) |
| `XV_RESULTADO_FINANCIERO` | Resultado financiero (incluye intereses) |

---

## Uso rapido desde Python

```python
import pandas as pd

REPO = 'https://raw.githubusercontent.com/santiagoriverti/cuentas_publicas/main'
df = pd.read_csv(f'{REPO}/output/aif_consolidado.csv', parse_dates=['fecha'])

# Resultado primario mensual - Sector Publico Total
for ss in ['total_adm_nacional', 'pami_fdos_otros']:
    s = df[(df['concepto_codigo']=='XIV_RESULTADO_PRIMARIO') &
           (df['subsector']==ss) & (df['periodo']=='mensual')]
    # sumar ambos subsectores para obtener el total del sector publico
```

---

## Estructura del repositorio

```
cuentas_publicas/
├── data/
│   ├── raw/           <- Agregar nuevos Excel de Hacienda aqui (gitignored)
│   │   └── sector_publico.zip.zip   (ZIP con todos los meses 2020-abr2026)
│   └── reference/
│       └── IPC.xlsx   <- IPC INDEC (commiteado)
├── output/
│   ├── aif_consolidado.csv     <- Se regenera con consolidate.py
│   └── imig_consolidado.csv
├── src/
│   ├── aif_parser.py       <- Parser AIF (deteccion automatica de formato por año)
│   ├── imig_parser.py      <- Parser IMIG (incluye formato multi-columna semestral)
│   └── consolidate.py      <- Lee ZIP + archivos sueltos en data/raw/ -> output/
├── notebooks/
│   ├── 01_consolidar.ipynb     <- Exporta Excel unificado
│   └── 02_analisis_fiscal.ipynb <- Graficos pesos constantes + ZIP descargable
└── requirements.txt
```

---

## Notas metodologicas

- Todos los valores en **millones de ARS corrientes** (no ajustados por inflacion)
- Deflactor para series reales: IPC Nivel General INDEC, base abril 2026
- Los titulares usan *Sector Publico Total* = Adm. Nacional + PAMI + Fondos Fiduciarios
- Desde 2026 los archivos AIF eliminan la columna EX-CAJAS; usar `total_adm_nacional` para series largas
- Los datos son "ejecucion provisoria"; pueden diferir levemente de publicaciones definitivas
- **Validado contra Hacienda oficial:** 2024 y 2025 con 0% de diferencia en resultado primario y financiero

---

Datos originales: Ministerio de Economia Argentina (dominio publico). Codigo: MIT License.
