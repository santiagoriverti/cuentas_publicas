# Proyecto: cuentas_publicas

## Objetivo
Consolidar datos del Sector Publico Nacional argentino (Hacienda) en un dataset tidy para analisis macro del ajuste fiscal y superavit primario, con desagregacion por subsector institucional y transferencias a provincias.

## Repositorio
- GitHub: https://github.com/santiagoriverti/cuentas_publicas (rama: main)
- Local: C:\Users\sriverti\Desktop\INECO\Repositorios\cuentas_publicas
- Notebook 01 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb
- Notebook 02 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb

## Fuente de datos
- URL: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica
- ZIP: data/raw/sector_publico.zip.zip (gitignored)
- Archivos sueltos en data/raw/ (gitignored): Nov-2021, Sep-2022, Jun-2022
- IPC INDEC: data/reference/IPC.xlsx (commiteado, ene-2017 a abr-2026)
- 78 archivos Excel, cobertura ene-2020 a abr-2026
- Gap unico AIF mensual: Jun-2022 (solo existe acumulado I Semestre)

## Datasets
- output/aif_consolidado.csv: 27.964 registros
- output/imig_consolidado.csv: 8.421 registros (4.706 tras dedup en runtime)
- Validado vs Hacienda: 2024 y 2025 con 0.00% diferencia en primario y financiero

## Estructura de codigo
```
src/
  aif_parser.py    <- Parser AIF. Bugs corregidos: sangria, patrones IVA/CONTRIBUTIVAS
  imig_parser.py   <- Parser IMIG. Jerarquia multi-columna, fechas "ene-22", \bIVA\b
  consolidate.py   <- iter_sources(): ZIP + archivos sueltos en data/raw/
  deflate.py       <- Utilidades de deflacion IPC
data/reference/
  IPC.xlsx         <- IPC Nivel General INDEC ene-2017 a abr-2026 (commiteado)
```

## Notebook 01 - Consolidacion
Exporta datos_fiscales_consolidado.xlsx (5 hojas):
- AIF_mensual | AIF_acumulado | Resultado_pivot (Sector Publico Total) | Transferencias_provincias | IMIG

## Notebook 02 - Analisis Fiscal (estado final verificado)
10 celdas, todas limpias (usa Write() para reescrituras - NO usar NotebookEdit).

Graficos (7, 600 DPI, etiquetas trimestrales en espanol, linea naranja Milei dic-2023):
  01_resultado_primario_financiero.png   <- barras primario + linea financiero mensual
  02_composicion_gasto.png              <- gasto corriente apilado mensual
  03_composicion_ingresos.png           <- ingresos apilados mensual
  04_transferencias_provincias.png      <- transferencias corrientes + capital Tesoro
  05_ajuste_componentes_anual.png       <- barras dobles 2023 vs 2024/2025 (AIF)
  06_torta_recorte_gasto.png            <- % por rubro (IMIG, 2023 vs 2025 anual)
  07_recorte_por_rubro.png              <- barras dobles por rubro IMIG (2023 vs 2024/2025)

Excel (5 hojas): Serie_mensual | Resumen_anual | Transferencias_prov |
                 Ajuste_AIF_anual | Ajuste_IMIG_rubros

Descarga: analisis_fiscal.zip (7 PNG + Excel)

Comparacion del ajuste: ANUAL 2023 vs 2024/2025 (anos completos, robusta)
NO usar comparacion mensual dic-23: sesgo alto por estacionalidad de diciembre

Celda 9 - Resumen completo (4 secciones):
  1. Resultado fiscal anual 2020-2026 con % PIB
  2. Magnitud del ajuste (anos completos 2023 vs 2024 y 2025)
  3. Desglose por componente AIF (2023 vs 2024/2025)
  4. Desglose funcional IMIG por rubro (2023 vs 2025)

## Validacion vs Hacienda oficial (nominal, sin diferencia)
| Año | Primario | Financiero |
|---|---|---|
| 2024 | +10.41 B (0.00%) ✅ | +1.76 B (0.00%) ✅ |
| 2025 | +11.77 B (0.00%) ✅ | +1.45 B (0.00%) ✅ |

