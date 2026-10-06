# CONTEXTO Y METODOLOGIA — cuentas_publicas

Decisiones de calculo y conocimiento del dominio que no son obvias leyendo el codigo.
Si algo aca contradice al codigo, manda el codigo; actualizar este archivo.

## 1. Objetivo

Medir el ajuste fiscal del Sector Publico Nacional argentino (gestion Milei, desde dic-2023):
resultado primario y financiero, composicion del gasto e ingresos, transferencias a provincias y
recorte por rubro funcional, en pesos constantes.

## 2. Fuentes

| Fuente | Que aporta | Donde |
|---|---|---|
| **AIF** (Hacienda, Sector Publico Base Caja) | Esquema Ahorro-Inversion-Financiamiento por subsector institucional; hojas mensual y acumulado | `data/raw/` |
| **IMIG** (Hacienda, Informe Mensual de Ingresos y Gastos) | Clasificacion funcional/por rubro (jubilaciones, AUH, obra publica, subsidios energia/transporte...) | `data/raw/` (hoja IMIG del mismo Excel o archivo aparte) |
| **IPC INDEC** | Deflactor: Nivel General nacional, dic-2016 = 100 | `data/reference/IPC.xlsx` |

Web de Hacienda: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica
IPC por API: serie `148.3_INIVELNAL_DICI_M_26` en https://apis.datos.gob.ar/series/api/

Formatos que fue cambiando Hacienda (el parser los maneja todos):
- 2020-2025: un Excel por mes con hojas AIF + IMIG (`.xls` hasta 2023, luego `.xlsx`).
- 2026: el AIF viene como `<Mes> 26.xlsx` (hojas `<Mes>` y `Acumulado`) y el IMIG en archivo aparte
  `IMIG <Mes> 2026.xlsx` (hojas `<Mes>` y `Mensualizacion`). Enero/febrero 2026 siguieron el formato viejo.
- Desde 2026 desaparece la columna Ex-Cajas y aparece `total_general`.
- jun-2022: archivo con 6 meses en columnas (solo acumulado semestral para el AIF).

## 3. Pipeline

```
data/raw/ (ZIP + sueltos) --src/consolidate.py--> output/aif_consolidado.csv
                                                 output/imig_consolidado.csv
                                  + data/reference/IPC.xlsx
                                        |
                        notebooks (leen de GitHub) --> graficos + Excel
```

`consolidate.py`:
1. Lee todos los Excel del ZIP y los sueltos de `data/raw/` que no esten en el ZIP (autodetecta
   `sector_publico*.zip`, toma el mas grande; ignora `IPC.xlsx` y `data/raw/_duplicados/`).
2. Parsea AIF (`aif_parser.py`) e IMIG (`imig_parser.py`, incluida la hoja `Mensualizacion`).
3. **AIF**: deduplica y **deriva meses mensuales faltantes** desde los acumulados:
   - `mens(M) = acum(M) - acum(M-1)`, o si falta `acum(M)`:
   - `mens(M) = acum(M+1) - acum(M-1) - mens(M+1)`
   - Validado: diferencia 0,0 M$ en 350 concepto x subsector contra abr/may/jun-2026 publicados.
   - Registros marcados `fuente_archivo = "derivado: ..."`. Caso actual: **jul-2026**.
4. **IMIG**: **una sola fuente por mes**, por prioridad:
   0. publicacion original (el mes mas reciente de su archivo);
   1. hoja `Mensualizacion` (IMIG 2026+: una columna por mes del ano; validada exacta vs hojas mensuales)
      → cubre **mar-2026 y jul-2026**, que Hacienda no publico como informe propio;
   2. columna comparativa de otro archivo (unica fuente para 2019).
   Motivo: los archivos del ano siguiente traen el mismo mes del ano anterior con valores
   **revisados y reclasificados** (ej. Salud abr-2025: 6.260 M$ revisado vs 66.920 M$ original).
   Mezclar versiones generaba totales anuales inconsistentes. Se usa siempre la original.
5. Imprime cobertura y meses faltantes.

## 4. Definiciones usadas en los notebooks

- **Sector Publico Total** = `total_adm_nacional` + `pami_fdos_otros`; donde existe `total_general`
  (2026) se usa ese valor (funcion `get_serie_total`).
