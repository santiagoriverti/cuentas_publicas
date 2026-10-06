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
  de datos.gob.ar (= `4.4_OGP_2004_T_17`, que arranca en 2004), que viene **trimestral anualizada** → anual = suma de los 4 trimestres / 4
  (sumarlos sin dividir da 4 veces el PIB). Hasta oct-2026 habia valores aproximados erroneos
  (2023 = 143,2). 2026 = n/d hasta que INDEC lo publique.

## 4b. Indice Macroeconomico (notebook 03)

### Datos
- `scripts/actualizar_macro.py` → `data/reference/macro_mensual.csv` (28 series crudas + 4 columnas
  calculadas de reservas netas, mensuales). Diarios → promedio del mes (stocks: reservas, encajes,
  pasivos del BCRA → ultimo dato del mes); trimestrales → mismo valor en los 3 meses. Si una API
  falla, conserva la columna anterior e imprime "FALLO".
- Fuentes: datos.gob.ar (EMAE, SIPA, salarios, desocupacion EPH [la API da fraccion → se guarda en
  %], expo/impo, PIB nominal, IPC Neuquen, UTDT promedio, CSV IMIG mensual 2016+), BCRA API v4
  (`verify=False`; reservas var 1, encajes var 1243, A3500, BADLAR, prestamos totales var 26 y en
  pesos var 117, REM var 29, inflacion var 27), BCRA cotizaciones (`estadisticascambiarias/v1.0/
  Cotizaciones/CNY`, `tipoPase` = USD por yuan; rechaza fechas futuras), BCRA balance semanal XLS
  (obligaciones con organismos internacionales), BCRA ITCRMSerie.xlsx (columna "ITCRM " con
  espacio), argentinadatos (riesgo pais, CCL), Ambito (blue con centavos,
  `/dolar/informal/historico-general/dd-mm-aaaa/dd-mm-aaaa`).
- Del repo: IPC (`IPC.xlsx`) e IMIG (`output/imig_consolidado.csv`). La IMIG se completa 2016-2018
  con el CSV de datos.gob.ar (distribucion 452.3; coincide 0,00% con la del repo en 2019-2026).
  OJO: los IDs `452.2_*` de la API son trimestrales y `452.1_*` anuales. 2003-2015: AIF historica
  (columnas `aif_hist_*`, ver "Fiscal 2003-2015").

### Variables (18) y pilares (celda 3 del NB03; hoja `Metodologia`)
| Pilar | Variable | Signo | Nota |
|---|---|---|---|
| Actividad | `emae_ia` EMAE desest. var. i.a. | + | |
| Actividad | `emae_vs_maximo` EMAE desest. vs su maximo de los 36 meses previos, % | + | nivel (v8), desde 2005 |
| Actividad | `recaudacion_ia` IVA + Deb./Cred. reales, trim. movil, var. i.a. | + | repo IMIG, desde 2017-03 |
| Empleo | `sipa_ia` asalariados privados registrados var. i.a. | + | desde 2013 |
| Empleo | `salario_real_ia` indice de salarios registrados / IPC, var. i.a. | + | desde 2016-10 |
| Empleo | `desocupacion` | − | trimestral |
| Precios | `inflacion_3m` 400·ln(IPC/IPC₋₃) | − | log |
| Precios | `inflacion_esperada` 100·ln(1+exp) | − | log |
| Fiscal | `primario_pib` primario 12 m sin extraordinarios / PIB 12 m | + | desde dic-2004 (v7; antes dic-2016) |
| Fiscal | `intereses_ingresos` intereses netos / ingresos sin extraordinarios, 12 m | − | desde ene-2004 (v7) |
| Externo | `reservas_netas_meses_impo` reservas netas / importaciones mensuales promedio 12 m | + | ver "Reservas netas" |
| Externo | `saldo_comercial_pib` (expo − impo) 12 m / PIB 12 m en USD (a A3500), % | + | desde dic-2004 (v6) |
| Externo | `brecha` CCL / A3500 − 1 | − | 0 antes de nov-2011 |
| Externo | `tcrm_desalineado` \|ln(ITCRM / mediana)\| | − | simetrico |
| Financiero | `riesgo_pais` | − | |
| Financiero | `credito_real_ia` prestamos EN PESOS / IPC, var. i.a. | + | var 117 |
| Financiero | `credito_pib` prestamos totales ($ + USD) / PIB 12 m | + | var 26; desde dic-2004 (v6) |
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
  2024 +1,78. No se ajusta 2016-2017 (blanqueo dentro de tributarios). En 2003-2015 tambien se restan
  el DEG de nov-dic 2009 (≈ 9.573 M$, en transferencias corrientes) y la licitacion 4G de dic-2014
  (≈ 7.978 M$, no tributarios; subasta de USD 2.233 M), como exceso sobre la mediana del anio.
