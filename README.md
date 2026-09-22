# Cuentas Publicas Argentina - Sector Publico Base Caja 2020-2026

Datos fiscales del Sector Publico Nacional (Secretaria de Hacienda) consolidados en un dataset
tidy, con graficos y un Excel de resultados en pesos constantes.

**Cobertura actual: enero 2020 - agosto 2026** | Deflactor: IPC INDEC, base agosto 2026

> Para retomar el trabajo (humanos o Claude): leer primero [`ESTADO.md`](ESTADO.md).
> Metodologia y decisiones de calculo: [`CONTEXTO.md`](CONTEXTO.md).

---

## Abrir en Google Colab

| Notebook | Descripcion | Link |
|---|---|---|
| **02 - Analisis Fiscal** (principal) | 7 graficos en pesos constantes + Excel con resultados y datos consolidados, todo en un ZIP descargable | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb) |
| 01 - Consolidacion (opcional) | Exporta solo los datos consolidados a un Excel (ya incluidos en el Excel del 02) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb) |

Los notebooks son independientes: leen los CSV e `IPC.xlsx` directamente desde GitHub.
Para obtener resultados basta con abrir el **02** y ejecutar todo (Entorno de ejecucion -> Ejecutar todas).

### Que descarga el notebook 02 (`analisis_fiscal.zip`)

- 7 graficos PNG: resultado primario/financiero mensual, composicion del gasto, composicion de
  ingresos, transferencias a provincias, ajuste por componente AIF, torta y barras del recorte por rubro (IMIG).
- `analisis_fiscal_resultados.xlsx` con 11 hojas:

| Hoja | Contenido |
|---|---|
| `Leeme` | Base del deflactor, cobertura, meses faltantes/derivados, unidades |
| `Serie_mensual` / `Resumen_anual` | Sector Publico Total, nominal y real |
| `Transferencias_prov` | Transferencias corrientes y de capital a provincias |
| `Ajuste_AIF_anual` / `Ajuste_IMIG_rubros` | Comparacion 2023 vs 2024 y 2025 (pesos constantes) |
| `Informe_tabla1` / `Informe_provincias` | Tablas resumen anuales (billones constantes y % PIB) |
| `AIF_mensual` / `AIF_acumulado` / `IMIG` | Datos consolidados completos (nominales) |

---

## Fuente de datos

**Secretaria de Hacienda - Ministerio de Economia**
https://www.argentina.gob.ar/economia/sechacienda/infoestadistica

- **AIF** - Sector Publico Base Caja (esquema Ahorro-Inversion-Financiamiento)
- **IMIG** - Informe Mensual de Ingresos y Gastos (clasificacion funcional)
- **IPC** - INDEC, Nivel General nacional (dic-2016 = 100)

Los Excel originales estan versionados en `data/raw/` (84 archivos: ZIP historico + meses sueltos),
asi que el repo es autocontenido: se puede regenerar todo en cualquier PC.

---

## Instalacion local

```bash
git clone https://github.com/santiagoriverti/cuentas_publicas.git
cd cuentas_publicas
pip install -r requirements.txt
```

En Windows conviene definir `PYTHONUTF8=1` (algunos prints usan caracteres unicode).

---

## Como agregar nuevos meses

1. **Descargar** de la web de Hacienda los Excel del mes (AIF y, si viene aparte, IMIG) y
   copiarlos a `data/raw/` (sin renombrar).
2. **Actualizar el IPC**:
   ```bash
   python scripts/actualizar_ipc.py
   ```
   Agrega los meses nuevos del Nivel General desde la API de datos.gob.ar. Opcional:
   `--divisiones RUTA/IPC.xlsx` para completar tambien las divisiones.
3. **Consolidar**:
   ```bash
   python src/consolidate.py
   ```
   Al final muestra la cobertura y los meses faltantes. Si Hacienda salteo un mes, el AIF se
   reconstruye solo desde los acumulados y el IMIG desde la hoja `Mensualizacion` (ver CONTEXTO.md).
4. **Verificar localmente** (opcional, recomendado):
   ```bash
   python scripts/run_notebooks_local.py
   ```
   Ejecuta ambos notebooks contra los archivos locales; salidas en `_local_run/`.
5. **Publicar**:
   ```bash
   git add data/raw data/reference output
   git commit -m "datos: YYYY-MM"
   git push
   ```
6. **Ejecutar el notebook 02 en Colab**.

---

## Datasets

| Archivo | Descripcion | Registros |
|---|---|---|
| `output/aif_consolidado.csv` | AIF mensual/acumulado por subsector institucional | 30.414 |
| `output/imig_consolidado.csv` | IMIG, detalle funcional (una fuente por mes) | 4.931 |
| `data/reference/IPC.xlsx` | IPC INDEC nivel general + 12 divisiones, ene-2017 a ago-2026 | 116 meses |

