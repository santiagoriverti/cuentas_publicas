# Proyecto: cuentas_publicas

## Objetivo
Consolidar datos del Sector Público Nacional argentino (Hacienda) en un dataset tidy para análisis macro del ajuste fiscal y superávit primario, con desagregación por subsector institucional y transferencias a provincias.

## Fuente de datos
- URL: https://www.argentina.gob.ar/economia/sechacienda/infoestadistica
- Archivo original: sector_publico.zip.zip → data/raw/sector_publico.zip.zip (dentro del repo, gitignored)
- 75 archivos Excel (xls/xlsx), 2020-2026
- DOS tipos de informes por archivo: AIF + IMIG

## Repositorio GitHub
- URL: https://github.com/santiagoriverti/cuentas_publicas (rama: main)
- Notebook 01 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb
- Notebook 02 Colab: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb

## Estructura de los archivos Excel

### AIF (Esquema Ahorro-Inversión-Financiamiento)
- Hoja con "ESQUEMA AHORRO" o "SECTOR PUBLICO BASE CAJA" en primeras filas
- Columnas: TESORO NACIONAL | REC.AFECTADOS | ORG.DESCENTRALIZADOS | INST.SEG.SOCIAL | EX-CAJAS PVCIALES (hasta 2025) | TOTAL | PAMI/FDOS | [TOTAL GRAL desde 2026]
- Filas: I) INGRESOS CORRIENTES ... XV) RESULTADO FINANCIERO + sub-items con sangría
- Offset de encabezado varía por año (1-3 filas de headers)
- 2026: eliminan columna EX-CAJAS, añaden T O T A L (col I)
- Sub-items clave en los datos:
  - Corrientes a provincias: `.. Provincias y CABA` → II4b1_TRANSF_PROVINCIAS_CABA
  - Capital a provincias: `. A Provincias y CABA` → V2a_TRANSF_CAPITAL_PROVINCIAS
  - Diferencia clave: capital tiene ". A " antes de Provincias, corrientes tiene ".."

### IMIG (Informe Mensual de Ingresos y Gastos)
- Hoja con "INGRESOS TOTALES" como marcador
- Jerarquía en columnas: col base=nivel1, col base+1=nivel2, col base+2=nivel3
- Dos columnas de valores: mes actual + mismo mes año anterior
- La fecha aparece como datetime o Excel serial en el encabezado (rango válido: 2018-2026)

## Datasets actuales

### output/aif_consolidado.csv
- ~27.250 filas, columnas: fecha, anio, mes, periodo, concepto_codigo, concepto_descripcion, concepto_nivel, subsector, valor_millones_pesos, fuente_archivo
- 54 conceptos únicos (15 principales I-XV + ~40 sub-items)
- XIV_RESULTADO_PRIMARIO y XV_RESULTADO_FINANCIERO son los KPIs clave
- Para series largas: usar subsector=total_adm_nacional, periodo=mensual

### output/imig_consolidado.csv
- ~6.830 filas, 52 conceptos en 3 niveles jerárquicos
- nivel_jerarquia: 0=principal, 1=detalle, 2=subdetalle
- Incluye datos del año anterior de cada archivo (columna de comparación)

## Notebooks

### notebooks/01_consolidar.ipynb
- Lee CSVs desde GitHub (rama main), exporta Excel unificado descargable
- 5 hojas: AIF_mensual | AIF_acumulado | Resultado_pivot | Transferencias_provincias | IMIG
- Hoja Resultado_pivot: ingresos, gastos, intereses, prestaciones, resultado primario y financiero
- Hoja Transferencias_provincias: pivot por subsector, tipo=Corrientes/Capital

### notebooks/02_analisis_fiscal.ipynb
- Lee CSVs desde GitHub, genera visualizaciones
- Secciones: resultado primario/financiero, ingresos, gasto, transferencias, subsectores, resumen ajuste

## Arquitectura del código

### src/aif_parser.py
- parse_filename_date(): extrae (año, mes) del nombre de archivo
- detect_column_map(): detecta qué columna es cada subsector via regex en headers combinados
- _is_data_row(): detecta filas de datos por Roman numeral (col A) o sangría en col B RAW (sin strip)
- normalize_concepto(): mapea descripciones a códigos normalizados (orden importa: capital antes que corrientes)
- parse_aif_sheet(): parsea una hoja AIF completa
- parse_file(): entry point, maneja xls y xlsx

### src/imig_parser.py
- detect_value_columns(): fechas como datetime o serial Excel, rango 2018-2026
- parse_imig_sheet(): detecta concepto en cols base/base+1/base+2 según nivel
- parse_file(): entry point, ignora hojas Acumulado/Mensualizacion/Salida

### src/consolidate.py
- Lee ZIP de data/raw/, parsea todos los archivos, deduplica, guarda CSVs
- Uso sin parámetros: python src/consolidate.py (busca en data/raw/ por defecto)

## Flujo para agregar nuevos meses
1. Descargar Excel de Hacienda → copiar a data/raw/
2. python src/consolidate.py
3. git add output/ && git commit -m "datos: YYYY-MM" && git push
4. Abrir Notebook 01 en Colab → ya tiene los nuevos datos

## Bugs corregidos (historial)
- AIF sub-items: .strip() borraba sangría antes de contar nivel → col_b_raw sin strip
- IMIG jerarquía: solo leía col base, ignoraba cols base+1/base+2
- IMIG fechas: valores de ingresos confundidos con seriales Excel → restringir 2018-2026
- V2a capital provincias: patrón CAPITAL.*PROVINCIAS no matcheaba ". A Provincias y CABA"
  → patrón ". A PROVINCIAS Y CABA" con prioridad sobre "PROVINCIAS Y CABA"
- Rama master → main (fix Colab 404)
- Encoding notebooks → reescritos sin caracteres especiales

## Meses faltantes en datos fuente (no hay Excel en el ZIP)
- Noviembre 2021
- Septiembre 2022

## Hallazgos clave (2020-2026)
- 2020-2023: déficit primario persistente (COVID + gestión Fernández)
- 2024-2026: superávit primario consistente (gestión Milei)
  - Excepción: diciembre cada año (aguinaldos + cierre)
  - Abril 2026: resultado primario +273.621 MM ARS, financiero -88.190 MM ARS
- Transferencias corrientes Tesoro a Provincias/CABA (mensual, MM ARS):
  - 2024: caída real vs 2023 (ajuste discrecional)
  - Abr 2026: corrientes 84.448 MM, capital 470 MM (Tesoro)
- Intereses deuda: 362.249 MM ARS en abril 2026

## Pendiente / Próximas sesiones
- [ ] Deflactor IPC/IPM para series en pesos constantes
- [ ] Notebook 02: mejorar visualizaciones con datos IMIG (subsidios, prestaciones)
- [ ] Datos MECON de finanzas provinciales desagregadas por jurisdicción
- [ ] Análisis subsidios energéticos y transporte (disponible en IMIG)
- [ ] Exportar a Parquet para queries más rápidas
