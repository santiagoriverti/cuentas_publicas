# Proyecto: cuentas_publicas

## Objetivo
Consolidar datos del Sector Público Nacional argentino (Hacienda) en un dataset tidy para análisis macro del ajuste fiscal y superávit primario, con desagregación por subsector institucional y transferencias a provincias. Expresar valores en pesos constantes via IPC.

## Repositorio GitHub
- URL: https://github.com/santiagoriverti/cuentas_publicas (rama: main)
- Notebook 01 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb
- Notebook 02 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb

## Fuente de datos
- URL: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica
- ZIP original: data/raw/sector_publico.zip.zip (gitignored)
- 75 archivos Excel (xls/xlsx), 2020-2026
- IPC INDEC: data/reference/IPC.xlsx (commiteado, ene-2017 a abr-2026)

## Estructura de archivos del repo
```
data/
  raw/          <- ZIP + Excel originales (gitignored, agregar nuevos meses aqui)
  reference/    <- IPC.xlsx y otros datos de referencia (commiteados)
output/
  aif_consolidado.csv    (~27.250 registros)
  imig_consolidado.csv   (~6.830 registros)
src/
  aif_parser.py    <- Parser AIF
  imig_parser.py   <- Parser IMIG
  consolidate.py   <- Script principal (lee data/raw/ -> output/)
  deflate.py       <- Modulo deflacion: load_ipc(), deflate_series(), deflate_df()
notebooks/
  01_consolidar.ipynb    <- Carga CSVs de GitHub, exporta Excel unificado descargable
  02_analisis_fiscal.ipynb <- Analisis completo con deflactor, exporta Excel resultados
```

## Datasets generados

### output/aif_consolidado.csv
- 27.250 filas | fecha, anio, mes, periodo, concepto_codigo, concepto_descripcion, concepto_nivel, subsector, valor_millones_pesos, fuente_archivo
- 54 conceptos únicos (15 principales I-XV + ~40 sub-items con sangría)
- concepto_nivel: principal / detalle / subdetalle / micro
- Para series largas: subsector=total_adm_nacional, periodo=mensual

### output/imig_consolidado.csv
- 6.830 filas | 52 conceptos en 3 niveles jerárquicos
- nivel_jerarquia: 0=principal, 1=detalle, 2=subdetalle
- Incluye año anterior como comparación (datos desde 2019)

## Notebooks en detalle

### Notebook 01 - Consolidacion
Exporta `datos_fiscales_consolidado.xlsx` con 5 hojas:
- AIF_mensual: todos los conceptos x subsector
- AIF_acumulado: idem acumulado
- Resultado_pivot: KPIs en columnas (ingresos, gastos, intereses, prestaciones, resultado)
- Transferencias_provincias: pivot fecha x tipo (Corrientes/Capital) x subsector
- IMIG: detalle funcional

### Notebook 02 - Analisis Fiscal
Lee CSVs + IPC desde GitHub. Todo corre en Colab sin subir archivos.
Base deflación: pesos constantes de abril 2026 (último mes IPC disponible).
Secciones:
1. Resultado Primario y Financiero 2020-2026 (nominal + real, lado a lado)
2. El ajuste 2024-2026: cuánto y de dónde (tabla 2022/2023/2024/2025 + gráfico variación)
3. Cuánto del ajuste se trasladó a provincias (con % cuantificado)
4. Composición del gasto apilada (real)
5. Composición de ingresos (real)
6. Desagregación por subsector institucional
7. Exporta `analisis_fiscal_resultados.xlsx` con 4 hojas:
   - Serie_mensual: KPIs mes a mes, nominal Y real
   - Resumen_anual: totales anuales
   - Transferencias_prov: corrientes + capital, Tesoro y total, nominal + real
   - Ajuste_componentes: tabla del ajuste por componente

## Módulo deflate.py
- load_ipc(): carga IPC local o descarga desde GitHub
- deflate_series(serie, ipc, base_date): serie nominal -> pesos constantes
- deflate_df(df, value_col, date_col, ipc, base_date): agrega columna valor_real al df

## Arquitectura parsers

