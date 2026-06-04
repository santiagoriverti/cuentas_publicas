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

## Bug IMIG corregido (2026-06-04)
El patron r"IVA" en el normalizador matcheaba la subcadena "IVA" en "CONTRIBUTIVAS".
Esto causaba que Jubilaciones_pensiones y Pensiones_no_contributivas fueran normalizadas
incorrectamente como IVA_neto_reintegros.
Fix: mover jubilaciones/pensiones ANTES de IVA en el dict, usar r"\bIVA\b".
IMIG regenerado: 8.421 registros (era 7.950).

## Notebook 02 - Estado actual (post 2026-06-04)
Graficos (600 DPI, sin gap Jun-2022, etiquetas cada 3 meses en español):
  01_resultado_primario_financiero.png
  02_ajuste_componentes_2023_2025.png  (barras horizontales con valores)
  03_transferencias_provincias.png
  04_composicion_gasto_corriente.png
  05_composicion_ingresos.png
  06_torta_recorte_gasto.png          (PIE CHART: % por rubro)
Intereses deuda y subsectores: eliminados por solicitud.

Celdas de analisis completo (Celda 9):
  Tabla 1: Resultado fiscal anual 2020-2026 con % del PIB
  Tabla 2: Cuantificacion ajuste Milei 2023->2024/2025
  Tabla 3: Desglose funcional por rubro (IMIG):
    Obra publica, Subsidios, Transf.Provincias, Salarios,
    Jubilaciones, Universidades, Pensiones NC, PAMI, AUH

Excel 5 hojas: Serie_mensual | Resumen_anual | Transferencias_prov |
               Ajuste_AIF | Ajuste_IMIG_funcional

## Hallazgos IMIG (pesos constantes abr-2026, 2023->2025):
- AUH: 3.9 B -> 7.5 B = +3.6 B (+92%) - UNICA partida con gran aumento real
- Obra publica: 16.8 -> 3.8 = -13.0 B (-77%)
- Subsidios: 22.3 -> 10.6 = -11.7 B (-52%)
- Otros prog sociales: 21.5 -> 11.2 = -10.3 B (-48%)
- Salarios: 26.4 -> 20.7 = -5.7 B (-22%)
- Transf. provincias: 7.2 -> 3.0 = -4.2 B (-58%)
- Universidades: 7.2 -> 5.1 = -2.1 B (-29%)
- Jubilaciones: 64.0 -> 66.0 = +2.0 B (+3%) - leve aumento en 2025
- PAMI: 9.3 -> 9.8 = +0.5 B (+5%) - leve aumento

## Fix adicional (post-verificacion 2026-06-04)
- rubros_tabla usaba texto completo con acento para AUH ('Asignación Universal para 
  Protección Social') en lugar del codigo normalizado 'AUH'. Fix: usar 'AUH'.
- Agregado 'Otros_prog_sociales' a rubros_tabla (-10.3 B, 12.6% del ajuste).
- La torta ahora incluye 'Otros prog. sociales' y 'AUH' correctamente.

## Verificacion final de datos (2026-06-04):
- NB01 IMIG: 8.421 filas ✅ (datos correctos con jubilaciones y pensiones)
- NB02 Transferencias_prov: 300 filas ✅ (+8 respecto a antes por Nov-2021 y Sep-2022)
- NB02 Resultado_pivot 2024/2025: 0% diferencia con Hacienda ✅
- NB02 tabla rubros: 10 items incluyendo AUH y Otros_prog_sociales ✅

## Pendiente
- [ ] Datos provinciales MECON por jurisdiccion
- [ ] IPC: actualizar con nuevos meses cuando esten disponibles
- [ ] Consolidacion intra-sector para % provincias/ajuste mas preciso