- **Fiscal 2003-2015 (v7)**: AIF del Sector Publico Nacional base caja mensual (datos.gob.ar, dataset
  379: 379.7 = 1993-2006, 379.8 = 2007-2014, 379.9 = metodologia 2017 desde 2015) llevada al criterio
  de la IMIG (`actualizar_macro.aif_historica`). La 379.9 es identica a la IMIG en 2016-2026 (primario,
  intereses, ingresos y financiero) → 2015 se toma tal cual. En 2003-2014:
  - Utilidades del BCRA: se restan con la var 50 del BCRA (transferencias de utilidades, suma mensual),
    que coincide mes a mes con las "rentas percibidas del BCRA" de la AIF 2015-2026.
  - Rentas que el FGS cobra al propio sector publico: en la metodologia 2017 se netean contra los
    intereses; antes de 2015 no hay desglose → las rentas sin BCRA se reparten con la proporcion de
    2015-16 (34% genuinas, 66% intra). Primario = superavit − utilidades − intra; intereses = brutos −
    intra; ingresos = antes de figurativos − utilidades − intra. Las rentas sin BCRA eran 0,1-0,4% del
    PIB antes de 2009 y 0,7-0,9% despues (estatizacion de las AFJP): el supuesto mueve el primario
    ±0,3 pp como mucho.
  - 1993-2006 registra coparticipacion + leyes especiales (~5,5% del PIB) como ingreso y como gasto: se
    restan de los ingresos (el resultado no cambia; los tributarios 2006 → 2007 quedan 11,8% vs 12,2%).
  - Resultado (% PIB): 2004 +3,3 · 2006 +2,9 · 2008 +2,2 · 2009 −0,3 · 2010 −0,2 · 2012 −1,0 · 2013
    −2,2 · 2014 −3,3 · 2015 −3,8 · 2016 −4,2 (empalme sin saltos). Intereses/ingresos: 7-10% en 2004-09,
    4-7% en 2010-15 (deuda en manos del propio sector publico y bonos en default sin pagar), 15% en 2018.
  - No separable: los traspasos de afiliados de las AFJP de 2007 (dentro de aportes).
  - Efecto: la normalizacion fiscal pasa a 2004-2026 (mediana del primario −0,85% vs −2,48%) → el
    superavit actual pesa menos: Fiscal ago-2026 +1,18 → +0,33; IMA +0,14 → +0,00. Lectura: intereses/
    ingresos premia 2010-15 (carga baja por deuda intra-sector publico): CFK II tiene Fiscal +0,32 con deficit.
- **Credito**: crecimiento real con prestamos solo en pesos (var 117): la var 26 incluye prestamos en
  dolares valuados al oficial y cada devaluacion inflaba el "crecimiento" (dic-2023: +11% con +81% de
  devaluacion). Credito/PIB usa el total (ahi la valuacion corresponde).
- **PIB mensual**: EMAE × IPC calibrado trimestre a trimestre al PIB nominal INDEC (serie trimestral
  anualizada / 4); trimestres sin PIB usan el ultimo factor. Serie `4.4_OGP_2004_T_17` (2004-T1 en
  adelante; identica a la `166.2_PPIB_0_0_3`, que arranca en 2006 y llega un trimestre menos). Como el
  EMAE empieza en 2004, las variables con PIB de 12 meses arrancan en dic-2004.