- **Unico mes sin AIF mensual:** jun-2022 (Hacienda solo publico el acumulado del I semestre).
- **Jul-2026:** Hacienda no lo publico. AIF derivado de acumulados; IMIG desde la hoja `Mensualizacion`
  (`fuente_archivo` lo indica: `derivado: ...` / `... [Mensualizacion]`).

### Columnas de aif_consolidado.csv

| Columna | Descripcion |
|---|---|
| `fecha` | Primer dia del mes (YYYY-MM-DD) |
| `periodo` | `mensual` o `acumulado` |
| `concepto_codigo` | Codigo normalizado (ej. `XIV_RESULTADO_PRIMARIO`) |
| `concepto_nivel` | `principal` / `detalle` / `subdetalle` / `micro` |
| `subsector` | Subsector institucional (ver tabla) |
| `valor_millones_pesos` | Millones de ARS corrientes |
| `fuente_archivo` | Excel de origen (o `derivado: ...` si se reconstruyo) |

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
| `I_INGRESOS_CORRIENTES` | Ingresos corrientes (antes de figurativas) |
| `XI_INGRESOS_DESPUES_FIGURAT` | Ingresos totales (despues de figurativas) |
| `XII_GASTOS_PRIMARIOS_DESPUES_FIGURAT` | Gasto primario |
| `II_GASTOS_CORRIENTES` | Gastos corrientes |
| `II2_INTERESES` | Intereses de deuda |
| `II3_PRESTACIONES_SEG_SOCIAL` | Jubilaciones, pensiones y prestaciones |
| `II4b1_TRANSF_PROVINCIAS_CABA` | Transferencias corrientes a provincias y CABA |
| `V2a_TRANSF_CAPITAL_PROVINCIAS` | Transferencias de capital a provincias y CABA |
| `XIV_RESULTADO_PRIMARIO` | Resultado primario (= XI - XII) |
| `XV_RESULTADO_FINANCIERO` | Resultado financiero (= primario - intereses) |

---

## Uso rapido desde Python

```python
import pandas as pd

REPO = 'https://raw.githubusercontent.com/santiagoriverti/cuentas_publicas/main'
df = pd.read_csv(f'{REPO}/output/aif_consolidado.csv', parse_dates=['fecha'])

# Resultado primario mensual - Sector Publico Total (Adm. Nacional + PAMI/Fondos)
m = df[(df.concepto_codigo == 'XIV_RESULTADO_PRIMARIO') & (df.periodo == 'mensual')]
total = (m[m.subsector.isin(['total_adm_nacional', 'pami_fdos_otros'])]
         .groupby('fecha').valor_millones_pesos.sum())
# Desde 2026 existe el subsector total_general: usarlo directamente para esos meses.
```

---

## Estructura del repositorio

```
cuentas_publicas/
├── README.md / ESTADO.md / CONTEXTO.md / CLAUDE.md
├── data/
│   ├── raw/                 <- Excel originales de Hacienda (versionados)
│   │   ├── sector_publico.zip     (80 archivos, ene-2020 a may-2026)
│   │   └── *.xlsx / *.xls         (meses sueltos posteriores al ZIP)
│   └── reference/IPC.xlsx   <- IPC INDEC
├── output/
│   ├── aif_consolidado.csv  <- generados por consolidate.py
│   └── imig_consolidado.csv
├── src/
│   ├── aif_parser.py        <- parser AIF (formatos 2020-2026)
│   ├── imig_parser.py       <- parser IMIG (hojas mensuales + Mensualizacion)
│   ├── consolidate.py       <- ZIP + sueltos -> CSV; deriva meses faltantes
│   └── deflate.py           <- helper de deflacion (standalone, no lo usan los NB)
├── scripts/
│   ├── actualizar_ipc.py        <- agrega meses nuevos del IPC (API datos.gob.ar)
│   └── run_notebooks_local.py   <- ejecuta los NB contra archivos locales
├── notebooks/
│   ├── 01_consolidar.ipynb
│   └── 02_analisis_fiscal.ipynb
└── requirements.txt
```

---

## Notas metodologicas (resumen)

- CSV en **millones de ARS corrientes**. Los notebooks deflactan con IPC Nivel General; la base
  es siempre el **ultimo mes disponible del IPC** (hoy agosto 2026).
- Titulares: *Sector Publico Total* = Adm. Nacional + PAMI + Fondos Fiduciarios.
- Comparacion del ajuste: anos completos 2023 vs 2024 y 2025.
- **Validado contra Hacienda:** resultado primario y financiero 2024 y 2025 con 0% de diferencia.
- Detalle completo en [`CONTEXTO.md`](CONTEXTO.md).

---

Datos originales: Ministerio de Economia Argentina (dominio publico). Codigo: MIT License.
