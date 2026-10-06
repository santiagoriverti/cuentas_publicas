# CLAUDE.md — instrucciones para sesiones de Claude en este repo

## Al empezar

1. `git pull` antes de cualquier cambio (el usuario trabaja desde mas de una PC y a veces hace commits
   propios, p. ej. "Copia repo local").
2. Leer **`ESTADO.md`** (estado actual, proximos pasos, rutina mensual, PC nueva).
3. Si hay que tocar calculos: leer **`CONTEXTO.md`** (definiciones, fuentes, trampas conocidas; el indice
   macro esta en §4b).
4. Historial detallado y notas de sesiones: `.claude/memory/project.md`.

## Reglas del usuario

- **Commits solo con el usuario (Santiago Riverti). NUNCA agregar `Co-Authored-By: Claude`** ni
  ninguna atribucion a Claude en commits o PRs.
- Idioma: espanol (rioplatense) en respuestas, commits y documentacion.
- El usuario usa los notebooks en **Google Colab**: el **notebook 02** descarga `analisis_fiscal.zip`
  (Excel + 7 graficos), el **notebook 03** (indice macro) descarga `indice_macro.zip`. El notebook 01 es
  opcional. Cuando el usuario pasa un ZIP de Colab, compararlo hoja por hoja con la corrida local.
- El **indice macro circula**: su nota metodologica esta en el **README** (pedido del usuario: ahi, no en
  un documento aparte). Comunicar el ultimo mes con su rango de sensibilidad ("cerca de lo tipico y en
  baja" si el rango cruza el 0). Pagina interactiva/dashboard: no por ahora.
- **Metodologia del indice congelada (v9)**: no cambiarla sin un sesgo verificado en los datos y sin
  acuerdo del usuario. Si cambia: actualizar la nota del README, CONTEXTO §4b, ESTADO, correr
  `sensibilidad_indice.py` y `control_calidad.py --guardar`.
- El informe LaTeX de prensa esta **en pausa** por pedido del usuario: no reactivar exports `.tex`
  sin que lo pida.
- Graficos 05 y 06 del NB02 van **sin titulo** a proposito (pedido previo).

## Reglas tecnicas que muerden

- Windows: correr Python con `PYTHONUTF8=1` (prints con unicode rompen en cp1252).
- **No usar NotebookEdit** en los `.ipynb` (rompio el encoding de `\n` una vez). Editar via JSON con
  Python: leer celda, `str.replace` sobre el source unido, guardar con `splitlines(keepends=True)` y
  `json.dump(..., ensure_ascii=False, indent=1)` (asi queda el formato del repo).
- **No escribir scripts ni ediciones con heredocs de bash**: convierten `\\n` en saltos reales y rompen
  f-strings. Usar las herramientas de escritura/edicion de archivos, o un `.py` aparte.
- **Cifras titulares del indice = las que imprime el notebook.** La hoja Indice y Por_gobierno vienen a 3
  decimales: re-redondearlas da errores (−0,015 → el NB dice −0,01). Ya paso tres veces.
- Los notebooks leen de GitHub (`raw.githubusercontent.com/.../main`). Para probar cambios antes
  del push: `python scripts/run_notebooks_local.py [01|02|03]` (redirige las URLs a disco).
- Antes de publicar el indice: `python scripts/control_calidad.py` (0 ALERTAS o explicarlas) y
  `--guardar` para actualizar `output/indice_macro.csv`. Robustez: `python scripts/sensibilidad_indice.py`
  (reproduce el indice desde el Excel; si no reproduce, algo cambio en el NB03).
- Despues de cambiar parsers: correr `python src/consolidate.py` y comparar contra los CSV
  versionados (cambios inesperados en meses viejos = regresion). Revisar el resumen de cobertura.
- `data/raw/` esta versionado (fuentes de Hacienda). `data/raw/_duplicados/` es local e ignorado.
  Agregar meses nuevos como archivos sueltos; no hace falta tocar el ZIP.
- Al cambiar el IPC cambia la base de todos los valores reales: los numeros en B cambian, los % no.
- Verificar siempre: primario nominal 2024 = 10,41 B y 2025 = 11,77 B (ver CONTEXTO.md §5).
- PIB nominal de datos.gob.ar (`4.4_OGP_2004_T_17`, = `166.2_PPIB_0_0_3` desde 2006) viene trimestral
  **anualizado**: anual = suma / 4.
- API del BCRA (`api.bcra.gob.ar`): usar `verify=False` (el certificado no valida en algunas PCs). La de
  cotizaciones rechaza fechas futuras (400).
- `macro_mensual.csv`: si se agregan columnas sin refrescar el resto, conservar el texto original de las
  existentes (la API devuelve ruido de 1e-6) y el orden de columnas de una corrida completa de
  `actualizar_macro.py`.
- **Notebook 03**: celdas 0 md · 1 parametros · 2 carga (IPC empalmado, IMIG + AIF historica 2003-15 +
  extraordinarios, PIB mensual) · 3 variables (`VARS`: codigo, nombre, pilar, signo, unidad, origen, serie;
  helper `vs_maximo()`) · 4 z, pilares, `indice_ancla`, rango de sensibilidad (`_variante()`, 12 variantes →
  `banda_min`/`banda_max`) · 5-8 graficos 01-04 + Por_gobierno · 9 export. Para agregar una variable:
  sumar la serie en `actualizar_macro.py` y una tupla en `VARS` (y actualizar los conteos "19 variables").
  Reservas netas: pasivos sin API (swap China, REPO, swap EEUU) en
  `data/reference/reservas_pasivos_manual.csv`; si el BCRA toma/cancela uno, agregar la fila.

## Cierre de sesion

Actualizar `ESTADO.md` (fecha, cobertura, cifras del indice, proximos pasos), el historial de
`.claude/memory/project.md` y, si cambiaron la metodologia o las cifras citadas, la nota del README y
CONTEXTO §4b. Commit + push (si el push pide credenciales, el usuario lo hace: Claude no ingresa tokens).