- **Saldo comercial en % del PIB (v6)**: antes iba en MM USD corrientes y la economia en dolares es ~3
  veces la de 2004 → el superavit de 2026 (24,5 MM) daba z +1,64, el mejor del pilar, aunque en % del
  PIB (3,4%) es la mitad que en 2004-05 (7,4% / 5,9%). PIB en USD = suma 12 m de PIB mensual / A3500.
  Con cepo el oficial esta sobrevaluado → PIB en USD alto → saldo % PIB algo subestimado en 2011-15 y
  2019-23 (convencion del FMI/INDEC: tipo de cambio oficial).

- **Nivel de actividad (v8)**: las variables de Actividad y Empleo eran casi todas var. i.a. (ritmo): un
  rebote post-crisis puntuaba como bonanza. `emae_vs_maximo` = EMAE / maximo de los 36 meses PREVIOS − 1
  (sin incluir el mes: si se incluye, 20% de los meses quedan en 0 exacto y el IQR se deforma; 36 meses =
  posicion en el ciclo, no estancamiento estructural). Corr. con `emae_ia` 0,77. Ej.: jun-2021 var. i.a.
  +13,9% pero −3,6% vs el pico; dic-2019 −1,4% i.a. pero −8,3% vs el pico; jul-2026 −4,5% vs el pico.
  Efecto: max 0,20 (may-2021), promedio 0,03; ago-2026 +0,00 → −0,02.

### Normalizacion y agregacion
- z = (x − mediana) / (IQR/1,349) sobre toda la historia disponible de cada variable, signo "mas
  alto = mejor", recorte ±3. Se descarto MAD: la brecha tiene ~95 meses en 0 y el MAD quedaba ~0,8 pp
  → cualquier brecha > 3% saturaba. La mediana y el IQR se calculan **solo sobre datos propios**
  (v4: los arrastres de borde de la hoja Arrastrados no entran en las estadisticas; el z de los
  meses arrastrados si se calcula con esa mediana/escala).
- **Ventanas distintas**: cada variable se normaliza con su historia (recaudacion 2017+, fiscal
  2004+ desde la v7, salario 2016+, SIPA 2013+): 0 = tipico de ESE periodo (`normalizado_desde` en Metodologia).
- Pilar = promedio de sus variables con dato; indice = promedio de pilares (minimo 4).
  `indice_sin_fiscal` = sin el pilar fiscal; desde la v7 es solo referencia (el fiscal cubre 2004-hoy y el
  indice completo ya es comparable en toda la serie: 5 pilares en 2004, 6 desde 2005).
  **Pesos iguales por pilar**: se evaluo ponderar por PCA (oct-2026) y se descarto — el 1er
  componente principal de los pilares explica solo ~40% de la varianza y carga con signos mixtos
  (con 6 pilares: Externo −46%, Precios −10%; con 5 sin fiscal: Empleo −17%), senal de que no hay
  un factor comun dominante. En ese caso la practica estandar en indicadores compuestos (manual
  OCDE) es mantener pesos iguales.
- **Vara de Precios**: el indice principal compara con la historia argentina (mediana de inflacion
  ~26% anual → 20% cuenta como "mejor que lo tipico"; nov-2008 da +0,03 en plena crisis global).
  Como referencia, `indice_ancla` mide Precios contra una **meta de 10% anual** (`Precios_ancla`,
  misma escala). Se mantiene el historico como principal por consistencia metodologica con el resto.
- Borde: el ultimo dato de cada variable se arrastra hasta 3 meses (hoja `Arrastrados`); ultimo mes
  del indice = ultimo con ≥ 60% de variables con dato propio.
- Por gestion: el mes va a quien gobierno la mayor parte (asuncion hasta el dia 15 → mes propio);
  pilar vacio si tiene < 12 meses con dato.

