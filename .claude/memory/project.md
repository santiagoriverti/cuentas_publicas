# Proyecto: cuentas_publicas — memoria de proyecto

> Estado vigente y rutina: `ESTADO.md` · Metodologia: `CONTEXTO.md` · Reglas para Claude: `CLAUDE.md`.
> Este archivo guarda el HISTORIAL de sesiones y notas que no entran en esos documentos.

## Datos del repo
- GitHub: https://github.com/santiagoriverti/cuentas_publicas (rama `main`)
- Local (PC INECO): `C:\Users\sriverti\Desktop\INECO\Repositorios\cuentas_publicas`
- Colab NB02: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb
- Colab NB01: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb

## Snapshot al cierre 2026-09-22
- Datos hasta ago-2026; base deflactor ago-2026 (IPC 12.276,766).
- AIF 30.414 registros (79 meses mensuales, falta solo jun-2022); IMIG 4.931 (2019-01..2026-08 completo).
- Gasto primario 2023 296,7 B → 2024 204,6 B (−31,1%) → 2025 208,5 B (−29,7%).
- Primario 2023 −29,5 / 2024 +22,7 / 2025 +17,0 / 2026 ene-ago +13,3 B.
- Push funciona con Git Credential Manager (desde sep-2026).

## Historial de sesiones

### 2026-06-03 a 06-05 — creacion
- Parsers AIF/IMIG para 75-80 Excel 2020-2026, consolidacion tidy, NB01 (Excel) y NB02 (7 graficos).
- Validacion vs Hacienda 2024/2025 primario y financiero 0,00%.
- Rama master → main (links de Colab daban 404).

### 2026-06-18 — ciclo mayo 2026
- Incorporado may-2026. Fix `I2_APORTES_SEG_SOCIAL` (variante vieja "Contribuciones a la Seg.Social").
- consolidate.py autodetecta ZIP y reporta huecos AIF/IMIG.
- NB02: hojas Informe_tabla1, Informe_provincias, Informe_valores, Tablas_LaTeX y 5 .tex para el
  informe de prensa (regla: totales/% desde valores sin redondear).
- Push con PAT temporal por chat (luego se paso a GCM).

### 2026-09-22 — ciclo agosto 2026 + reorganizacion
- Nuevos: `Junio 26.xlsx`, `Agosto 26.xlsx`, `IMIG Junio 2026.xlsx`, `IMIG Agosto 2026.xlsx`.
  Hacienda NO publico julio 2026 (la web salta de junio a agosto).
- `consolidate._derivar_mensuales_aif`: jul-2026 = acum ago − acum jun − mens ago (validado exacto
  contra abr/may/jun-2026).
- `imig_parser.parse_mensualizacion` + `consolidate._una_fuente_por_mes_imig`: IMIG de una sola
  fuente por mes; mar-2026 y jul-2026 desde hoja Mensualizacion. IMIG bajo de 8.745 a 4.931 filas
  (se eliminaron duplicados de versiones revisadas).
- BUG IMIG corregido: mar-2023 tenia valores de may-2019 (fecha serial falsa en
  resultado_fiscal_mayo-20.xls). Rubros IMIG 2023 estaban ~5% subestimados en el informe de junio.
- IPC jun-ago 2026: nivel general por API datos.gob.ar; divisiones completadas desde el IPC.xlsx
  que bajo el usuario.
- NB02: export sin LaTeX (Excel 11 hojas: Leeme + analisis + AIF_mensual/AIF_acumulado/IMIG) + 7 PNG;
  tabla 1 con Ingresos totales (XI); torta con colores unicos y leyenda lateral; leyendas 02/05/07
  fuera de las barras (helper `leyenda_var` en celda 1); "(N meses)" de 2026 dinamico.
- Repo autocontenido: `data/raw/` versionado (sector_publico.zip + sueltos). Los 78 sueltos que
  duplicaban el ZIP, un zip viejo de 75 archivos y una copia de IPC se movieron a
  `data/raw/_duplicados/` (local, gitignored; contenido identico verificado por hash/celdas).
- Scripts nuevos: `scripts/actualizar_ipc.py`, `scripts/run_notebooks_local.py`.
- Docs nuevos: ESTADO.md, CONTEXTO.md, CLAUDE.md; README reescrito.
- Usuario ejecuto NB02 en Colab: resultados identicos a la corrida local (11 hojas, 0 diferencias).

## Notas sueltas utiles
- Mensualizacion: cada IMIG 2026+ trae ene..mes actual → si falta el IMIG de un mes, el del mes
  siguiente lo cubre automaticamente.
- 2026 en AIF: `total_general` reemplaza la suma nac+pami en `get_serie_total`.
- Meses de cupon de deuda (enero, julio) → intereses altos; junio y diciembre → aguinaldo.
- NB02 celda 9 todavia calcula `df_informe_valores` / `df_tablas_latex` / `TEX_FILES` (LaTeX en pausa).
- NB02 celdas: 0 md · 1 helpers · 2 carga · 3-8 graficos 01-07 · 9 resumen + tablas informe · 10 export.
- NB01 (7 celdas) exporta `datos_fiscales_consolidado.xlsx`: AIF_mensual, AIF_acumulado,
  Resultado_pivot, Transferencias_provincias, IMIG; imprime validacion 2024/2025 vs Hacienda.

## Pendientes (ver ESTADO.md §3)
- [ ] Proximo mes: septiembre 2026 (rutina ESTADO.md §4).
- [ ] (pausa) Informe LaTeX rebaseado.
- [ ] Datos provinciales MECON por jurisdiccion.
- [ ] Consolidacion intra-sector para % provincias.
- [ ] Revocar PAT viejo de jun-2026 si sigue activo.
