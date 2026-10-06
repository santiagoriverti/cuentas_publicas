# CLAUDE.md — instrucciones para sesiones de Claude en este repo

## Al empezar

1. Leer **`ESTADO.md`** (estado actual, proximos pasos, rutina mensual).
2. Si hay que tocar calculos: leer **`CONTEXTO.md`** (definiciones, fuentes, trampas conocidas).
3. Historial detallado y notas de sesiones: `.claude/memory/project.md`.
4. `git pull` antes de cualquier cambio (el usuario trabaja desde mas de una PC y a veces
   hace commits propios, p. ej. "Copia repo local").

## Reglas del usuario

- **Commits solo con el usuario (Santiago Riverti). NUNCA agregar `Co-Authored-By: Claude`** ni
  ninguna atribucion a Claude en commits o PRs.
- Idioma: espanol (rioplatense) en respuestas, commits y documentacion.
- El usuario usa los notebooks en **Google Colab**; lo que importa es que el **notebook 02** corra y
  descargue `analisis_fiscal.zip` (Excel + 7 graficos). El notebook 01 es opcional. El **notebook 03**
  (indice macro) descarga `indice_macro.zip` y lee `data/reference/macro_mensual.csv`.
- El informe LaTeX de prensa esta **en pausa** por pedido del usuario: no reactivar exports `.tex`
  sin que lo pida.
- Graficos 05 y 06 van **sin titulo** a proposito (pedido previo).

## Reglas tecnicas que muerden

- Windows: correr Python con `PYTHONUTF8=1` (prints con unicode rompen en cp1252).
- **No usar NotebookEdit** en los `.ipynb` (rompio el encoding de `\n` una vez). Editar via JSON con
  Python: leer celda, `str.replace` sobre el source unido, guardar con `splitlines(keepends=True)`.
  Cuidado con heredocs de bash: `\\n` dentro de strings puede convertirse en salto real y romper
  f-strings → escribir el script de edicion a un archivo `.py` y ejecutarlo.
- Los notebooks leen de GitHub (`raw.githubusercontent.com/.../main`). Para probar cambios antes
  del push: `python scripts/run_notebooks_local.py [01|02]` (redirige las URLs a disco).
- Despues de cambiar parsers: correr `python src/consolidate.py` y comparar contra los CSV
  versionados (cambios inesperados en meses viejos = regresion). Revisar el resumen de cobertura.
- `data/raw/` esta versionado (fuentes de Hacienda). `data/raw/_duplicados/` es local e ignorado.
  Agregar meses nuevos como archivos sueltos; no hace falta tocar el ZIP.
- Al cambiar el IPC cambia la base de todos los valores reales: los numeros en B cambian, los % no.
- Verificar siempre: primario nominal 2024 = 10,41 B y 2025 = 11,77 B (ver CONTEXTO.md §5).
- PIB nominal de datos.gob.ar (`4.4_OGP_2004_T_17`, = `166.2_PPIB_0_0_3` desde 2006) viene trimestral
  **anualizado**: anual = suma / 4.
- API del BCRA (`api.bcra.gob.ar`): usar `verify=False` (el certificado no valida en algunas PCs).
- **Notebook 03**: celdas 0 md · 1 parametros · 2 carga (IPC empalmado, IMIG + extraordinarios, PIB
  mensual) · 3 variables (lista `VARS`: codigo, nombre, pilar, signo, unidad, origen, serie) · 4 z,
  pilares, `indice_ancla` · 5-8 graficos 01-04 + Por_gobierno · 9 export. Para agregar una variable:
  sumar la serie en `actualizar_macro.py` y una tupla en `VARS`. Editar via JSON (igual que NB02).
  Reservas netas (v5): pasivos sin API (swap China, REPO, swap EEUU) en
  `data/reference/reservas_pasivos_manual.csv`; si el BCRA toma/cancela uno, agregar la fila.
  Antes de dar por buena una corrida, recalcular desde el Excel: Z = (Variables − mediana)/escala,
  pilares = promedio de Z, indice = promedio de pilares (las auditorias de oct-2026 lo hicieron asi).

## Cierre de sesion

Actualizar `ESTADO.md` (fecha, cobertura, cifras clave si cambiaron, proximos pasos) y agregar al
historial de `.claude/memory/project.md`. Commit + push (si el push pide credenciales, el usuario
lo hace: Claude no ingresa tokens).
