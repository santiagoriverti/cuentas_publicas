# ESTADO DEL PROYECTO — cuentas_publicas

> Punto de entrada para retomar el trabajo en otra sesion o en otra PC.
> Ultima actualizacion: **2026-10-06**. Siguiente tarea: **septiembre 2026** cuando lo publique Hacienda (seccion 5).

El repo tiene dos productos:
1. **Analisis fiscal** (notebooks 01-02): ajuste del Sector Publico Nacional en pesos constantes.
2. **Indice Macroeconomico** (notebook 03): indice mensual 2004-hoy, 19 variables en 6 pilares. **Circula**:
   su nota metodologica esta en el README.

## 1. Donde estamos

| Item | Estado |
|---|---|
| Datos AIF + IMIG | **hasta agosto 2026** (79 meses AIF mensuales; IMIG completo 2019-01 a 2026-08) |
| IPC (deflactor) | hasta agosto 2026 → base de todos los valores reales: **ago-2026** (IPC 12.276,766) |
| Notebook 02 | Verificado en Colab (2026-09-22): 0 errores, ZIP = Excel 11 hojas + 7 PNG |
| Notebook 03 (indice macro) | **v9, metodologia congelada**; con rango de sensibilidad. Verificado en Colab (2026-10-06): identico a local en las 8 hojas; control de calidad 0 ALERTAS. ZIP = Excel 8 hojas + 4 PNG |
| Indice publicado | `output/indice_macro.csv` (2004-01 a 2026-08), lo actualiza `control_calidad.py --guardar` |
| Series macro externas | `data/reference/macro_mensual.csv`: 36 columnas (28 descargadas + 4 de reservas netas + 4 de la AIF historica 2003-2015), 2003 a oct-2026; pasivos del BCRA a mano en `reservas_pasivos_manual.csv` |
| Validacion vs Hacienda | Primario 2024 = 10,41 B y 2025 = 11,77 B nominales (0% dif.); financiero 1,76 / 1,45 B |
| Repo | Autocontenido: fuentes crudas en `data/raw/`, `consolidate.py` reproduce los CSV byte a byte |
| Ultimo mes publicado por Hacienda revisado | agosto 2026 (julio 2026 NO publicado → derivado) |

### Cifras clave del analisis fiscal (pesos constantes de ago-2026, Sector Publico Total)

| | 2023 | 2024 | 2025 | 2026 (ene-ago) |
|---|---|---|---|---|
| Ingresos totales (B) | 267,2 | 227,3 | 225,5 | 143,5 |
| Gasto primario (B) | 296,7 | 204,6 | 208,5 | 130,1 |
| Resultado primario (B) | −29,5 | +22,7 | +17,0 | +13,3 |
| Resultado financiero (B) | −50,8 | +4,6 | +2,6 | +2,6 |
| Primario % PIB | −2,7% | +1,8% | +1,4% | n/d |

Ajuste del gasto primario: **−31,1%** 2023→2024 y −29,7% 2023→2025.
IMIG 2023→2025: baja total −61,3 B (obra publica −15,4; subsidios −13,6; otros prog. sociales −12,8;
salarios −8,1; transf. provincias −4,9); unica suba AUH +3,4 B.

## 2. Indice Macroeconomico: estado actual (ago-2026)

Cifras = las que **imprime el notebook** (no re-redondear el Excel, que viene a 3 decimales).

| Ago-2026 | Valor | Hace 12 meses |
|---|---|---|
| Indice (6 pilares, 19 variables) | **−0,01** (rango de sensibilidad −0,11 a +0,34) | +0,23 |
| Indice sin fiscal (referencia) | −0,08 | +0,18 |
| Indice con Precios vs meta 10% (`indice_ancla`) | −0,25 | −0,01 |

- Pilares: Actividad −0,66 · Empleo −0,37 · Precios +0,33 (vs meta: −1,11) · Fiscal +0,33 · Externo −0,19 ·
  Financiero +0,50. Cambio en 12 meses −0,24 (−0,35 a −0,13 segun la variante).
- **Como comunicarlo:** "cerca de lo tipico y en baja". El signo del mes NO es concluyente (el rango cruza
  el 0); la caida del ultimo anio si es robusta.
- Promedio por gestion (indice completo): N. Kirchner +0,04 · C. Fernandez +0,17 · C. Fernandez II +0,06 ·
  Macri −0,30 · A. Fernandez −0,79 · Milei −0,28 (sin fiscal: −0,02 · +0,09 · +0,01 · −0,17 · −0,77 · −0,36).
