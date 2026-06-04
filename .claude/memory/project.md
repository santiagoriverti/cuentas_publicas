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

## Validacion contra datos oficiales de Hacienda (2026-06-04)

### Comparacion con datos oficiales Hacienda (nominal, billones ARS):

| Año | Primario oficial | Nuestro | Dif | Financiero oficial | Nuestro | Dif |
|---|---|---|---|---|---|---|
| 2023 | -5.48 B | -5.2 B | ~5% | -8.74 B | -8.4 B | ~4% |
| 2024 | +10.41 B | +10.4 B | <0.1% ✅ | +1.76 B | +1.8 B | ~2% ✅ |
| 2025 | +11.77 B | +11.8 B | <0.3% ✅ | +1.45 B | +1.5 B | ~3% ✅ |

Fuentes oficiales:
- https://www.argentina.gob.ar/noticias/el-sector-publico-nacional-registro-superavit-financiero-anual-por-primera-vez-desde-el
- https://www.argentina.gob.ar/noticias/en-el-ano-2025-el-sector-publico-nacional-registro-un-superavit-financiero-de-1453819

**2024 y 2025 coinciden con menos del 3% de diferencia → dataset validado.**
Diferencia ~5% en 2023: los Excel del ZIP son versiones provisorias; Hacienda publica
cifras definitivas revisadas. No hay bug en el código.

### Nota metodológica: consolidación intra-sector
Al sumar total_adm_nacional + pami_fdos_otros para gasto primario, se infla el denominador
porque las transferencias intra-sector aparecen en ambos lados (ej: Tesoro → PAMI).
Esto afecta solo el % provincias/ajuste (9.3% nuestro vs ~15.9% de otros análisis).
El resultado financiero NO está afectado porque los resultados por entidad ya netean esos flujos.

### Componentes del ajuste 2023→2025 (Adm. Nacional, real):
- Subsidios (transf. sector privado): -17.7 B (-36.6% del ajuste)
- Gastos corrientes totales: -42.3 B
- Gastos de capital: -6.0 B
- Transferencias a provincias/CABA: -5.0 B (-10.2% del ajuste)
- Remuneraciones: -6.2 B (-12.9%)
- Universidades: -2.5 B (-5.2%)
- Prestaciones Seg. Social: -3.4 B (-7.0%)
- UNICA partida que CRECIÓ: no capturada aún a nivel sub-item (AUH está en IMIG)

## Notebook 02 - Graficos (estado 2026-06-04)
- Todos en pesos constantes abr-2026. Sin titulos principales.
- Eje X: todos los meses, rotados 45 grados. Exportados a 600 DPI.
- Descarga final: analisis_fiscal.zip con Excel + 7 PNGs separados:
  01_resultado_primario_financiero.png
  02_ajuste_componentes_2023_2025.png
  03_transferencias_provincias.png
  04_composicion_gasto_corriente.png
  05_composicion_ingresos.png
  06_resultado_por_subsector.png
  07_intereses_deuda.png

## Pendiente / Próximas sesiones
- [ ] Análisis IMIG: AUH (+71% real), subsidios energía/transporte desagregados
- [ ] Deflactor IPC: actualizar cuando salgan nuevos meses (mayo 2026+)
- [ ] Datos MECON de finanzas provinciales desagregadas por jurisdicción
- [ ] Exportar a Parquet para queries más rápidas
- [ ] Consolidación intra-sector para % provincias/ajuste más preciso
