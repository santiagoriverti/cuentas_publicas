# Proyecto: cuentas_publicas

## Objetivo
Consolidar datos del Sector Público Nacional argentino (Hacienda) en un dataset tidy para análisis macro del ajuste fiscal y superávit primario, con desagregación por subsector institucional y transferencias a provincias.

## Fuente de datos
- URL: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica
- Archivo original: sector_publico.zip.zip (C:\Users\sriverti\Downloads\deficit\)
- 75 archivos Excel (xls/xlsx), 2020-2026
- DOS tipos de informes por archivo: AIF + IMIG

## Estructura de los archivos Excel

### AIF (Esquema Ahorro-Inversión-Financiamiento)
- Hoja con "ESQUEMA AHORRO" o "SECTOR PUBLICO BASE CAJA" en primeras filas
- Columnas: TESORO NACIONAL | REC.AFECTADOS | ORG.DESCENTRALIZADOS | INST.SEG.SOCIAL | EX-CAJAS PVCIALES (hasta 2025) | TOTAL | PAMI/FDOS | [TOTAL GRAL desde 2026]
- Filas: I) INGRESOS CORRIENTES ... XV) RESULTADO FINANCIERO + sub-items
- Offset de encabezado varía por año (1-3 filas de headers)
- 2026: eliminan columna EX-CAJAS, añaden T O T A L (col I)

### IMIG (Informe Mensual de Ingresos y Gastos)
- Hoja con "INGRESOS TOTALES" como marcador
- Columna de conceptos en jerarquía (sangría indica nivel)
- Dos columnas de valores: mes actual + mismo mes año anterior
- La fecha aparece como datetime o Excel serial en el encabezado

## Datasets generados

### output/aif_consolidado.csv
- ~8.000 filas, columnas: fecha, anio, mes, periodo, concepto_codigo, concepto_descripcion, concepto_nivel, subsector, valor_millones_pesos, fuente_archivo
- Conceptos principales: I a XV (romanos), más sub-items
- XIV_RESULTADO_PRIMARIO y XV_RESULTADO_FINANCIERO son los KPIs clave
- Para series largas: usar subsector=total_adm_nacional, periodo=mensual

### output/imig_consolidado.csv
- ~650 filas, columnas: fecha, anio, mes, concepto_codigo, concepto_descripcion, nivel_jerarquia, valor_millones_pesos, fuente_archivo
- Incluye datos del año anterior de cada archivo (dos valores por fila histórica)

## Hallazgos clave (2020-2026)

### Resultado Primario Total Adm. Nacional (XIV, mensual, MM ARS):
- 2020: déficit todo el año (COVID), máx déficit -300.000 MM en mayo
- 2021: mixto, déficit en mayoría de meses
- 2022-2023: déficit persistente
- 2024-2025: superávit primario consistente (gestión Milei)
  - 2024: +1.9 billones enero, promedio mensual ~+700.000 MM
  - 2025: superávit similar o mayor
  - Excepción: diciembre con déficit (pago aguinaldos y cierre)
- 2026: superávit sostenido (3.29 B enero, 1.1 B febrero)

### Transferencias a Provincias/CABA (Tesoro, corrientes):
- Caída nominal en 2024 vs 2023 en términos reales (ajuste discrecional)

## Arquitectura del código

### src/aif_parser.py
- parse_filename_date(): extrae (año, mes) del nombre de archivo
- detect_column_map(): detecta qué columna es cada subsector via regex en headers
- parse_aif_sheet(): parsea una hoja AIF completa
- parse_file(): entry point, maneja xls y xlsx

### src/imig_parser.py
- detect_value_columns(): encuentra columnas con fechas (datetime o Excel serial)
- parse_imig_sheet(): parsea una hoja IMIG
- parse_file(): entry point

### src/consolidate.py
- Extrae ZIP, parsea todos los archivos, deduplica, guarda CSVs
- Uso: python src/consolidate.py --zip <ruta_zip>

## Repositorio GitHub
- URL: https://github.com/sriverti/cuentas_publicas
- Link Colab: https://colab.research.google.com/github/sriverti/cuentas_publicas/blob/main/notebooks/01_analisis_fiscal.ipynb

## Pendiente / Próximas sesiones
- [ ] Agregar deflactor (IPC o IPM) para series en pesos constantes
- [ ] IMIG tiene pocos conceptos normalizados — mejorar la jerarquía funcional de gastos
- [ ] Añadir datos MECON de finanzas provinciales desagregadas por jurisdicción
- [ ] Análisis de subsidios energéticos y transporte (dato disponible en IMIG 2026)
- [ ] Transferencias Tesoro a Provincias: mapear educación, salud, seguridad social
- [ ] Exportar a Parquet para queries más rápidas en análisis grandes
- [ ] Verificar meses faltantes: septiembre 2023 tiene archivo xls; no hay octubre/noviembre 2021