- **Robustez** (`scripts/sensibilidad_indice.py`, 33 variantes): forma historica firme (corr. 0,90-1,00);
  A. Fernandez ultimo en todas; los tres gobiernos kirchneristas arriba de Macri, Milei y A. Fernandez en
  todas (NK vs Milei 97%). **No firmes:** NK vs CFK II y Macri vs Milei.
- **Validacion:** 7 recesiones 2008-2024 (regla UTDT sobre el EMAE tendencia-ciclo): el indice cae en todas
  (AUC 0,67); Spearman con el indice de miseria −0,56.

### Historial de versiones del indice (todas del 2026-10-06; detalle en CONTEXTO.md §4b)

| Version | Cambio | Efecto principal |
|---|---|---|
| v1 | Indice inicial: 16 series, 6 pilares, z robusto (IQR) | — |
| v2 | IPC Neuquen 2007-15, expectativas UTDT 2006-16, blue 2011-12, fiscal desde 2016, credito/PIB, hoja Arrastrados | revision de estructura |
| v3 | Fiscal sin extraordinarios (DEG 2021, rentas 2022, rec. extraordinarios 2026), credito real solo en pesos, blue de Ambito, UTDT ajustada al REM, `indice_ancla` | primario % PIB = oficial |
| v4 | Mediana/IQR solo sobre datos propios; PCA evaluado y descartado | max 0,02 |
| v5 | **Reservas netas** (reemplazan a las brutas) | max 0,15 (2004) |
| v6 | **Saldo comercial en % del PIB** en dolares; PIB nominal desde 2004 (serie 4.4) | ago-26 +0,19 → +0,14 |
| v7 | **Pilar fiscal desde 2004** (AIF historica llevada a la metodologia 2017) | ago-26 +0,14 → +0,00; el indice completo compara todas las gestiones |
| v8 | **EMAE vs su maximo de 36 meses** (nivel, no solo ritmo) | max 0,20 (may-2021) |
| v9 | **Salario real vs su maximo de 36 meses**; metodologia congelada | max 0,07 |
| circulacion | Rango de sensibilidad (12 variantes) en el NB03, `control_calidad.py`, `output/indice_macro.csv`, nota en el README | no cambia el indice |

Tambien en oct-2026: **bug del PIB del NB02 corregido** (`PIB_B`, celda 9: 2023 era 143,2 B y es 193,9 B;
cambian los % PIB, no los valores en B).

## 3. Ciclo anterior (sep-2026)

- Incorporados junio y agosto 2026. **Julio 2026 no fue publicado por Hacienda** → AIF derivado de
  acumulados (validado exacto) e IMIG desde la hoja `Mensualizacion`. Marzo 2026 IMIG tambien
  recuperado por esa via (antes figuraba como gap permanente).
- IMIG: ahora **una sola fuente por mes** (publicacion original > Mensualizacion > comparativa revisada).
- **Bug corregido** en `imig_parser.detect_value_columns`: marzo 2023 tenia valores de mayo 2019
  (un dato ~45.000 se leia como fecha serial Excel). Subestimaba ~5% los rubros IMIG 2023.
- NB02: tabla 1 usa **Ingresos totales (XI)**; graficos 02/05/06/07 con leyendas y colores corregidos;
  descarga sin archivos LaTeX y con los datos consolidados completos en el Excel.
- Fuentes crudas versionadas; scripts `actualizar_ipc.py` y `run_notebooks_local.py`.

## 4. Proximos pasos

1. **Septiembre 2026** cuando lo publique Hacienda → rutina mensual (seccion 5). Cuando INDEC publique el
   PIB anual 2026, agregarlo a `PIB_B` del NB02 (el NB03 lo toma solo de la API).
2. **Indice macro: metodologia congelada (v9).** Cambiarla solo ante un sesgo verificado en los datos y con
   acuerdo del usuario; si cambia: actualizar la nota del README, CONTEXTO §4b, correr
   `sensibilidad_indice.py` y `control_calidad.py --guardar`. Pagina interactiva/dashboard: **no por ahora**
   (pedido del usuario). SEDESA en las reservas netas solo si aparece una serie publica.
3. *(En pausa por pedido del usuario)* Informe LaTeX de prensa: rebasear a la base vigente. El `.tex` NO
   esta en el repo (lo tiene el usuario). La celda 9 del NB02 sigue calculando `Informe_valores` y
   `Tablas_LaTeX` (no se exportan). Decision pendiente: ajuste con regla "sin redondear" vs resta de
   valores redondeados (difieren en 0,1 B).
4. Ideas no iniciadas: datos provinciales MECON por jurisdiccion; consolidacion intra-sector para medir
   mejor el peso de las provincias en el ajuste.
