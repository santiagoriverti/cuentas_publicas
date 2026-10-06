# ESTADO DEL PROYECTO — cuentas_publicas

> Punto de entrada para retomar el trabajo en otra sesion o en otra PC.
> Ultima actualizacion: **2026-10-06**.

## 1. Donde estamos

| Item | Estado |
|---|---|
| Datos AIF + IMIG | **hasta agosto 2026** (79 meses AIF mensuales; IMIG completo 2019-01 a 2026-08) |
| IPC (deflactor) | hasta agosto 2026 → base de todos los valores reales: **ago-2026** (IPC 12.276,766) |
| Notebook 02 | Verificado en Colab (2026-09-22): 0 errores, ZIP = Excel 11 hojas + 7 PNG |
| Notebook 03 (indice macro) | v3 (2026-10-06), dos revisiones exhaustivas aplicadas; verificado local: ZIP = Excel 8 hojas + 4 PNG. v2 verificada en Colab (identica a local) |
| Series macro externas | `data/reference/macro_mensual.csv` (25 series, 2003 a oct-2026) |
| Validacion vs Hacienda | Primario 2024 = 10,41 B y 2025 = 11,77 B nominales (0% dif.); financiero 1,76 / 1,45 B |
| Repo | Autocontenido: fuentes crudas en `data/raw/`, `consolidate.py` reproduce los CSV byte a byte |
| Ultimo mes publicado por Hacienda revisado | agosto 2026 (julio 2026 NO publicado → derivado) |

### Cifras clave (pesos constantes de ago-2026, Sector Publico Total)

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

## 2. Que se hizo en el ultimo ciclo (oct-2026)

- **Indice Macroeconomico (IMA)**: notebook 03 + `scripts/actualizar_macro.py`. 17 variables en 6
  pilares (actividad, empleo e ingresos, precios, fiscal, externo, financiero), z robusto, mensual
  desde 2004. Metodologia completa en CONTEXTO.md §4b.

  | Ago-2026 | Valor | Hace 12 meses |
  |---|---|---|
  | Indice | **+0,20** | +0,37 |
  | Indice sin fiscal (comparable 2004-hoy) | +0,00 | +0,18 |
  | Indice con Precios vs meta 10% (`indice_ancla`) | −0,04 | +0,13 |

  Pilares ago-2026: Actividad −0,55 · Empleo −0,39 · Precios +0,33 (vs meta: −1,11) · Fiscal +1,18 ·
  Externo +0,11 · Financiero +0,51. Promedio por gestion (indice sin fiscal): N. Kirchner +0,01 ·
  C. Fernandez +0,06 · C. Fernandez II −0,09 · Macri −0,23 · A. Fernandez −0,72 · Milei −0,35.
  Correlacion con el indice de miseria: −0,56.
- **v3 (2da revision, de datos)**: fiscal sin ingresos extraordinarios (DEG sep-2021 428 mil M$,
  rentas por emision 2022 295 mil M$, recursos extraordinarios ene-2026 1,04 billones) → primario %
  PIB ahora coincide con el oficial (2021 −3,05 vs −3,0; 2022 −2,36 vs −2,4); credito real solo en
  pesos (BCRA var 117; la var 26 suma dolares y las devaluaciones inflaban el crecimiento); blue
  2011-12 de Ambito con centavos (argentinadatos/bluelytics redondean a $1); expectativas UTDT con
  el promedio ajustado al nivel del REM (la mediana venia redondeada a 5 pp); `indice_ancla`.
- **v2 (1ra revision, de estructura)**: inflacion 2007-2015 con IPC Neuquen (la
  serie del BCRA repetia el IPC intervenido), expectativas 2006-2016 UTDT, brecha 2011-12 con blue,
  fiscal extendido a 2016 (IMIG datos.gob.ar, identica a la del repo), credito/PIB, hoja
  Arrastrados, Por_gobierno con asignacion por mayoria del mes y minimo 12 meses por pilar.
- **Bug corregido: PIB del NB02** (`PIB_B`, celda 9). Los valores 2020-2023 y 2025 estaban mal
  (ej. 2023 = 143,2 B en vez de 193,9 B). Ahora salen de la serie INDEC (trimestral anualizada /4).
  Cambian los % PIB: primario 2023 −3,6% → −2,7%; 2025 +1,6% → +1,4%; 2020 −3,9% → −6,4%.
  Los valores en B no cambian.

## 2b. Ciclo anterior (sep-2026)

- Incorporados junio y agosto 2026. **Julio 2026 no fue publicado por Hacienda** → AIF derivado de
  acumulados (validado exacto) e IMIG desde la hoja `Mensualizacion`. Marzo 2026 IMIG tambien
  recuperado por esa via (antes figuraba como gap permanente).
- IMIG: ahora **una sola fuente por mes** (publicacion original > Mensualizacion > comparativa revisada).
- **Bug corregido** en `imig_parser.detect_value_columns`: marzo 2023 tenia valores de mayo 2019
  (un dato ~45.000 se leia como fecha serial Excel). Subestimaba ~5% los rubros IMIG 2023. Las
  cifras AIF nunca estuvieron afectadas.
