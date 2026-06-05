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
- ZIP original: data/raw/sector_publico.zip.zip (gitignored)
- Archivos sueltos adicionales en data/raw/ (gitignored):
  - resultado_fiscal_noviembre_2021.xls
  - resultado-fiscal_septiembre-2022.xlsx
  - resultado-fiscal_junio-2022.xlsx (AIF solo tiene acumulado; IMIG si tiene mensual)
- IPC INDEC: data/reference/IPC.xlsx (commiteado, ene-2017 a abr-2026)
- 78 archivos Excel procesados, 2020-2026

## Datasets actuales (estado: 2026-06-04)
- output/aif_consolidado.csv: 27.964 registros
- output/imig_consolidado.csv: 8.421 registros (8.421 raw, ~4.706 tras dedup en runtime)
- Cobertura: enero 2020 - abril 2026
- UNICO gap AIF mensual: Jun-2022 (solo existe acumulado I Semestre)
- IMIG: cubre los 12 meses de 2022 (Jun-2022 recuperado del formato multi-columna)

## Estructura de archivos
```
data/raw/          <- ZIP + nuevos Excel (gitignored). consolidate.py los lee todos.
data/reference/    <- IPC.xlsx (commiteado)
output/            <- CSVs generados (commiteados)
src/
  aif_parser.py    <- Parser AIF. col_b_raw sin strip; ". A PROVINCIAS" prioridad capital.
  imig_parser.py   <- Parser IMIG. Jerarquia en cols base/+1/+2. Fechas "ene-22".
                     BUG CORREGIDO: r"\bIVA\b" evita match en "CONTRIBUTIVAS".
                     Jubilaciones y Pensiones NC ahora capturadas correctamente.
  consolidate.py   <- iter_sources(): ZIP + archivos sueltos. Muestra gaps al final.
  deflate.py       <- load_ipc(), deflate_series(), deflate_df()
```

## Notebooks

### Notebook 01 - Consolidacion (01_consolidar.ipynb)
Lee CSVs de GitHub. Exporta datos_fiscales_consolidado.xlsx (5 hojas):
- AIF_mensual: todos los conceptos x subsector, periodicidad mensual
- AIF_acumulado: idem acumulado
- Resultado_pivot: KPIs Sector Publico Total (Adm.Nac + PAMI) en columnas
- Transferencias_provincias: corrientes Y capital, pivot por subsector
- IMIG: detalle funcional completo (8.421 registros)

### Notebook 02 - Analisis Fiscal (02_analisis_fiscal.ipynb)
Lee CSVs + IPC de GitHub. Todo corre en Colab sin subir archivos.
Base deflacion: pesos constantes de abril 2026.
Titulares: get_serie_total() = total_adm_nacional + pami_fdos_otros.
Gap Jun-2022 removido con drop_gap() + posiciones enteras en barras.

Graficos (600 DPI, etiquetas cada 3 meses en español, sin titulo principal):
  01_resultado_primario_financiero.png   <- barras primario + linea financiero
  02_ajuste_componentes_2023_2025.png    <- barras horiz con valor+% del ajuste
  03_transferencias_provincias.png       <- barras apiladas corrientes+capital
  04_composicion_gasto_corriente.png     <- barras apiladas 6 componentes
  05_composicion_ingresos.png            <- barras apiladas 3 componentes
  06_torta_recorte_gasto.png             <- torta % de cada rubro en el recorte

Celdas de analisis (Celda 9):
  Tabla 1: Resultado fiscal anual 2020-2026 con % del PIB
  Tabla 2: Cuantificacion ajuste Milei (dic-2023 en adelante)
  Tabla 3: Desglose funcional 10 rubros (IMIG):
    Obra publica, Subsidios, Transf.Provincias, Salarios, Jubilaciones,
    Universidades, Pensiones NC, PAMI, Otros_prog_sociales, AUH
    Cada uno: valor 2023/2024/2025, variacion absoluta, % real, % del ajuste

