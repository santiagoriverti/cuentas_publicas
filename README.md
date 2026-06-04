# Cuentas Publicas Argentina - Sector Publico Base Caja 2020-2026

Datos fiscales del Sector Publico Nacional (Secretaria de Hacienda) consolidados en un unico dataset tidy.

---

## Abrir en Google Colab

| Notebook | Descripcion | Link |
|---|---|---|
| **01 - Consolidacion** | Carga los datos desde GitHub y exporta un Excel unificado descargable | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb) |
| **02 - Analisis Fiscal** | Graficos de resultado primario, gasto, intereses, transferencias a provincias | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb) |

---

## Como agregar nuevos meses

Cuando Hacienda publique nuevos datos mensuales, seguir estos pasos:

### Paso 1 — Descargar el archivo Excel nuevo
Ir a: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica  
Descargar el archivo del mes correspondiente (ej. `sector_publico_base_caja_mayo_2026.xlsx`).

### Paso 2 — Copiar el archivo a la carpeta de datos crudos
```
C:\Users\sriverti\Desktop\INECO\Repositorios\cuentas_publicas\data\raw\
```
> Esta carpeta esta ignorada por git (los Excel no se suben a GitHub), pero el script la lee automaticamente.  
> El ZIP original `sector_publico.zip.zip` ya esta en esa carpeta con todos los meses anteriores.

### Paso 3 — Regenerar los datasets
Abrir una terminal en la carpeta del proyecto y ejecutar:
```bash
python src/consolidate.py
```
El script detecta automaticamente todos los archivos `.xls` y `.xlsx` en `data/raw/`,
los parsea y regenera `output/aif_consolidado.csv` e `output/imig_consolidado.csv`.

### Paso 4 — Publicar los datos actualizados en GitHub
```bash
git add output/aif_consolidado.csv output/imig_consolidado.csv
git commit -m "datos: agregar mes YYYY-MM"
git push
```

### Paso 5 — Abrir el Notebook 01 en Colab
El notebook lee los CSVs directamente desde GitHub, por lo que al ejecutarlo
ya incluye los nuevos datos sin ninguna configuracion adicional.

---

## Fuente de datos

**Secretaria de Hacienda - Ministerio de Economia**  
https://www.argentina.gob.ar/economia/sechacienda/infoestadistica

- **AIF** - Sector Publico Base Caja (Esquema Ahorro-Inversion-Financiamiento)
- **IMIG** - Informe Mensual de Ingresos y Gastos

Cobertura actual: **enero 2020 - abril 2026** (75 archivos Excel)

---

## Datasets en este repositorio

| Archivo | Descripcion | Registros |
|---|---|---|
| `output/aif_consolidado.csv` | AIF mensual/acumulado por subsector institucional | ~26.700 |
| `output/imig_consolidado.csv` | IMIG - detalle funcional de ingresos y gastos | ~6.800 |

### Hojas del Excel exportado por el Notebook 01

| Hoja | Descripcion |
|---|---|
| `AIF_mensual` | Todos los conceptos x subsector, periodicidad mensual |
| `AIF_acumulado` | Idem, acumulado anual |
| `Resultado_pivot` | KPIs en columnas: ingresos, gastos, intereses, resultado primario y financiero |
| `Transferencias_provincias` | Transferencias corrientes Y de capital a Provincias/CABA por subsector |
| `IMIG` | Detalle funcional: prestaciones sociales, subsidios, salarios, etc. |

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
| `I1_INGRESOS_TRIBUTARIOS` | Ingresos tributarios |
| `I2_APORTES_SEG_SOCIAL` | Aportes y contribuciones a la seguridad social |
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

# Resultado primario mensual - Total Administracion Nacional
resultado = df[
    (df['concepto_codigo'] == 'XIV_RESULTADO_PRIMARIO') &
    (df['subsector'] == 'total_adm_nacional') &
    (df['periodo'] == 'mensual')
].set_index('fecha')['valor_millones_pesos']

print(resultado.tail(12))
```

---

## Estructura del repositorio

```
cuentas_publicas/
├── data/
│   └── raw/                       <- AGREGAR AQUI los nuevos Excel de Hacienda
│       └── sector_publico.zip.zip    (ZIP con todos los meses 2020-abr2026)
├── output/
│   ├── aif_consolidado.csv        <- Dataset AIF (se regenera con consolidate.py)
│   └── imig_consolidado.csv       <- Dataset IMIG (se regenera con consolidate.py)
├── src/
│   ├── aif_parser.py              <- Parser AIF (deteccion automatica de formato)
│   ├── imig_parser.py             <- Parser IMIG
│   └── consolidate.py             <- Script principal: lee data/raw/ -> output/
├── notebooks/
│   ├── 01_consolidar.ipynb        <- Exporta Excel unificado desde GitHub
│   └── 02_analisis_fiscal.ipynb   <- Visualizaciones y analisis
└── requirements.txt
```

---

## Notas metodologicas

- Todos los valores en **millones de ARS corrientes** (no ajustados por inflacion)
- Los datos son "ejecucion provisoria" de Hacienda; pueden diferir de publicaciones definitivas
- Desde 2026 los archivos AIF eliminan la columna EX-CAJAS PROVINCIALES; para series largas usar `subsector = total_adm_nacional`
- El script `consolidate.py` es idempotente: puede ejecutarse multiples veces, siempre sobreescribe los CSVs con los datos mas actualizados

---

Datos originales: Ministerio de Economia Argentina (dominio publico). Codigo: MIT License.