5. Seguridad: el remote usa Git Credential Manager (push funciona). Si quedo algun PAT viejo en GitHub
   (usado en jun-2026), revocarlo en Settings → Developer settings → Tokens.

## 5. Rutina mensual (checklist)

```bash
git pull                                       # 0. siempre (hay commits desde mas de una PC)
# 1. copiar los Excel nuevos de Hacienda a data/raw/ (sin renombrar)
python scripts/actualizar_ipc.py               # 2. IPC nuevo (API datos.gob.ar)
python scripts/actualizar_macro.py             # 3. series del indice macro; revisar que no diga "FALLO"
                                               #    si el BCRA tomo/cancelo un REPO o swap: reservas_pasivos_manual.csv
python src/consolidate.py                      # 4. revisar "RESUMEN DE COBERTURA" al final
python scripts/run_notebooks_local.py 02 03    # 5. correr los notebooks con los archivos locales (_local_run/)
python scripts/control_calidad.py              # 6. control del indice: 0 ALERTAS (o explicarlas)
python scripts/control_calidad.py --guardar    #    actualiza output/indice_macro.csv (indice publicado)
python scripts/sensibilidad_indice.py          # 7. (opcional) robustez completa
git add data/raw data/reference output && git commit -m "datos: YYYY-MM" && git push
# 8. Colab: notebook 02 -> analisis_fiscal.zip; notebook 03 -> indice_macro.zip
# 9. Actualizar este archivo (seccion 1 y 2) y, si cambiaron cifras citadas, el ejemplo de la nota del README
```

Que revisar:
- **Paso 4:** `Meses SIN datos` debe listar solo `2022-06`. Si aparece un mes nuevo, ver si Hacienda lo
  salteo (la derivacion necesita el acumulado del mes siguiente) o si falta copiar un archivo.
  `Cobertura mensual IMIG: completa`; si falta un mes, buscar el Excel IMIG aparte o esperar al siguiente
  (su hoja `Mensualizacion` lo trae). Si Hacienda cambia el formato, revisar `CONCEPTO_NORMALIZE`
  (`src/aif_parser.py`) / `CONCEPTO_IMIG_NORMALIZE` (`src/imig_parser.py`).
- **Paso 6:** ALERTA = dato de mas de 2 anios que cambio > 5%, dato reciente que cambio > 25%, serie que
  perdio meses, salto atipico en un dato nuevo, o indice ya publicado revisado > 0,10. Los avisos son
  informativos (EMAE/SIPA desestacionalizados y PIB se revisan siempre). Si ya commiteaste las series,
  comparar con `--contra HEAD~1`.
- **Paso 8:** si el usuario pasa el ZIP de Colab, compararlo hoja por hoja con `_local_run/indice_macro.xlsx`
  y correr `control_calidad.py --excel <ruta del Excel de Colab>` (deberia dar identico y 0 ALERTAS).

## 6. Empezar en una PC nueva

```bash
git clone https://github.com/santiagoriverti/cuentas_publicas.git
cd cuentas_publicas
pip install -r requirements.txt
```

- Windows: definir `PYTHONUTF8=1` (prints con unicode rompen en cp1252).
- Push con Git Credential Manager (pide login de GitHub la primera vez; Claude no ingresa tokens).
- `_local_run/` (salidas locales) y `data/raw/_duplicados/` no estan en git: se regeneran o no hacen falta.
- Claude: leer `CLAUDE.md` (reglas) → este archivo → `CONTEXTO.md` si hay que tocar calculos.

## 7. Gaps conocidos (no son bugs)

- **AIF mensual jun-2022**: Hacienda solo publico el acumulado del I semestre y no hay acumulado de
  mayo 2022 → no se puede derivar. Los graficos lo saltean (`GAP_DATE` en celda 1 del NB02).
- IMIG antes de 2019: no disponible en el repo (el indice usa la AIF historica 2003-2015 y la IMIG de
  datos.gob.ar 2016-2018).
- Divisiones del IPC: solo informativas (los notebooks usan solo "Nivel general").
- Indice macro: desocupacion 2015-T4/2016-T1 no publicada (emergencia estadistica); REM ene-2005 vacio;
  UTDT e IPC Neuquen terminan ene-2026 (solo se usan hasta 2016 / 2015); primario % PIB 2018 (−2,3 vs
  −2,6 oficial) y 2023 (−2,7 vs −2,9) sin explicar (probablemente base de PIB del dato oficial); reservas
  netas sin SEDESA; rentas del FGS 2004-2014 repartidas con la proporcion 2015-16. Detalle: CONTEXTO §4b.