- **Resultado primario** = `XIV_RESULTADO_PRIMARIO` = Ingresos totales (XI) − Gasto primario (XII).
- **Ingresos totales** = `XI_INGRESOS_DESPUES_FIGURAT`; **gasto primario** =
  `XII_GASTOS_PRIMARIOS_DESPUES_FIGURAT`. Ambos "despues de figurativas", por eso restan exacto al
  primario. `I_INGRESOS_CORRIENTES` (antes de figurativas, sin recursos de capital) se muestra solo
  como dato informativo: NO restarlo contra el gasto primario.
- **Deflactor**: `valor_real = valor_nominal * IPC_base / IPC_mes`, con base = ultimo mes del IPC
  (automatico: al agregar un mes de IPC cambia la base de TODOS los valores reales; los % no cambian).
- **Comparacion del ajuste**: anos completos 2023 vs 2024 y 2023 vs 2025 (`ANO_BASE`, `ANO_1`,
  `ANO_2` en celda 1 del NB02). No usar dic-2023 vs ultimo mes: diciembre tiene aguinaldo y los
  meses de cupon (enero/julio) inflan intereses.
- **Desglose AIF por componente** (grafico 05): subsector `total_adm_nacional`.
- **Transferencias a provincias** (grafico 04): subsector `tesoro_nacional`, corrientes
  (`II4b1_TRANSF_PROVINCIAS_CABA`) + capital (`V2a_TRANSF_CAPITAL_PROVINCIAS`). En `Informe_provincias`
  se usa `total_adm_nacional`; totales y % se calculan sin redondear y se redondea al final.
- **Rubros IMIG** (graficos 06/07): `Gastos_capital` = obra publica, `Subsidios_economicos`,
  `Transf_corrientes_provincias`, `Salarios`, `Jubilaciones_pensiones`, `Transf_universidades`,
  `Pensiones_no_contributivas`, `INSSJP_PAMI`, `Otros_prog_sociales`, `AUH` (nivel de jerarquia en
  la lista `rubros` de la celda 8).
- **% PIB**: PIB nominal INDEC hardcodeado en la celda 9 del NB02 (`PIB_B`, billones: 2020 27,2 ·
  2021 46,2 · 2022 82,8 · 2023 193,9 · 2024 584,4 · 2025 850,2). Fuente: serie `166.2_PPIB_0_0_3`
  de datos.gob.ar, que viene **trimestral anualizada** → anual = suma de los 4 trimestres / 4
  (sumarlos sin dividir da 4 veces el PIB). Hasta oct-2026 habia valores aproximados erroneos
  (2023 = 143,2). 2026 = n/d hasta que INDEC lo publique.

## 4b. Indice Macroeconomico (notebook 03)

### Datos
- `scripts/actualizar_macro.py` → `data/reference/macro_mensual.csv` (25 series crudas, mensuales).
  Diarios → promedio del mes (reservas: ultimo dato del mes); trimestrales → mismo valor en los 3
  meses. Si una API falla, conserva la columna anterior e imprime "FALLO".
- Fuentes: datos.gob.ar (EMAE, SIPA, salarios, desocupacion EPH [la API da fraccion → se guarda en
  %], expo/impo, PIB nominal, IPC Neuquen, UTDT promedio, CSV IMIG mensual 2016+), BCRA API v4
  (`verify=False`; reservas, A3500, BADLAR, prestamos totales var 26 y en pesos var 117, REM var 29,
  inflacion var 27), BCRA ITCRMSerie.xlsx (columna "ITCRM " con espacio), argentinadatos (riesgo
  pais, CCL), Ambito (blue con centavos, `/dolar/informal/historico-general/dd-mm-aaaa/dd-mm-aaaa`).
- Del repo: IPC (`IPC.xlsx`) e IMIG (`output/imig_consolidado.csv`). La IMIG se completa 2016-2018
  con el CSV de datos.gob.ar (distribucion 452.3; coincide 0,00% con la del repo en 2019-2026).
  OJO: los IDs `452.2_*` de la API son trimestrales y `452.1_*` anuales.