## PIB nominal hardcodeado (billones ARS)
2020:44.9 | 2021:72.0 | 2022:115.0
2023:143.2 (deficit 8.74B = -6.1% PIB, Hacienda)
2024:586.7 (superavit 1.76B = +0.3% PIB, Hacienda)
2025:725.0 (superavit 1.45B = +0.2% PIB, Hacienda)

## Hallazgos clave verificados (pesos constantes abr-2026)

### Macro - Sector Publico Total (AIF):
- Gasto primario: 274.6 B (2023) → 189.4 B (2024) → 193.0 B (2025)
- Reduccion: -31.1% en 2024 vs 2023 | -29.7% en 2025 vs 2023
- Resultado primario: -27.3 B (2023) → +21.0 B (2024) → +15.7 B (2025)
- Mejora primaria 2023→2024: +48.3 B
- Resultado financiero: -47.0 B (2023) → +4.2 B (2024) → +2.4 B (2025)

### Mensual dic-2023 → abr-2026 (AIF, Adm. Nacional):
ATENCION: dic-2023 es mes de alto gasto estacional (aguinaldo), caidas % magnificadas
- Gastos corrientes: 18.0 → 10.9 B = -7.1 B (-39.3%)
- Intereses: 1.3 → 0.4 B = -1.0 B (-72.4%)
- Subsidios: 4.5 → 2.5 B = -2.0 B (-43.9%)
- Remuneraciones: 2.8 → 1.4 B = -1.4 B (-51.0%)
- Prestaciones: 6.8 → 5.5 B = -1.2 B (-18.1%)
- Resultado primario: -7.0 → +0.3 B = +7.2 B

### Funcional dic-2023 → abr-2026 (IMIG):
- AUH: +0.4 B (+183.8%) <- UNICO rubro con gran suba
- PAMI: flat (+0.1%)
- Salarios: -1.7 B (-50.5%)
- Obra publica: -0.6 B (-57.8%)
- Subsidios: -1.1 B (-48.0%)
- Jubilaciones: -1.1 B (-18.2%)
- Transf. Provincias: -0.8 B (-83.7%)
- Universidades: -0.8 B (-65.1%)
- Otros prog. sociales: -1.0 B (-53.8%)
- Total baja: -7.2 B | Total suba: +0.4 B | Neto: -6.8 B

## Bugs corregidos (historial completo)
- AIF: sangria en col_b borrada por .strip() → usar col_b_raw
- AIF: ". A PROVINCIAS" patron capital vs corrientes
- IMIG: solo leia col base → ahora base/+1/+2
- IMIG: fechas 2027+ por seriales Excel → rango 2018-2026
- IMIG: r"IVA" matcheaba "CONTRIBUTIVAS" → r"\bIVA\b" + orden correcto
- IMIG: AUH normalizacion con acento → r"ASIGNACI.N UNIVERSAL"
- NB01: Resultado_pivot usaba solo total_adm_nacional → get_total_pivot()
- NB01: get_total() perdia nombre de Serie → concat por columnas
- NB02: NotebookEdit sobreescribio celda datos (bug de encoding \n) → usar Write()
- NB02: df_anual sin index=idx → RangeIndex.year error → index=idx
- Rama master → main (fix Colab 404)
- Jun-2022 IMIG: formato multi-columna (6 meses horizontales) → ahora parseado

## Flujo para nuevos meses
1. Descargar Excel de Hacienda → copiar a data/raw/
2. python src/consolidate.py
3. git add output/ && git commit -m "datos: YYYY-MM" && git push
4. Notebooks en Colab se actualizan automaticamente

## Pendiente
- [ ] Datos provinciales MECON por jurisdiccion
- [ ] IPC: actualizar cuando salgan nuevos meses (mayo 2026+)
- [ ] Consolidacion intra-sector para % provincias/ajuste mas preciso
