# Proyecto: cuentas_publicas

## Objetivo
Consolidar datos del Sector Publico Nacional argentino (Hacienda) en un dataset tidy para analisis macro del ajuste fiscal y superavit primario, con desagregacion por subsector institucional y transferencias a provincias.

## Repositorio
- GitHub: https://github.com/santiagoriverti/cuentas_publicas (rama: main)
- Local: C:\Users\sriverti\Desktop\INECO\Repositorios\cuentas_publicas
- Notebook 01 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb
- Notebook 02 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb

## HANDOFF — estado al 2026-06-18 (para retomar en otro chat)
ESTADO: todo commiteado y pusheado a main (ultimo commit 5465e2a). Arbol git limpio.
Datos hasta MAYO 2026. Deflactor base = ultimo mes IPC = may-2026 (automatico).
Ambos notebooks ejecutan end-to-end sin errores y estan validados vs Hacienda y vs fuente cruda.

HECHO ESTE CICLO (jun-2026):
- Incorporado mayo 2026 (IPC + AIF + IMIG), re-consolidado, validado.
- Fix parser AIF: I2_APORTES_SEG_SOCIAL en formato viejo ("Contribuciones a la Seg.Social").
- consolidate.py: autodetecta ZIP (corre con `python src/consolidate.py`) + reporta huecos IMIG.
- NB02: agregadas 4 hojas nuevas al Excel -> Informe_tabla1, Informe_provincias,
  Informe_valores (tabla larga con TODO valor del informe), Tablas_LaTeX (5 bloques .tex).
  El ZIP ahora trae tambien 5 archivos .tex (filas de datos de cada tabla del informe).
- Mapeo completo de reemplazos base-abril -> base-may del documento LaTeX entregado en chat.

PROXIMO PASO ABIERTO (lo que quedo pendiente de hacer):
- Aplicar sobre el documento LaTeX del usuario (informe de prensa INECO) los reemplazos a
  base may-2026: rebasear todos los $billones (~+2.1%), cambiar "abril 2026"->"mayo 2026",
  cobertura a mayo, columna 2026 parcial (5 meses), %/pp del PIB NO cambian.
  Fuente de verdad = hojas Informe_valores y Tablas_LaTeX del Excel del NB02.
  El usuario tiene el .tex en su chat (no esta en el repo). Pedirselo de nuevo para editarlo.
- Decision pendiente del usuario: en el titulo, ajuste gasto primario 2023->2024 da -87,1 B
  por la regla sin-redondear; si prefiere que el lector lo verifique como 280,6-193,4 usar -87,2.

GAPS CONOCIDOS (no son bugs): AIF mensual falta jun-2022 (Hacienda solo publico acumulado);
IMIG falta mar-2026 (Hacienda no publico IMIG ese mes; permanente; no afecta graficos).

SEGURIDAD: el token del remote estaba vencido; los push de este ciclo se hicieron con un PAT
nuevo pasado por chat (one-time URL, sin guardarlo). Conviene rotar ese token y limpiar el
remote para que use Git Credential Manager.

## Fuente de datos
- URL: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica
- ZIP: data/raw/sector_publico.zip (gitignored). consolidate.py AUTODETECTA
  data/raw/sector_publico*.zip -> ya NO hace falta pasar --zip. Correr:
  `python src/consolidate.py`
- Archivos sueltos en data/raw/ (gitignored): Nov-2021, Sep-2022, Jun-2022
- IPC INDEC: data/reference/IPC.xlsx (commiteado, ene-2017 a may-2026)
- 80 archivos Excel, cobertura ene-2020 a may-2026
- Gap unico AIF mensual: Jun-2022 (solo existe acumulado I Semestre)
- Gap unico IMIG: 2026-03. PERMANENTE: Hacienda NO publico informe IMIG de marzo 2026,
  solo el AIF (marzo_26.xlsx, hojas Marzo/Acumulado, sin IMIG). Confirmado con el usuario
  (2026-06-18). No se puede reconstruir desde el AIF (desagregacion funcional distinta).
  No afecta graficos (IMIG solo usa 2023-2025 anual). NO volver a marcarlo como "a descargar".
- AIF marzo 2026 VALIDADO contra fuente cruda: 16 conceptos x subsector coinciden exacto
  (Adm.Nacional, Total general, Tesoro), incl. I2_APORTES_SEG_SOCIAL