### Variables (17) y pilares (celda 3 del NB03; hoja `Metodologia`)
| Pilar | Variable | Signo | Nota |
|---|---|---|---|
| Actividad | `emae_ia` EMAE desest. var. i.a. | + | |
| Actividad | `recaudacion_ia` IVA + Deb./Cred. reales, trim. movil, var. i.a. | + | repo IMIG, desde 2017-03 |
| Empleo | `sipa_ia` asalariados privados registrados var. i.a. | + | desde 2013 |
| Empleo | `salario_real_ia` indice de salarios registrados / IPC, var. i.a. | + | desde 2016-10 |
| Empleo | `desocupacion` | − | trimestral |
| Precios | `inflacion_3m` 400·ln(IPC/IPC₋₃) | − | log |
| Precios | `inflacion_esperada` 100·ln(1+exp) | − | log |
| Fiscal | `primario_pib` primario 12 m sin extraordinarios / PIB 12 m | + | desde dic-2016 |
| Fiscal | `intereses_ingresos` intereses netos / ingresos sin extraordinarios, 12 m | − | desde dic-2016 |
| Externo | `reservas_meses_impo` reservas brutas / importaciones mensuales promedio 12 m | + | |
| Externo | `saldo_comercial` expo − impo 12 m (MM USD) | + | |
| Externo | `brecha` CCL / A3500 − 1 | − | 0 antes de nov-2011 |
| Externo | `tcrm_desalineado` \|ln(ITCRM / mediana)\| | − | simetrico |
| Financiero | `riesgo_pais` | − | |
| Financiero | `credito_real_ia` prestamos EN PESOS / IPC, var. i.a. | + | var 117 |
| Financiero | `credito_pib` prestamos totales ($ + USD) / PIB 12 m | + | var 26 |
| Financiero | `tasa_real_desvio` \|tasa real ex-ante − 2%\| (BADLAR efectiva vs expectativas) | − | |

### Empalmes y correcciones de datos (revisados en dos auditorias, oct-2026)
- **Inflacion**: INDEC 2017+; serie BCRA 2016 (ene-abr completado por el BCRA) y antes de 2007;
  **IPC Neuquen 2007-01 a 2015-12** (la serie del BCRA repite el IPC intervenido: 2010 10,5% vs
  Neuquen 26,7%; 2013 10,7% vs 28,3%). Inflacion oficial 2018-2024 verificada (±0,2 pp).
- **Expectativas**: REM jun-2016+; **ago-2006 a may-2016 UTDT promedio** llevado al nivel del REM
  restando la diferencia mediana en log de la superposicion (≈ 5,4 pts; se calcula en el notebook).
  La mediana UTDT viene redondeada a 5 pp (descartada); la serie BCRA 2007-2012 seguia al IPC
  oficial (~11%) y tiene hueco 2012-10 a 2016-05.
- **Brecha**: CCL 2013+; **nov-2011 a dic-2012 dolar blue de Ambito** (con centavos; corr. 0,98 con
  el CCL). argentinadatos y bluelytics traen el blue 2011-2012 redondeado a $1 (descartados).
- **Fiscal sin ingresos extraordinarios**: se restan del primario y de los ingresos: rentas por
  emision primaria sobre el limite del PFE (may-dic 2022), "Recursos extraordinarios (*)" (2026),
  licitacion 5G (dic-2023, 0) — son partidas informativas ya incluidas en los totales de la IMIG — y
  el **DEG del FMI de sep-2021**, que no tiene linea propia: exceso de "Transferencias corrientes"
  (nivel 2) sobre la mediana de 2021 (≈ 428 mil M$; Hacienda informo ≈ 427 mil M$). Con esto el
  primario coincide con el oficial: 2017 −3,79 · 2019 −0,44 · 2020 −6,43 · 2021 −3,05 · 2022 −2,36 ·
  2024 +1,78. No se ajusta 2016-2017 (blanqueo dentro de tributarios).
- **Credito**: crecimiento real con prestamos solo en pesos (var 117): la var 26 incluye prestamos en
  dolares valuados al oficial y cada devaluacion inflaba el "crecimiento" (dic-2023: +11% con +81% de
  devaluacion). Credito/PIB usa el total (ahi la valuacion corresponde).
- **PIB mensual**: EMAE × IPC calibrado trimestre a trimestre al PIB nominal INDEC (serie trimestral
  anualizada / 4); trimestres sin PIB usan el ultimo factor.

