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
| **03 - Indice Macroeconomico** | Indice mensual 2004-hoy (19 variables, 6 pilares) con rango de sensibilidad + 4 graficos + Excel de 8 hojas, en un ZIP ([nota metodologica](#indice-macroeconomico-notebook-03-nota-metodologica)) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/03_indice_macro.ipynb) |
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

## Indice Macroeconomico (notebook 03): nota metodologica

Indice mensual de la situacion macroeconomica argentina, **enero 2004 a hoy**. Un numero por mes, en desvios
respecto de lo tipico de la Argentina en ese periodo: **0 = tipico, positivo = mejor, negativo = peor**.
Serie publicada: [`output/indice_macro.csv`](output/indice_macro.csv) (indice, variantes, pilares y rango de
sensibilidad; se actualiza cada mes). Detalle de cada decision: [`CONTEXTO.md`](CONTEXTO.md) §4b.

### Como leerlo

- **Unidad: desvios (z).** Con distribucion normal, ±1 equivale a un desvio estandar: el 92% de los meses desde
  2004 esta entre −1 y +1. Maximo: +0,61 (dic-2006). Minimo: −1,50 (may-2020).
- **0 es "tipico argentino", no "bueno".** La vara es la historia argentina desde 2004 (inflacion mediana ~26%
  anual, deficit fiscal frecuente). Por eso tambien se publica `indice_ancla`, que mide el pilar Precios contra una
  meta de inflacion de 10% anual.
- **Rango de sensibilidad** (`banda_min` / `banda_max`, banda gris del grafico): el indice recalculado con 12
  variantes metodologicas razonables. **Si el rango cruza el 0, el signo del mes no es concluyente**: conviene
  leer la tendencia (el cambio en 12 meses), que suele ser robusta.
- **El ultimo mes es provisorio:** las series que se publican con rezago repiten su ultimo dato hasta 3 meses
  (hoja `Arrastrados` del Excel) y se reemplazan cuando sale el dato.

Ejemplo, agosto 2026: indice −0,01, rango −0,11 a +0,34 (signo no concluyente); hace 12 meses +0,23; cambio en
12 meses −0,24 (entre −0,35 y −0,13 segun la variante). Lectura: **cerca de lo tipico y en baja**.

### Pilares y variables (19)

| Pilar | Variables (signo: + = mas alto es mejor) | Fuentes |
|---|---|---|
| Actividad | EMAE desestacionalizado, var. i.a. (+) · EMAE vs su maximo de los 36 meses previos (+) · recaudacion real de IVA + impuesto al cheque, var. i.a. (+) | INDEC; Hacienda (IMIG) |
| Empleo e ingresos | asalariados privados registrados, var. i.a. (+) · salario real registrado, var. i.a. (+) · salario real vs su maximo de 36 meses (+) · desocupacion (−) | SIPA; INDEC |
| Precios | inflacion de 3 meses anualizada (−) · inflacion esperada a 12 meses (−) | INDEC (2007-2015: IPC Neuquen); REM del BCRA (2006-2016: encuesta UTDT) |
| Fiscal | resultado primario 12 meses / PIB (+) · intereses / ingresos 12 meses (−), ambos sin ingresos extraordinarios | Hacienda (IMIG; 2003-2015: AIF historica) + PIB INDEC |
| Externo | reservas netas en meses de importaciones (+) · saldo comercial 12 meses / PIB en dolares (+) · brecha CCL / oficial (−) · desalineamiento del tipo de cambio real (−) | BCRA; INDEC; argentinadatos; Ambito |
| Financiero | riesgo pais (−) · credito real en pesos al sector privado, var. i.a. (+) · credito / PIB (+) · distancia de la tasa real a 2% anual (−) | argentinadatos; BCRA |

Las variables de nivel (EMAE y salario contra su maximo previo) complementan a las de ritmo (var. i.a.): asi un
rebote post-crisis no cuenta como bonanza. El tipo de cambio real y la tasa real penalizan los dos extremos
(atraso y sobredevaluacion; tasas muy negativas y muy altas).

### Como se calcula

1. Cada variable se lleva a un z robusto: **z = signo × (valor − mediana) / (rango intercuartil / 1,349)**, con
   la mediana y el rango de **su propia historia** (sin los meses arrastrados), recortado a ±3.
2. **Pilar** = promedio de sus variables con dato. **Indice** = promedio simple de los pilares (pesos iguales,
   minimo 4 pilares: 5 en 2004 y 6 desde 2005). Se probo ponderar por componentes principales y se descarto:
   no hay un factor comun dominante.
3. **Por gestion:** promedio de los meses de cada gobierno (cada mes va a quien gobierno la mayor parte).

Decisiones de datos que importan (detalle en CONTEXTO.md §4b):

- **Inflacion 2007-2015** con el IPC de la provincia de Neuquen (el IPC del INDEC estaba intervenido);
  expectativas 2006-2016 con la encuesta de la UTDT, llevada al nivel del REM.
- **Reservas netas** = brutas − encajes − deuda del BCRA con organismos internacionales (FMI hasta 2006, BIS)
  − swap con China − REPO del BCRA − swap con el Tesoro de EEUU. No se restan SEDESA (~USD 2.000 M, sin serie
  publica), Bopreal ni la deuda del Tesoro (incluido el FMI).
- **Fiscal con el criterio actual de Hacienda en toda la serie:** 2003-2015 desde la AIF historica, sin
  utilidades del BCRA ni rentas que el FGS cobra al propio sector publico. Se excluyen ingresos extraordinarios:
  DEG del FMI (2009 y 2021), licitaciones de espectro 4G (2014) y 5G (2023), rentas por emision (2022) y
  recursos extraordinarios (2026).

### Que conclusiones son firmes

Analisis de sensibilidad con 33 variantes (`scripts/sensibilidad_indice.py`): pesos por variable, otra ventana de
normalizacion, sin tope o con otro tope, media y desvio, sin las variables de historia corta, y sacando cada pilar
y cada variable.

- **Firmes:** la forma historica (correlacion 0,90-1,00 entre variantes), los grandes episodios y la direccion
  del cambio reciente.
- **Por gestion:** A. Fernandez queda ultimo en todas las variantes. N. Kirchner, C. Fernandez y C. Fernandez II
  quedan por encima de Macri, Milei y A. Fernandez en todas (N. Kirchner vs Milei: 97% de las variantes).
- **No firmes:** el signo de un mes cercano a 0; el orden entre N. Kirchner y C. Fernandez II; el orden entre
  Macri y Milei.

| | N. Kirchner | C. Fernandez | C. Fernandez II | Macri | A. Fernandez | Milei (a ago-2026) |
|---|---|---|---|---|---|---|
| Promedio del indice | +0,04 | +0,17 | +0,06 | −0,30 | −0,79 | −0,28 |

### Validacion

- **Recesiones:** con la regla del Indice Lider de la UTDT (6 o mas caidas mensuales seguidas del EMAE
  tendencia-ciclo de INDEC) hay 7 recesiones entre 2008 y 2024. En todas el indice cae hasta un minimo en el
  valle o cerca: 2009 −0,33 · 2016 −0,46 · 2018 −0,87 · 2020 −1,50 · 2024 −1,29.
- **Indice de miseria** (inflacion + desocupacion): correlacion de Spearman −0,56.

### Limitaciones y advertencias

- **El promedio por gestion describe condiciones macroeconomicas, no evalua gobiernos:** no separa el contexto
  externo (precios de las materias primas, sequias, pandemia) ni las condiciones heredadas.
- Cada variable se mide contra su propia historia: las que empiezan mas tarde (recaudacion 2017, empleo
  registrado 2013, salario 2016) tienen otra vara. Ej.: el salario real cae casi sin pausa desde 2017, asi que
  estar 12% debajo de su pico es "tipico" dentro de esa ventana.
- Intereses / ingresos fue bajo en 2010-2015 en parte porque la deuda estaba en manos del propio sector publico
  y habia bonos en default sin pagar: eso favorece al pilar fiscal de esos anios.
- Reservas a fin de mes y sin SEDESA; rentas del FGS 2004-2014 repartidas con la proporcion de 2015-2016 (efecto
  acotado: ±0,3 puntos del PIB en el resultado primario).

### Actualizacion mensual y control de calidad

```bash
python scripts/actualizar_macro.py           # series externas -> data/reference/macro_mensual.csv
python scripts/run_notebooks_local.py 03     # corre el notebook 03 con los archivos locales
python scripts/control_calidad.py            # revisa datos e indice antes de publicar
python scripts/control_calidad.py --guardar  # sin ALERTAS: actualiza output/indice_macro.csv
python scripts/sensibilidad_indice.py        # (opcional) analisis de robustez completo
```

`control_calidad.py` compara las series con su ultima version publicada (git) y el indice con
`output/indice_macro.csv`. Sale con error si encuentra ALERTAS: datos de mas de 2 anios que cambiaron mas de 5%,
datos recientes que cambiaron mas de 25%, series que perdieron meses, saltos atipicos en los datos nuevos o
revisiones del indice ya publicado mayores a 0,10. Los avisos (rango que cruza el 0, revisiones chicas) son
informativos.

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
   Para el indice macro (notebook 03): `python scripts/actualizar_macro.py` (BCRA, INDEC, datos.gob.ar,
   argentinadatos, Ambito). Metodologia del indice: [`CONTEXTO.md`](CONTEXTO.md) §4b.
3. **Consolidar**:
   ```bash
   python src/consolidate.py
   ```
   Al final muestra la cobertura y los meses faltantes. Si Hacienda salteo un mes, el AIF se
   reconstruye solo desde los acumulados y el IMIG desde la hoja `Mensualizacion` (ver CONTEXTO.md).
4. **Indice macro:** ver [Actualizacion mensual y control de calidad](#actualizacion-mensual-y-control-de-calidad)
   (`actualizar_macro.py`, notebook 03, `control_calidad.py`).
5. **Verificar localmente** (opcional, recomendado):
   ```bash
   python scripts/run_notebooks_local.py
   ```
   Ejecuta los notebooks contra los archivos locales; salidas en `_local_run/`.
6. **Publicar**:
   ```bash
   git add data/raw data/reference output
   git commit -m "datos: YYYY-MM"
   git push
   ```
7. **Ejecutar los notebooks 02 y 03 en Colab**.

---

## Datasets

| Archivo | Descripcion | Registros |
|---|---|---|
| `output/aif_consolidado.csv` | AIF mensual/acumulado por subsector institucional | 30.414 |
| `output/imig_consolidado.csv` | IMIG, detalle funcional (una fuente por mes) | 4.931 |
| `data/reference/IPC.xlsx` | IPC INDEC nivel general + 12 divisiones, ene-2017 a ago-2026 | 116 meses |
| `output/indice_macro.csv` | Indice macro mensual: indice, sin fiscal, ancla, rango de sensibilidad y pilares | 272 meses (2004-hoy) |
| `data/reference/macro_mensual.csv` | Series externas del indice (BCRA, INDEC, datos.gob.ar, argentinadatos, Ambito) | 36 series, 2003-hoy |
| `data/reference/reservas_pasivos_manual.csv` | Pasivos del BCRA sin serie publica (swap China, REPO, swap EEUU), con fuente | por evento |

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
│   └── reference/
│       ├── IPC.xlsx                    <- IPC INDEC
│       ├── macro_mensual.csv           <- series del indice macro (actualizar_macro.py)
│       └── reservas_pasivos_manual.csv <- pasivos del BCRA cargados a mano, con fuente
├── output/
│   ├── aif_consolidado.csv  <- generados por consolidate.py
│   ├── imig_consolidado.csv
│   └── indice_macro.csv     <- indice macro publicado (control_calidad.py --guardar)
├── src/
│   ├── aif_parser.py        <- parser AIF (formatos 2020-2026)
│   ├── imig_parser.py       <- parser IMIG (hojas mensuales + Mensualizacion)
│   ├── consolidate.py       <- ZIP + sueltos -> CSV; deriva meses faltantes
│   └── deflate.py           <- helper de deflacion (standalone, no lo usan los NB)
├── scripts/
│   ├── actualizar_ipc.py        <- agrega meses nuevos del IPC (API datos.gob.ar)
│   ├── actualizar_macro.py      <- series externas del indice macro
│   ├── control_calidad.py       <- control mensual antes de publicar el indice
│   ├── sensibilidad_indice.py   <- robustez del indice (33 variantes) y validacion vs recesiones
│   └── run_notebooks_local.py   <- ejecuta los NB contra archivos locales
├── notebooks/
│   ├── 01_consolidar.ipynb
│   ├── 02_analisis_fiscal.ipynb
│   └── 03_indice_macro.ipynb
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