### src/aif_parser.py - bugs corregidos
- Sub-items: col_b_raw sin strip() para contar sangría correctamente
- Capital a provincias: patrón ". A PROVINCIAS Y CABA" con prioridad sobre "PROVINCIAS Y CABA"
  * Corrientes: `.. Provincias y CABA` → II4b1_TRANSF_PROVINCIAS_CABA
  * Capital: `. A Provincias y CABA` → V2a_TRANSF_CAPITAL_PROVINCIAS

### src/imig_parser.py - bugs corregidos
- Jerarquía en cols base/base+1/base+2 (no solo col base)
- Fechas: rango restringido 2018-2026

### src/consolidate.py
- Uso: python src/consolidate.py (busca data/raw/ por defecto)
- Idempotente: sobreescribe CSVs con datos más actualizados

## Flujo para agregar nuevos meses
1. Descargar Excel de Hacienda -> copiar a data/raw/
2. python src/consolidate.py
3. git add output/ && git commit -m "datos: YYYY-MM" && git push
4. Notebooks en Colab ya tienen los nuevos datos automáticamente

## Meses faltantes en datos fuente (no hay Excel en el ZIP)
- Noviembre 2021
- Septiembre 2022

## Hallazgos clave (2020-2026, en pesos corrientes)
- 2020-2023: déficit primario persistente
  - Pico: 2023 = -6.22 billones ARS nominales
- 2024-2026: superávit primario sostenido
  - 2024: +7.69 B | 2025: +7.89 B | 2026 (4 meses): +5.36 B
  - Excepción: diciembre cada año (aguinaldos)
- Intereses deuda: crecen de 1.3 B (2022) a 10.3 B (2025)
- Transferencias corrientes Tesoro -> Provincias/CABA:
  - 2023: 1.124 B | 2024: 1.324 B | 2025: 2.028 B
  - Capital 2023: 273 MM | 2024: 35 MM (caída -87% real) | 2025: 111 MM

## Validacion de resultados (2026-06-04)

### Resultado financiero - matchea con fuente oficial (base mar-2026):
| Año | Referencia | Nuestro |
|---|---|---|
| 2023 | -44.3 B | -47.0 B (~6% dif. por base mar vs abr 2026) |
| 2024 | +4.0 B | +4.2 B ✅ |
| 2025 | +2.5 B | +2.4 B ✅ |

### Transferencias a provincias:
- Var 2023→2025: -70% (ref: -73%) ✅
- Var absoluta: -7.6 B (ref: -8.7 B) — diferencia por consolidación intra-sector

### Nota metodológica importante: consolidación intra-sector
El gasto primario total y % de provincias difieren porque la referencia usa sector
público consolidado (neta transferencias intra-sector). En nuestro cálculo, cuando
Tesoro transfiere fondos a PAMI, aparece como gasto en ambos lados → denominador inflado.
- Nuestro % provincias/ajuste gasto: 9.3% (ref: 15.9%)
- Para los titulares de resultado financiero, la cifra es correcta porque los resultados
  por entidad ya incluyen esas transferencias netas en sus ingresos/gastos.

### Componentes del ajuste 2023→2025 (Adm. Nacional, real):
- Subsidios (transf. sector privado): -17.7 B (-36.6% del ajuste)
- Gastos corrientes totales: -42.3 B
- Gastos de capital: -6.0 B
- Transferencias a provincias/CABA: -5.0 B (-10.2% del ajuste)
- Remuneraciones: -6.2 B (-12.9%)
- Universidades: -2.5 B (-5.2%)
- Prestaciones Seg. Social: -3.4 B (-7.0%)
- UNICA partida que CRECIÓ: no capturada aún a nivel sub-item (AUH está en IMIG)

## Pendiente / Próximas sesiones
- [ ] Consolidación real: usar total_general (disponible desde 2026) como benchmark
      para entender cuánto del gap en gasto primario es por doble-conteo intra-sector
- [ ] Análisis IMIG: AUH (+71% real), subsidios energía/transporte desagregados
- [ ] Deflactor IPC: actualizar cuando salgan nuevos meses (mayo 2026+)
- [ ] Datos MECON de finanzas provinciales desagregadas por jurisdicción
- [ ] Exportar a Parquet para queries más rápidas
- [ ] Mejorar formato Excel: columnas reales en billones (no MM ARS) para legibilidad
