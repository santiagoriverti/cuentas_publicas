# Proyecto: cuentas_publicas — memoria de proyecto

> Estado vigente y rutina: `ESTADO.md` · Metodologia: `CONTEXTO.md` · Reglas para Claude: `CLAUDE.md`.
> Este archivo guarda el HISTORIAL de sesiones y notas que no entran en esos documentos.

## Datos del repo
- GitHub: https://github.com/santiagoriverti/cuentas_publicas (rama `main`)
- Local (PC INECO): `C:\Users\sriverti\Desktop\INECO\Repositorios\cuentas_publicas`
- Colab NB02: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/02_analisis_fiscal.ipynb
- Colab NB01: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/01_consolidar.ipynb
- Colab NB03: https://colab.research.google.com/github/santiagoriverti/cuentas_publicas/blob/main/notebooks/03_indice_macro.ipynb

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

## Sesion 2026-10-06: indice macroeconomico
- Nuevo `scripts/actualizar_macro.py` → `data/reference/macro_mensual.csv` (16 series: datos.gob.ar,
  BCRA API v4, BCRA ITCRMSerie.xlsx, argentinadatos). Nuevo `notebooks/03_indice_macro.ipynb`
  (10 celdas: 0 md · 1 params · 2 carga + IPC empalmado + PIB mensual · 3 variables · 4 z/pilares ·
  5-8 graficos 01-04 + promedio por gestion · 9 export). Agregado "03" a run_notebooks_local.
- Normalizacion IQR (no MAD: rompia con la brecha); reservas en meses de importaciones.
- BUG PIB_B NB02: valores 2020-2023/2025 erroneos; la serie INDEC es trimestral anualizada (/4).
- Resultado ago-2026: IMA −0,01, sin fiscal −0,17. Promedio por gestion (sin fiscal): NK −0,22 ·
  CFK +0,19 · CFK2 −0,06 · Macri −0,43 · AF −0,70 · Milei −0,40.
- Revision v2 (mismo dia): IPC 2007-2015 Neuquen, expectativas UTDT 2006-2016, brecha blue 2011-12,
  fiscal 2016+ (CSV infra.datos.gob.ar .../452.3/download/imig-mensual.csv, identico al repo),
  credito/PIB, hoja Arrastrados, Por_gobierno (mes por mayoria, min 12 meses). Ago-2026: IMA +0,22,
  sin fiscal +0,03. Por gestion (sin fiscal): NK +0,02 · CFK +0,07 · CFK2 −0,12 · Macri −0,20 ·
  AF −0,73 · Milei −0,32.
- OJO: en datos.gob.ar los IDs 452.2_* son TRIMESTRALES y 452.1_* anuales; la IMIG mensual solo esta
  como CSV de la distribucion 452.3.
- v2 corrida por el usuario en Colab: identica a la local (8 hojas, dif 0).
- Revision v3 (de datos, benchmarks vs cifras oficiales): primario sin extraordinarios (DEG sep-2021
  = exceso de 'Transferencias corrientes' nivel 2; rentas PFE 2022; recursos extraordinarios 2026),
  credito real en pesos (BCRA var 117), blue de Ambito (centavos), UTDT promedio con ajuste de nivel
  (−5,4 pts log vs REM), `indice_ancla` (Precios vs meta 10%). Ago-2026: IMA +0,20, sin fiscal +0,00,
  ancla −0,04. Por gestion (sin fiscal): NK +0,01 · CFK +0,06 · CFK2 −0,09 · Macri −0,23 · AF −0,72 ·
  Milei −0,35.
- Revision v4 (3ra, verificacion independiente 2026-10-06): se recalculo TODO desde el Excel sin
  usar el codigo del NB y reprodujo exacto (z, pilares, indice/sin_fiscal/ancla — formula del ancla
  confirmada: −(x − 100·ln(1,10))/escala —, Por_gobierno, arrastres ≤3m, spot-checks desde
  Datos_crudos; tcrm usa la mediana del ITCRM en ventana INICIO:FIN_IPC). Unico hallazgo: la
  mediana/IQR se calculaba sobre X DESPUES del ffill de borde → fix: `X_propio = X.where(OBS)` en
  celda 4; Metodologia (normalizado_hasta/meses/pct_meses_en_tope) ahora sobre datos propios
  (celda 9). Impacto max 0,02 z historico; ago-2026: IMA +0,20 (igual), sin fiscal −0,00 (antes
  +0,00), ancla −0,04 (igual); Empleo −0,40 (antes −0,39). PCA para pesos: evaluado y DESCARTADO
  (PC1 explica ~40%, signos mixtos: Externo −46% / Precios −10%); queda documentado en CONTEXTO §4b.
- Las auditorias usaron scripts descartables (scratchpad): recalcular Z/pilares/indice desde el
  Excel, comparar Colab vs local hoja por hoja, benchmarks (inflacion oficial, EMAE, reservas,
  desocupacion, primario % PIB), tramos congelados y saltos en crudos. Repetirlas si se cambia el NB03.