Excel 5 hojas: Serie_mensual | Resumen_anual | Transferencias_prov |
               Ajuste_AIF | Ajuste_IMIG_funcional

Descarga: analisis_fiscal.zip (6 PNG + Excel)

## Validacion contra Hacienda oficial (nominal)
| Año | Primario oficial | Nuestro | Financiero oficial | Nuestro |
|---|---|---|---|---|
| 2024 | +10.41 B | +10.4 B (0%) ✅ | +1.76 B | +1.8 B (2%) ✅ |
| 2025 | +11.77 B | +11.8 B (0%) ✅ | +1.45 B | +1.5 B (3%) ✅ |

## PIB nominal hardcodeado en Notebook 02 (billones ARS)
2020: 44.9 | 2021: 72.0 | 2022: 115.0
2023: 143.2 (Hacienda: deficit 8.74B = -6.1% PIB)
2024: 586.7 (Hacienda: superavit 1.76B = +0.3% PIB)
2025: 725.0 (Hacienda: superavit 1.45B = +0.2% PIB)

## Hallazgos clave (pesos constantes abr-2026)

### Macro (AIF, Sector Publico Total):
- 2020-2023: deficit primario (peor 2023: -27.3 B real)
- 2024: superavit primario +21.0 B | 2025: +15.7 B
- Gasto primario: 274.6 B (2023) → 189.4 B (2024) → 193.0 B (2025)
- Reduccion gasto 2023→2024: -85.3 B (-31.1%)
- Reduccion gasto 2023→2025: -81.6 B (-29.7%)

### Funcional (IMIG):
- AUH: 3.9 → 7.5 B = +3.6 B (+92%) ← UNICA partida con gran aumento real
- Obra publica: 16.8 → 3.8 = -13.0 B (-77%)
- Subsidios: 22.3 → 10.6 = -11.7 B (-52%)
- Otros prog sociales: 21.5 → 11.2 = -10.3 B (-48%)
- Salarios: 26.4 → 20.7 = -5.7 B (-22%)
- Transf. provincias: 7.2 → 3.0 = -4.2 B (-58%)
- Universidades: 7.2 → 5.1 = -2.1 B (-29%)
- Jubilaciones: 64.0 → 66.0 = +2.0 B (+3%) - leve aumento en 2025
- PAMI: 9.3 → 9.8 = +0.5 B (+5%)
- Pensiones NC: 5.9 → 5.5 = -0.4 B (-7%)

## Bugs corregidos (historial)
- AIF: .strip() en col_b borraba sangria → col_b_raw
- AIF: V2a capital provincias mal matcheado → ". A PROVINCIAS" prioridad
- IMIG: solo leia col base → ahora base/+1/+2
- IMIG: fechas 2027+ por seriales Excel → rango 2018-2026
- IMIG: r"IVA" matcheaba "CONTRIBUTIVAS" → r"\bIVA\b" + orden correcto
- IMIG: AUH normalizacion con acento → r"ASIGNACI.N UNIVERSAL"
- NB01: Resultado_pivot usaba solo total_adm_nacional → get_total_pivot()
- NB01: get_total() perdía nombre de Serie → get_total_pivot() con concat
- Rama master → main (fix Colab 404)

## Flujo para nuevos meses
1. Descargar Excel de Hacienda → copiar a data/raw/
2. python src/consolidate.py (muestra gaps detectados automaticamente)
3. git add output/ && git commit -m "datos: YYYY-MM" && git push
4. Colab se actualiza automaticamente

## Pendiente / Proximas sesiones
- [ ] Datos provinciales MECON desagregados por jurisdiccion
- [ ] IPC: actualizar cuando salgan nuevos meses (mayo 2026+)
- [ ] Consolidacion intra-sector para % provincias/ajuste mas preciso (~15% real vs ~9% nuestro)