- NB02: tabla 1 usa **Ingresos totales (XI)** para que Ingresos − Gasto primario = Resultado primario;
  graficos 02/05/06/07 con leyendas y colores corregidos; descarga sin archivos LaTeX y con los datos
  consolidados completos en el Excel.
- IPC completo (nivel general + divisiones) a ago-2026.
- Fuentes crudas versionadas; scripts nuevos `scripts/actualizar_ipc.py` y `scripts/run_notebooks_local.py`.
- Documentacion reorganizada: README, ESTADO (este), CONTEXTO, CLAUDE, `.claude/memory/project.md`.

## 3. Proximos pasos

1. **Cuando Hacienda publique septiembre 2026** → rutina mensual (seccion 4).
   Correr el notebook 03 v3 en Colab y comparar con la corrida local (deberia dar identico).
   Cuando INDEC publique el PIB de 2026, agregarlo a `PIB_B` del NB02 (el NB03 lo toma solo).
2. *(En pausa por pedido del usuario)* Informe LaTeX de prensa: rebasear a la base vigente. El `.tex`
   NO esta en el repo (lo tiene el usuario). La celda 9 del NB02 sigue calculando `Informe_valores` y
   `Tablas_LaTeX` (no se exportan); para reactivarlo, volver a agregarlas al export de la celda 10.
   Decision pendiente en ese informe: ajuste gasto primario con regla "sin redondear" vs resta de
   valores redondeados (difieren en 0,1 B).
3. Ideas no iniciadas: datos provinciales MECON por jurisdiccion; consolidacion intra-sector para
   medir mejor el peso de las provincias en el ajuste.
   Indice macro: reservas netas (requiere armarlas a mano: brutas − swap China − encajes − otros
   pasivos de corto plazo; el BCRA no las publica por API); pesos por PCA como sensibilidad;
   publicar el indice como Artifact/dashboard.
4. Seguridad: el remote usa Git Credential Manager (push funciona). Si quedo algun PAT viejo en
   GitHub (usado en jun-2026), revocarlo en Settings → Developer settings → Tokens.

## 4. Rutina mensual (checklist)

```bash
# 0. en PC nueva:  git clone ... && pip install -r requirements.txt   (Windows: set PYTHONUTF8=1)
# 1. copiar los Excel nuevos de Hacienda a data/raw/ (sin renombrar)
python scripts/actualizar_ipc.py          # 2. IPC nuevo (API datos.gob.ar)
python scripts/actualizar_macro.py        # 2b. series del indice macro (BCRA, INDEC, argentinadatos, Ambito)
                                          #     revisar que no diga "FALLO" (si falla conserva la version anterior)
python src/consolidate.py                 # 3. revisar "RESUMEN DE COBERTURA" al final
python scripts/run_notebooks_local.py 02 03  # 4. verificar (salidas en _local_run/)
git add data/raw data/reference output && git commit -m "datos: YYYY-MM" && git push
# 5. Colab: abrir notebook 02 -> Ejecutar todas -> descarga analisis_fiscal.zip (idem 03 -> indice_macro.zip)
```

Que revisar en el paso 3:
- `Meses SIN datos` debe listar solo `2022-06`. Si aparece un mes nuevo, ver si Hacienda lo salteo
  (la derivacion automatica necesita el acumulado del mes siguiente) o si falta copiar un archivo.
- `Cobertura mensual IMIG: completa`. Si falta un mes, buscar el Excel IMIG del mes (a veces viene
  aparte: "IMIG <Mes> <Año>.xlsx") o esperar al siguiente, cuya hoja `Mensualizacion` lo trae.
- Si Hacienda cambia el formato de un Excel (conceptos nuevos sin normalizar, huecos en un concepto),
  revisar `CONCEPTO_NORMALIZE` en `src/aif_parser.py` / `CONCEPTO_IMIG_NORMALIZE` en `src/imig_parser.py`.

## 5. Gaps conocidos (no son bugs)

- **AIF mensual jun-2022**: Hacienda solo publico el acumulado del I semestre y no hay acumulado de
  mayo 2022 → no se puede derivar. Los graficos lo saltean (`GAP_DATE` en celda 1 del NB02).
- IMIG antes de 2019: no disponible.
- Divisiones del IPC: solo informativas (los notebooks usan solo "Nivel general").
- Indice macro: desocupacion 2015-T4/2016-T1 no publicada (emergencia estadistica); REM ene-2005
  vacio; UTDT termina ene-2026 (solo se usa hasta may-2016); IPC Neuquen termina ene-2026 (solo se
  usa 2007-2015). Primario % PIB 2018 (−2,3 vs −2,6 oficial) y 2023 (−2,7 vs −2,9): diferencia
  no atribuida a ninguna partida de la IMIG (probablemente base de PIB del dato oficial).