### Reservas netas (oct-2026; reemplazan a las brutas en el pilar Externo)
- **Netas = brutas − encajes − obligaciones con organismos internacionales − swap con China − REPO
  del BCRA − swap con el Tesoro de EEUU**, a fin de mes (M USD, columna `reservas_netas_usd`).
  Idea: restar los pasivos en moneda extranjera del BCRA cuya contrapartida esta dentro de las brutas.
  - Encajes: cuentas corrientes en ME de los bancos en el BCRA (API var 1243; coincide con el balance).
  - Organismos internacionales: renglon del balance semanal (XLS, "Obligations with international
    agencies", neto de la contrapartida del tramo de reservas). Capta la deuda del BCRA con el FMI
    hasta ene-2006 (16,8 MM en 2003), los creditos del BIS 2018-abr 2024 (2,3-3,7 MM) y el swap con
    el BIS de dic-2025 a may-2026 (2,5 MM, con el que se cancelo el swap con EEUU).
  - Sin serie publica → `data/reference/reservas_pasivos_manual.csv` (con fuente por fila): swap con
    China en yuanes (tramos 2014-15, 70.000 M desde sep-2015, 130.000 M desde dic-2018; valuado con la
    cotizacion CNY del BCRA), REPO del BCRA (2016: 5.000 → 1.000 M, var 76; 2025-26: 1.000 → 3.000 →
    6.000 M) y swap con el Tesoro de EEUU (2.541 M, oct-nov 2025).
- **No se restan**: SEDESA (fondo de garantia de depositos, ~1,5-2 MM USD en 2023-26; sin serie
  publica), Bopreal (no trajo dolares a las brutas; mayormente > 1 anio), deuda del Tesoro (bonos,
  REPO del Tesoro de 2017, FMI desde 2018: el desembolso de 2025 cuenta como reserva, igual que el de
  2018-19), asignaciones de DEG. Los "otros pasivos" y "pases" del balance no sirven para el swap ni los
  REPO: mezclan partidas en pesos.
- Contraste: dic-2023 = −6,6 MM (consultoras: −9,4 a −11,5, que ademas restan SEDESA y el BIS bruto);
  feb-2026 = +1,4 MM (FMI Art. IV 2026: activos ~45 − encajes 18 − swaps PBoC+BIS 20 − SEDESA 2 ≈ +5,
  sin restar REPO; y ≈ −10 excluyendo el credito FMI 2025, criterio del programa). Ago-2026 = +9,2 MM.
- En meses de importaciones: 2004 negativo (deuda con el FMI), maximo 12,6 en jun-2007, ~5-7 en
  2017-19, minimo reciente −1,4 en nov-2023. Correlacion con las brutas (z) 0,61. Efecto en el indice:
  max 0,15 (ene-2004), promedio 0,03; ago-2026 +0,20 → +0,19; Spearman con miseria sin cambio (−0,56).
- Si el BCRA toma o cancela un REPO/swap, agregar la fila en el CSV manual (`hasta` vacio = vigente).

### Limitaciones conocidas (documentadas, no resolubles con datos publicos por API)
- Reservas a **fin de mes** (pico diario 2019: 77,5 MM USD el 9-abr; fin de mes max 71,7). Netas sin
  SEDESA y con el swap chino 2015 interpolado entre ene y sep (sin dato mensual publico).
- IPC Neuquen es provincial; UTDT es encuesta a hogares (por eso se ajusta el nivel).
- `inflacion_3m` e `inflacion_esperada` correlacionan 0,81: el pilar Precios es casi una sola senal.
- Desocupacion 2004-T1 = 14,28% en la API vs 14,4% publicado entonces (revision de la serie).
- TCRM penaliza igual atraso y adelanto; tasa real neutral fijada en 2%; pesos iguales por pilar
  (PCA evaluado y descartado, ver "Normalizacion y agregacion").
- Validacion: correlacion de Spearman con el indice de miseria ≈ −0,56 (indice completo, v7; sin fiscal
  −0,54); episodios (2009, 2014,
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
