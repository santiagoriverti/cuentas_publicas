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
- Archivos sueltos adicionales en data/raw/ (gitignored, se procesan automaticamente):
  - resultado_fiscal_noviembre_2021.xls (recuperado)
  - resultado-fiscal_septiembre-2022.xlsx (recuperado)
  - resultado-fiscal_junio-2022.xlsx (acumulado I Semestre, IMIG mensual si)
- IPC INDEC: data/reference/IPC.xlsx (commiteado, ene-2017 a abr-2026)
- 78 archivos Excel procesados, 2020-2026

## Datasets actuales
- output/aif_consolidado.csv: 27.964 registros
- output/imig_consolidado.csv: 7.950 registros
- Cobertura: enero 2020 - abril 2026
- UNICO mes faltante: Jun-2022 AIF mensual (el archivo de Hacienda solo tiene acumulado I Semestre)
  - Jun-2022 IMIG mensual: SI disponible (estaba en el archivo en columnas multi-mes)

## Estructura de archivos
```
data/raw/          <- ZIP + nuevos Excel (gitignored). consolidate.py los lee todos.
data/reference/    <- IPC.xlsx (commiteado)
output/            <- CSVs generados (commiteados)
src/
  aif_parser.py    <- Parser AIF. Bug corregido: col_b_raw sin strip para sangria.
                     Patron ". A PROVINCIAS" con prioridad para capital vs corrientes.
  imig_parser.py   <- Parser IMIG. Jerarquia en cols base/+1/+2. Fechas "ene-22" soportadas.
  consolidate.py   <- iter_sources(): lee ZIP + archivos sueltos en data/raw/.
                     Resumen final lista meses faltantes automaticamente.
  deflate.py       <- load_ipc(), deflate_series(), deflate_df()
```

## Notebooks

### Notebook 01 - Consolidacion
- Lee CSVs de GitHub, exporta datos_fiscales_consolidado.xlsx (5 hojas)
- AIF_mensual | AIF_acumulado | Resultado_pivot | Transferencias_provincias | IMIG

### Notebook 02 - Analisis Fiscal
- Lee CSVs + IPC de GitHub. Todo corre en Colab sin subir archivos.
- Base deflacion: pesos constantes abril 2026
- Titulares: get_serie_total() = total_adm_nacional + pami_fdos_otros
- MESES_FALTANTES = ['2022-06-01'] (unico gap visible en graficos de barras)
- Graficos (600 DPI, sin titulo, etiquetas cada 3 meses en espanol, align=edge):
  01_resultado_primario_financiero.png
  02_ajuste_componentes_2023_2025.png
  03_transferencias_provincias.png
  04_composicion_gasto_corriente.png
  05_composicion_ingresos.png
  06_intereses_deuda.png
- Descarga final: analisis_fiscal.zip (6 PNG + Excel con 4 hojas)

## Validacion contra Hacienda oficial
| Año | Primario oficial | Nuestro | Financiero oficial | Nuestro |
|---|---|---|---|---|
| 2024 | +10.41 B | +10.4 B (0%) ✅ | +1.76 B | +1.8 B (2%) ✅ |
| 2025 | +11.77 B | +11.8 B (0%) ✅ | +1.45 B | +1.5 B (3%) ✅ |

## Nota metodologica: consolidacion intra-sector
Al sumar total_adm_nacional + pami_fdos_otros para gasto primario, el denominador
queda inflado por transferencias intra-sector. Esto afecta el % provincias/ajuste
(~9% nuestro vs ~16% en analisis consolidados). El resultado financiero NO se afecta.

## Flujo para nuevos meses
1. Descargar Excel de Hacienda -> copiar a data/raw/
2. python src/consolidate.py  (lista meses faltantes al final)
3. git add output/ && git commit -m "datos: YYYY-MM" && git push
4. Colab se actualiza automaticamente al ejecutar los notebooks

## Hallazgos clave (2020-2026, pesos abr-2026)
- 2020-2023: deficit primario (peor 2023: -27.3 B real)
- 2024: superavit +21.0 B real | 2025: +15.7 B real
- Ajuste 2023->2025: -42.3 B gastos corrientes + -6.0 B capital
  Subsidios: -17.7 B (-36.6%) | Salarios: -6.2 B (-12.9%)
  Transf. provincias: -5.0 B (-10.2%) | Universidades: -2.5 B (-5.2%)
- Transferencias a provincias: 4.0% del gasto en 2023 -> 1.7% en 2025

## Pendiente
- [ ] Analisis IMIG: AUH, subsidios energia/transporte desagregados
- [ ] Datos provinciales MECON por jurisdiccion
- [ ] IPC: actualizar con nuevos meses cuando esten disponibles
- [ ] Consolidacion intra-sector para % provincias/ajuste mas preciso