- v5 (2026-10-06, otra sesion): **reservas netas** reemplazan a las brutas en el pilar Externo
  (`reservas_netas_meses_impo`). Netas = brutas (var 1) − encajes (var 1243, M USD; = renglon
  "Current accounts in other currencies" del balance) − organismos internacionales (balance semanal
  XLS `summary-balances-assets-liabilities-bcra-annual-series-1998-to-date.xls`, una hoja por anio,
  miles de $ / "Rate of Exchange"; 2002-2006 traen el dia 7 leido como mes) − swap China − REPO BCRA −
  swap EEUU (estos tres a mano en `data/reference/reservas_pasivos_manual.csv`; el yuan se valua con
  `estadisticascambiarias/v1.0/Cotizaciones/CNY`, `tipoPase`). Descartados como fuente: dataset
  datos.gob.ar 300.1 (balance mensual, corta en oct-2025), "Other liabilities" y "Due to repo" del
  balance (mezclan pesos), FRED (corta la conexion). REPO 2017 = Tesoro (no se resta). Efecto: max
  0,15 (2004), ago-2026 IMA +0,19 (antes +0,20), Spearman −0,56 sin cambio. CSV macro: 32 columnas.
- v6 (2026-10-06): `saldo_comercial` (MM USD corrientes) → `saldo_comercial_pib` = (expo − impo) 12 m
  / suma 12 m (pib_mensual / A3500) × 100. El nominal en USD premiaba 2026 (z +1,64) aunque en % PIB
  (3,4%) es la mitad que 2004-05. PIB nominal pasa a la serie 4.4_OGP_2004_T_17 (desde 2004; = 166.2)
  → credito_pib arranca dic-2004. Ago-2026: IMA +0,19 → +0,14, sin fiscal −0,06, ancla −0,09 (−0,095),
  Externo −0,19; Spearman miseria −0,54. En el CSV solo se agregaron meses nuevos del PIB (los
  existentes se dejaron con el texto original: la API devuelve ruido de 1e-6).
  Evaluados y pendientes de decision: extender el pilar fiscal a 2004 (restando utilidades BCRA y
  rentas FGS 2007-15) y EMAE como brecha vs tendencia en vez de var. i.a. (el usuario eligio solo el saldo).
- v7 (2026-10-06): **pilar fiscal desde 2004**. `actualizar_macro.aif_historica()` → columnas
  `aif_hist_{primario,intereses,ingresos,extraordinarios}` (2003-2015) desde la AIF SPN base caja mensual
  de datos.gob.ar (379.7 1993-2006, 379.8 2007-2014, 379.9 metodologia 2017 2015+; la 379.9 = IMIG
  exacto en 2016-26). Ajustes 2003-14: utilidades BCRA = BCRA var 50 (suma mensual; = "rentas percibidas
  del BCRA" de la AIF 2015+ mes a mes); rentas sin BCRA repartidas 34% genuina / 66% intra (2015-16);
  primario = sup − util − intra, intereses = brutos − intra, ingresos = antes fig − util − intra
  (− coparticipacion + leyes especiales en 1993-2006). Extraordinarios: DEG nov-dic 2009, 4G dic-2014.
  NB03: `imig_serie(..., col_aif)`; graf. 01 y validacion con el indice completo. Ago-2026: IMA +0,00
  (antes +0,14), Fiscal +0,33 (antes +1,18), ancla −0,24; Spearman −0,56.
- v8 (2026-10-06): `emae_vs_maximo` = EMAE desest. / max(36 meses previos, min 12) − 1, en Actividad
  (nivel vs ritmo; se evaluaron incluir el mes [20% de ceros] y maximo historico; elegido 36m previo).
  Ago-2026 −4,5% (z −0,87), IMA −0,01 (−0,015), Actividad −0,66. Efecto max 0,20 (may-2021). Spearman −0,56.
- v9 (2026-10-06): `salario_real_vs_maximo` (Empleo), helper `vs_maximo()` en la celda 3 (tambien lo usa
  `emae_vs_maximo`, sin cambios). Mediana −12,4% (salario en caida desde 2017). Ago-2026 IMA −0,01 (NB),
  Empleo −0,37. **Metodologia congelada en v9** (pedido: no seguir ajustando sin sesgo verificado).
  Proximo posible: sensibilidad (pesos por variable, ventana fija, sin tope) y validacion vs recesiones.

## Notas sueltas utiles
- Cifras titulares del NB03: tomar las que IMPRIME el notebook (redondeo del valor exacto), NO
  re-redondear la hoja Indice ni Por_gobierno (vienen a 3 decimales: −0,015 → el NB dice −0,01;
  Macri sin fiscal −0,175 → −0,17). Ya paso tres veces.
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
- [x] NB03 v5 corrido en Colab (2026-10-06): identico a local en las 8 hojas.
- [x] NB03 v6 corrido en Colab (2026-10-06): identico a local en las 8 hojas.
- [x] Pilar fiscal desde 2004 (v7, 2026-10-06).
- [x] Nivel de actividad: EMAE vs maximo 36m (v8).
- [x] Nivel del salario real (v9; metodologia congelada).
- [x] NB03 v9 corrido en Colab (2026-10-06): identico a local en las 8 hojas.
- [ ] (opcional) Sensibilidad + validacion vs cronologia de recesiones; dashboard.
- [x] NB03 v8 corrido en Colab (2026-10-06): identico a local en las 8 hojas.
- [x] NB03 v7 corrido en Colab (2026-10-06): identico a local en las 8 hojas.
- [ ] Indice macro: dashboard/Artifact; SEDESA en netas si aparece serie. (PCA descartado v4; netas hechas v5.)
- [ ] Cada mes: revisar si hubo REPO/swap nuevo del BCRA → `reservas_pasivos_manual.csv`.