### Normalizacion y agregacion
- z = (x − mediana) / (IQR/1,349) sobre toda la historia disponible de cada variable, signo "mas
  alto = mejor", recorte ±3. Se descarto MAD: la brecha tiene ~95 meses en 0 y el MAD quedaba ~0,8 pp
  → cualquier brecha > 3% saturaba.
- **Ventanas distintas**: cada variable se normaliza con su historia (recaudacion 2017+, fiscal
  dic-2016+, salario 2016+, SIPA 2013+): 0 = tipico de ESE periodo (`normalizado_desde` en Metodologia).
- Pilar = promedio de sus variables con dato; indice = promedio de pilares (minimo 4).
  `indice_sin_fiscal` = sin el pilar fiscal (arranca dic-2016): comparable en toda la serie.
- **Vara de Precios**: el indice principal compara con la historia argentina (mediana de inflacion
  ~26% anual → 20% cuenta como "mejor que lo tipico"; nov-2008 da +0,03 en plena crisis global).
  Como referencia, `indice_ancla` mide Precios contra una **meta de 10% anual** (`Precios_ancla`,
  misma escala). Se mantiene el historico como principal por consistencia metodologica con el resto.
- Borde: el ultimo dato de cada variable se arrastra hasta 3 meses (hoja `Arrastrados`); ultimo mes
  del indice = ultimo con ≥ 60% de variables con dato propio.
- Por gestion: el mes va a quien gobierno la mayor parte (asuncion hasta el dia 15 → mes propio);
  pilar vacio si tiene < 12 meses con dato.

### Limitaciones conocidas (documentadas, no resolubles con datos publicos por API)
- Reservas **brutas** (incluyen swap con China y encajes) y a **fin de mes** (pico diario 2019:
  77,5 MM USD el 9-abr; fin de mes max 71,7). El BCRA no publica reservas netas por API.
- IPC Neuquen es provincial; UTDT es encuesta a hogares (por eso se ajusta el nivel).
- `inflacion_3m` e `inflacion_esperada` correlacionan 0,81: el pilar Precios es casi una sola senal.
- Desocupacion 2004-T1 = 14,28% en la API vs 14,4% publicado entonces (revision de la serie).
- TCRM penaliza igual atraso y adelanto; tasa real neutral fijada en 2%; pesos iguales por pilar.
- Validacion: correlacion de Spearman con el indice de miseria ≈ −0,56; episodios (2009, 2014,
  2018-19, 2020, fines de 2023 - inicio 2024) ubicados correctamente.

## 5. Validaciones de referencia

| Chequeo | Resultado esperado |
|---|---|
| Primario nominal 2024 / 2025 (Sector Publico Total) | 10,41 B / 11,77 B (Hacienda oficial) |
| Financiero nominal 2024 / 2025 | 1,76 B / 1,45 B |
| Identidades AIF por mes (III=I−II, VI=I+IV, VII=II+V, VIII=VI−VII, XIV=XV+II2) | cierran en los 79 meses |
| XI − XII = XIV (anual) | exacto |
| Consolidacion reproducible | `consolidate.py` genera los CSV versionados byte a byte |

## 6. Trampas conocidas (historial de bugs)

- **IMIG fecha falsa (corregido sep-2026)**: `detect_value_columns` buscaba fechas tambien en filas
  de datos; un valor ~45.000 M$ se interpretaba como fecha serial Excel (→ 2023-03). Ahora solo mira
  el encabezado (antes de "INGRESOS TOTALES"), una fecha por columna, anos hasta el actual+1.
- IMIG: `r"IVA"` matcheaba "CONTRIBUTIVAS" → `\bIVA\b` y orden de patrones (Jubilaciones antes que IVA).
- IMIG: `r"TRIBUTARIOS"` tambien matchea "Ingresos no tributarios" en algunos anos (nivel 2); no se
  usa en los notebooks, pero ojo si se agrega un grafico con `Tributarios` nivel 2.
- AIF: `I2_APORTES_SEG_SOCIAL` con variante vieja "Contribuciones a la Seg. Social" (2021-2022).
- AIF: la sangria de la columna B define la jerarquia → no aplicar `.strip()` antes de leerla.
- AIF: filas con notas al pie "(2)", "(3)" quedan como conceptos crudos separados. No afecta
  totales (los principales se leen directo, no se suman detalles).
- Rama `main` (no `master`): los links de Colab dependen de eso.