- IMIG 2026 viene en archivos separados por mes: ene/feb en sector_publico_base_caja_*_2026
  (hoja IMIG), abril=IMIG Abril 2026.xlsx, mayo=imig_mayo_2026.xlsx, MARZO=ausente
- En Windows correr con PYTHONUTF8=1 (los prints usan flecha unicode -> crash cp1252)

## Datasets
- output/aif_consolidado.csv: 28.664 registros (incluye may-2026)
- output/imig_consolidado.csv: 8.529 registros (incluye may-2026)
- Validado vs Hacienda: 2024 y 2025 con 0.00% diferencia en primario y financiero
- Deflactor base = ultimo mes IPC (auto). Tras agregar may-2026, base = may-2026
  (antes abr-2026). Bloque "Hallazgos clave" abajo ya recomputado en base may-2026

## Estructura de codigo
```
src/
  aif_parser.py    <- Parser AIF. Bugs corregidos: sangria, patrones IVA/CONTRIBUTIVAS
  imig_parser.py   <- Parser IMIG. Jerarquia multi-columna, fechas "ene-22", \bIVA\b
  consolidate.py   <- iter_sources(): ZIP + archivos sueltos. Autodetecta ZIP +
                      reporta huecos mensuales AIF e IMIG en el resumen
  deflate.py       <- Utilidades de deflacion IPC (helper standalone, no usado por NB)
data/reference/
  IPC.xlsx         <- IPC Nivel General INDEC ene-2017 a may-2026 (commiteado)
```

## Auditoria exhaustiva fuentes (2026-06-18)
- 80 archivos fuente revisados. 34 conceptos AIF normalizados cubren los 76 meses en
  total_adm_nacional SIN huecos (tras fix I2). Subsectores clave (tesoro, pami) OK.
- 0 nulos en AIF/IMIG. Validacion Hacienda 2024/2025 intacta (primario/financiero <0.3%).
- Ambos notebooks ejecutados celda-por-celda end-to-end: 0 errores, 7 PNG + Excel + ZIP.
- Fragmentacion cosmetica (NO afecta nada): filas detalle/subdetalle con notas al pie
  "(2)/(3)" quedan como texto crudo separado (ej. SUPERAVIT OP. EMPRESAS PUB / ...(3),
  . INTERESES (2), XVI INGRESOS EXTRAORDINARIOS (3)). Los principales se leen directo
  del Excel, NO se suman de detalles -> totales correctos. Dejado asi a proposito.
- Sin pendientes de datos: IMIG marzo 2026 no existe en origen (gap permanente, ver arriba).

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

Excel (7 hojas): Serie_mensual | Resumen_anual | Transferencias_prov |
                 Ajuste_AIF_anual | Ajuste_IMIG_rubros |
                 Informe_tabla1 | Informe_provincias
- Informe_tabla1 (2026-06-18): tabla macro lista para informe, 1 fila/anio 2020-2026,
  desde df_macro: ingresos/gasto_primario/intereses_netos/primario/financiero (B, 1 dec)
  + primario_pct_PIB + financiero_pct_PIB. Construida en celda 9, exportada en celda 10.
- Informe_provincias (2026-06-18): transf. a prov subsector total_adm_nacional, real, B,
  corrientes/capital/total + pct_gasto_primario (vs Gasto_real Sector Publico Total).
  REGLA: total y pct se calculan desde valores SIN redondear (suma cruda -> 2024=2,7/1,4%,
  no 2,6/1,3%). Misma regla en Informe_valores y Tablas_LaTeX.
- Informe_valores (2026-06-18): tabla larga (seccion/clave/descripcion/valor_num/valor_fmt/
  unidad) con TODOS los valores citados en el informe LaTeX. unidad in {B,%,pp_PIB,meses,texto}.
- Tablas_LaTeX (2026-06-18): columna 'latex' con los 5 bloques de filas de datos de las tablas
  del informe (tab:01, composicion_gasto, ing_gasto_anual, prov, imig), encabezados "% === label ===".
  Tambien escribe 5 .tex en disco -> al ZIP. Ahora ZIP = Excel + 7 PNG + 5 .tex (13 archivos).
- *.tex y *.png en .gitignore (generados).
- Edicion de celdas 9/10 se hizo via JSON con Python (splitlines keepends), NO NotebookEdit.
- OJO base may-2026 + regla sin-redondear: gp_ajuste 2023->2024 = -87,1 B (doc decia -87,2 por
  restar redondeados); torta salarios 12,0 / transf 8,9 / otros 21,7 (doc 12,1/8,7/21,8). Correcto.

