# Cuentas Publicas Argentina - Sector Publico Base Caja 2020-2026

Datos fiscales del Sector Publico Nacional (Secretaria de Hacienda) consolidados en un unico dataset tidy.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_analisis_fiscal.ipynb)

---

## Fuente de datos

**Secretaria de Hacienda - Ministerio de Economia**  
https://www.argentina.gob.ar/economia/sechacienda/infoestadistica

Archivos incluidos:
- **AIF** - Sector Publico Base Caja (Esquema Ahorro-Inversion-Financiamiento)
- **IMIG** - Informe Mensual de Ingresos y Gastos

Cobertura: **enero 2020 - abril 2026** (75 archivos Excel, ~8.000 registros AIF)

---

## Datasets generados

| Archivo | Descripcion | Filas |
|---|---|---|
| `output/aif_consolidado.csv` | AIF mensual/acumulado por subsector | ~8.000 |
| `output/imig_consolidado.csv` | IMIG funcional de ingresos y gastos | ~650 |

### Estructura AIF (`aif_consolidado.csv`)

| Columna | Descripcion |
|---|---|
| `fecha` | Primer dia del mes (YYYY-MM-DD) |
| `anio` / `mes` | Año y mes numerico |
| `periodo` | `mensual` o `acumulado` |
| `concepto_codigo` | Codigo normalizado (ej. `XIV_RESULTADO_PRIMARIO`) |
| `concepto_descripcion` | Texto original del Excel |
| `concepto_nivel` | `principal` / `detalle` / `subdetalle` |
| `subsector` | Subsector institucional (ver abajo) |
| `valor_millones_pesos` | En millones de ARS corrientes |
| `fuente_archivo` | Nombre del archivo Excel de origen |

**Subsectores:**

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

**Principales conceptos normalizados:**

| Codigo | Descripcion |
|---|---|
| `I_INGRESOS_CORRIENTES` | Ingresos corrientes totales |
| `II_GASTOS_CORRIENTES` | Gastos corrientes totales |
| `II2_INTERESES` | Intereses de deuda |
| `II3_PRESTACIONES_SEG_SOCIAL` | Jubilaciones, pensiones y otros |
| `II4b1_TRANSF_PROVINCIAS_CABA` | Transferencias corrientes a provincias |
| `V2a_TRANSF_CAPITAL_PROVINCIAS` | Transferencias de capital a provincias |
| `XIV_RESULTADO_PRIMARIO` | Resultado primario (antes de intereses) |
| `XV_RESULTADO_FINANCIERO` | Resultado financiero (despues de intereses) |

---

## Uso rapido

```python
import pandas as pd

df = pd.read_csv('output/aif_consolidado.csv', parse_dates=['fecha'])

# Resultado primario mensual - Total Administracion Nacional
resultado = df[
    (df['concepto_codigo'] == 'XIV_RESULTADO_PRIMARIO') &
    (df['subsector'] == 'total_adm_nacional') &
    (df['periodo'] == 'mensual')
].set_index('fecha')['valor_millones_pesos']

print(resultado.tail(12))
```

---

## Como reproducir el dataset

```bash
git clone https://github.com/santiagoriverti/cuentas_publicas.git
cd cuentas_publicas
pip install -r requirements.txt

# Copiar el ZIP original a data/raw/
# cp /ruta/al/sector_publico.zip.zip data/raw/

python src/consolidate.py
```

Los CSVs se generan en `output/`.

---

## Estructura del repositorio

```
cuentas_publicas/
├── data/
│   └── raw/              # Excel originales (no versionados en git)
├── output/
│   ├── aif_consolidado.csv
│   └── imig_consolidado.csv
├── src/
│   ├── aif_parser.py     # Parser AIF (Esquema Ahorro-Inversion-Financiamiento)
│   ├── imig_parser.py    # Parser IMIG (Informe Mensual Ingresos y Gastos)
│   └── consolidate.py    # Script principal de consolidacion
├── notebooks/
│   └── 01_analisis_fiscal.ipynb
├── .claude/
│   └── memory/
│       └── project.md    # Memoria del proyecto para continuacion
├── requirements.txt
└── README.md
```

---

## Notas metodologicas

- **Pesos corrientes:** todos los valores en millones de ARS corrientes (no ajustados por inflacion)
- **Cambio estructural 2026:** desde enero 2026, los archivos AIF eliminan la columna "EX-CAJAS PROVINCIALES" y añaden una columna "T O T A L" que consolida administracion nacional + PAMI/fondos. Para series largas, usar `total_adm_nacional`.
- **Provisorio vs. definitivo:** los datos de Hacienda son "ejecucion provisoria"; pueden diferir levemente de publicaciones definitivas.
- **Cobertura geografica:** los datos AIF son nacionales. No incluyen datos provinciales desagregados por jurisdiccion (para eso ver MECON/series provinciales).

---

## Licencia

Datos originales: Ministerio de Economia Argentina (dominio publico).  
Codigo de procesamiento: MIT License.
