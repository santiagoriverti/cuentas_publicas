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
- **% PIB**: PIB nominal aproximado hardcodeado en la celda 9 (`PIB_B`, billones: 2020 44,9 · 2021 72,0 ·
  2022 115,0 · 2023 143,2 · 2024 586,7 · 2025 725,0). Solo orden de magnitud; 2026 = n/d.
  Actualizar cuando haya PIB 2026.

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