Descarga: analisis_fiscal.zip (7 PNG + Excel)

Comparacion del ajuste: ANUAL 2023 vs 2024/2025 (anos completos, robusta)
NO usar comparacion mensual dic-23: sesgo alto por estacionalidad de diciembre

ESTADO FINAL VERIFICADO (2026-06-05):
- Excel 5 hojas, sin nulls, 0.00% diferencia vs Hacienda 2024/2025
- 7 graficos limpios, leyendas corregidas (verde/rojo en G01, sin titulo en G06,
  4 colores en G07 con legend en lower right)
- Graficos 05/06/07 usan comparacion anual
- Notebook completo sin errores, listo para uso en informe tecnico

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

## Hallazgos clave verificados (pesos constantes may-2026, run 2026-06-18)

### Macro - Sector Publico Total (AIF):
- Gasto primario: 280.6 B (2023) → 193.4 B (2024) → 197.2 B (2025) | 2026 parcial ene-may: 72.9 B
- Reduccion: -31.1% en 2024 vs 2023 | -29.7% en 2025 vs 2023
- Resultado primario: -27.9 B (2023) → +21.5 B (2024) → +16.1 B (2025) | 2026 parcial: +8.6 B
- Mejora primaria 2023→2024: +49.4 B | 2023→2025: +44.0 B
- Resultado financiero: -48.0 B (2023) → +4.3 B (2024) → +2.5 B (2025) | 2026 parcial: +2.6 B
- Validacion nominal vs Hacienda intacta: primario 2024 10.41 B / 2025 11.77 B (0.00%)

### Mensual dic-2023 → may-2026 (AIF, Adm. Nacional):
ATENCION: dic-2023 es mes de alto gasto estacional (aguinaldo), caidas % magnificadas
OJO endpoint: may-2026 es mes de CUPON de deuda (intereses altos) → intereses sale +7.1%
(artefacto estacional del mes final; usar comparacion ANUAL para intereses)
- Gastos corrientes: 18.4 → 12.3 B = -6.1 B (-33.3%)
- Intereses: 1.3 → 1.4 B = +0.1 B (+7.1%)  <- distorsion por cupon de mayo
- Subsidios: 4.6 → 2.4 B = -2.3 B (-48.7%)
- Remuneraciones: 2.9 → 1.4 B = -1.4 B (-50.6%)
- Prestaciones: 6.9 → 5.7 B = -1.2 B (-17.8%)
- Resultado primario: -7.1 → +1.4 B = +8.5 B

### Funcional dic-2023 → may-2026 (IMIG):
- AUH: +0.4 B (+174.4%) <- UNICO rubro con gran suba
- PAMI: flat (+0.1%)
- Salarios: -1.7 B (-51.6%)
- Obra publica: -0.8 B (-82.0%)
- Subsidios: -1.5 B (-66.0%)
- Jubilaciones: -1.2 B (-18.0%)
- Transf. Provincias: -0.8 B (-83.5%)
- Universidades: -0.4 B (-35.4%)
- Otros prog. sociales: -0.9 B (-47.9%)
- Total baja: -7.3 B | Total suba: +0.4 B | Neto: -7.0 B

## Bugs corregidos (historial completo)
- AIF: sangria en col_b borrada por .strip() → usar col_b_raw
- AIF: ". A PROVINCIAS" patron capital vs corrientes
- AIF: I2_APORTES_SEG_SOCIAL no capturado en 2021-05/06 y 2022-05/07/08 (formato viejo
  "- Contribuciones a la Seg. Social" sin "Aportes y") → patron ampliado a
  "APORTES Y CONTRIB.*SEG|CONTRIBUCIONES A LA SEG". Eliminaba un codigo huerfano y
  dejaba huecos en grafico 03 (Seg.Social). Unico hueco legitimo restante: 2022-06 (gap global)
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
- [ ] PRINCIPAL: aplicar reemplazos base may-2026 al documento LaTeX del informe INECO
      (ver seccion HANDOFF; pedir el .tex al usuario). Fuente: hojas Informe_valores / Tablas_LaTeX.
- [ ] Datos provinciales MECON por jurisdiccion
- [x] IPC actualizado a may-2026 (2026-06-18)
- [ ] IPC: actualizar cuando salgan nuevos meses (junio 2026+)
- [ ] Consolidacion intra-sector para % provincias/ajuste mas preciso
- [ ] Seguridad: rotar PAT expuesto en chat + limpiar token del remote (usar GCM)
