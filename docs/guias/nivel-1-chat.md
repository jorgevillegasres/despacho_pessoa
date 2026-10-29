# Modo chat - El despacho sin instalar agentes

Para usar el Despacho Pessoa en este modo solo necesitas un navegador y una cuenta de **Claude** (claude.ai), **ChatGPT** (chatgpt.com) o **Gemini** (gemini.google.com). No instalas agentes. Tiempo estimado: unos 30 minutos, después de crear tu caso.

> **Nota:** esta guía usa la tutela como ejemplo. Si tu materia es otra (demanda laboral, concepto, etc.), cambia la plantilla y el corpus según `materias/<materia>/` y el campo `Corpus` de tu `00-expediente.md`; los roles y la cadena de custodia son los mismos.

> **Apertura:** antes de Caeiro, pega `prompts-chat/00-apertura-chat.md` en una conversación nueva. La mesa de recepción te preguntará cómo quieres que te llame y qué trato prefieres. Si ya conoces el despacho, escribe «Vamos al caso» y pasa directo al prompt de Caeiro.

**La regla de oro: un chat nuevo para cada agente.** Si le pides todo a una sola conversación, el que redacta termina aprobando su propio trabajo, y eso es justo lo que el despacho evita (Regla 4 del [Estatuto](../../ESTATUTO.md): «quien redacta no aprueba»).

Un **prompt** es el texto de instrucciones que le pegas al chat para que haga de un agente. Los cinco prompts del despacho están listos en la carpeta `prompts-chat/`; tú solo copias y pegas.

## Antes de empezar

1. **Descomprime el sistema.** Toma `despacho-pessoa.zip` y descomprímelo en una carpeta de trabajo (Windows: clic derecho → **Extraer todo**; Mac: doble clic). El ZIP ya contiene todo el sistema; no necesitas descargar nada más.
2. **Abre una terminal en la carpeta descomprimida.** En Windows: clic derecho en un espacio vacío → **Abrir en Terminal**. En macOS: abre Terminal, escribe `cd ` (con un espacio), arrastra la carpeta y pulsa Enter.
3. **Crea tu caso.** Esta versión no trae casos resueltos. Escribe:

   ```text
   python herramientas/nuevo_caso.py
   ```

   El script pregunta la materia (por ejemplo `tutela` o `demanda-laboral`), el nombre del caso, cómo quieres que te llame el Director y otros datos. Al terminar tendrás una carpeta `casos/<tu-caso>/` con toda la estructura. En los ejemplos de abajo uso `mi-primer-caso`; cambia ese nombre por el que hayas elegido.
4. **Escribe la entrada.** Abre `casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md` y completa la entrevista y el inventario de pruebas. Solo hechos y documentos; no conclusiones jurídicas. Lo que no conste se escribe `NO CONSTA`. Añade los documentos a `01-entrada/pruebas/`.
5. **Mira el expediente.** Abre `casos/mi-primer-caso/00-expediente.md` y localiza el campo `Corpus` (por ejemplo, `fuentes/00_transversal, fuentes/01_salud`) y el campo `Plantilla` (por ejemplo, `plantillas/modelo-tutela.md`). Los vas a necesitar en los pasos 2 y 3.
6. **Ten a mano un editor de texto simple.** Los archivos terminan en `.md` (**Markdown**: texto normal con algunos símbolos de formato, como `#` para los títulos y `**` para la negrita). Para abrir uno en Windows: clic derecho → **Abrir con** → **Bloc de notas**. En Mac: clic derecho → **Abrir con** → **TextEdit**.

Cada prompt de `prompts-chat/` dice al principio qué archivos pegarle y con qué nombre guardar la respuesta. Esta guía repite esas listas paso a paso.

## Cómo guardar una respuesta como archivo

Cuando el chat termine:

1. Copia toda la respuesta (en Claude y ChatGPT hay un botón **Copiar** debajo de cada respuesta; en Gemini está en el menú de los tres puntos).
2. Abre un Bloc de notas nuevo (o TextEdit en Mac) y pega el texto.
3. **Archivo → Guardar como**. En Windows: en **Tipo** elige **Todos los archivos**, escribe el nombre exacto (por ejemplo `hechos.md`) y en **Codificación** deja **UTF-8** (UTF-8 es la forma de guardar el texto que conserva tildes y eñes). En Mac, TextEdit pide primero **Formato → Convertir a texto sin formato**; luego guarda con el nombre exacto y, si pregunta por la extensión, conserva `.md`.
4. Guárdalo **dentro de la carpeta de tu caso**, en la subcarpeta que indica cada paso (`02-hechos/`, `03-investigacion/`, `04-borrador/` o `05-auditoria/`). Los agentes siguientes lo van a necesitar.

## Paso 1 - Caeiro, el Observador → `02-hechos/hechos.md`

1. Abre un chat nuevo. Si tu chat tiene búsqueda web, desactívala: el despacho trabaja con corpus cerrado (Regla 1) y nada de afuera debe entrar.
2. Abre `prompts-chat/01-observador-caeiro-chat.md`, copia todo lo que hay **debajo de la línea** `---` y pégalo en el chat.
3. En el mismo mensaje, pega a continuación el contenido de estos dos archivos, uno tras otro:
   - `ESTATUTO.md`
   - `casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md`

   Envía el mensaje.
4. **La calculadora.** Caeiro tiene prohibido contar días hábiles de cabeza (Regla 5) y, en el chat, no puede ejecutar la calculadora del despacho. Por eso escribirá `PLAZO PENDIENTE DE CALCULADORA` y dejará las fechas que necesita. Abre la [calculadora de plazos](../../web/calculadora.html), pon esas fechas y el tipo de plazo, pulsa **Calcular** y después **Copiar el resultado**. Vuelve al chat y pega lo copiado con esta frase delante: «Esta es la salida de la calculadora; transcríbela literal en la sección 3».
5. **Revisa como Socio Director.** ¿Tiene las cinco secciones del contrato de salida? ¿Está la tabla de afirmaciones que `NO CONSTAN`? ¿Cada hecho probado lleva su `[Soporte: Prueba P-XX]`? Si algo falla, díselo en el mismo chat y pídele que corrija. Cuando estés conforme, guarda la respuesta como `casos/mi-primer-caso/02-hechos/hechos.md`.

## Paso 2 - Search, el Investigador → `03-investigacion/investigacion.md`

1. **Chat nuevo.** Pega lo que hay debajo de la línea en `prompts-chat/02-investigador-search-chat.md`.
2. Pega después, en el mismo mensaje:
   - `ESTATUTO.md`
   - `casos/mi-primer-caso/02-hechos/hechos.md`
   - **todos** los archivos de las carpetas de `fuentes/` que indica el campo `Corpus` de tu `00-expediente.md`. Por ejemplo, para una tutela de salud: `fuentes/00_transversal/` y `fuentes/01_salud/`; para una demanda laboral: `fuentes/00_transversal/` y `fuentes/02_laboral/`.
   - `plantillas/ficha-cita.md`

   Si el chat no deja pegar tanto texto, arrastra los archivos a la ventana del chat para adjuntarlos.
3. Revisa que cada ficha de cita tenga los cuatro datos de la Regla 2: ruta del archivo en `fuentes/`, identificador oficial, ubicación dentro del documento y texto literal entre comillas. Guarda como `casos/mi-primer-caso/03-investigacion/investigacion.md`.

## Paso 3 - Reis, el Redactor → `04-borrador/borrador.md`

1. **Chat nuevo.** Pega lo que hay debajo de la línea en `prompts-chat/03-redactor-reis-chat.md`.
2. Pega después:
   - `ESTATUTO.md`
   - `casos/mi-primer-caso/02-hechos/hechos.md`
   - `casos/mi-primer-caso/03-investigacion/investigacion.md`
   - la plantilla que indica el campo `Plantilla` de tu `00-expediente.md` (por ejemplo, `plantillas/modelo-tutela.md` o `materias/demanda-laboral/plantillas/modelo-demanda-laboral.md`)

   Nada más: Reis no debe ver `fuentes/` ni la entrevista. Solo redacta con lo que Caeiro y Search le dejaron.
3. Guarda como `casos/mi-primer-caso/04-borrador/borrador.md`.

## Paso 4 - Soares, el Verificador → `05-auditoria/informe-verificacion.md`

1. **Chat nuevo.** Pega lo que hay debajo de la línea en `prompts-chat/04-verificador-soares-chat.md`.
2. Pega después:
   - `ESTATUTO.md`
   - `casos/mi-primer-caso/04-borrador/borrador.md`
   - `casos/mi-primer-caso/02-hechos/hechos.md`
   - `casos/mi-primer-caso/03-investigacion/investigacion.md`
   - `casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md`
   - los mismos archivos de `fuentes/` del paso 2
   - `plantillas/ficha-cita.md`
3. En el chat, Soares no puede correr el verificador automático de citas; lo hace a mano, cita por cita, comparando el borrador con los archivos que le pegaste. Fíjate en qué marca `COINCIDE`, `NO COINCIDE` o `FUERA DEL CORPUS` (Regla 7: lo que no está en el corpus no se declara «inexistente»). Guarda como `casos/mi-primer-caso/05-auditoria/informe-verificacion.md`.

## Paso 5 - Campos, el Abogado del Diablo → `05-auditoria/informe-riesgo.md`

1. **Chat nuevo.** Pega lo que hay debajo de la línea en `prompts-chat/05-diablo-campos-chat.md`.
2. Pega después:
   - `ESTATUTO.md`
   - `casos/mi-primer-caso/04-borrador/borrador.md`
   - `casos/mi-primer-caso/02-hechos/hechos.md`
   - `casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md`
   - `casos/mi-primer-caso/05-auditoria/informe-verificacion.md`
   - los archivos de `fuentes/` del paso 2

   Campos no recibe `investigacion.md`: ataca el borrador tal como lo leería el juez o la contraparte, sin ver las notas del investigador.
3. Guarda como `casos/mi-primer-caso/05-auditoria/informe-riesgo.md`.

## Paso 6 - Tú decides

Lee los dos informes completos. Decide si el borrador se corrige, se radica o se descarta, y anótalo en `casos/mi-primer-caso/06-decision/decision.md` y en `registro.md` (está en la carpeta principal del despacho) con la plantilla «Asiento de Auditoría» que hay al final de ese archivo. Marca las casillas que puedas comprobar y escribe tu decisión: `APROBADO`, `DEVUELTO A REDACTOR` o `DESCARTADO`. **El que firma eres tú** (Regla 6).

## Lo que el chat no puede hacer

En el chat, las siete reglas dependen de que el modelo obedezca la instrucción: nadie le impide escribir lo que no debe, leer lo que no le toca ni inventar una cita. Por eso tú haces de control en cada paso: revisas las secciones, cotejas las fichas y usas la calculadora. Si quieres que los permisos los haga cumplir un programa en vez de una promesa, pasa al modo local: [Claude Code](nivel-2-claude-code.md), [OpenCode](nivel-2-opencode.md) o [Codex](nivel-2-codex.md).

**Nunca pegues en un chat gratuito datos reales de una persona.** Los casos que construyas deben ser ficticios o estar rigurosamente anonimizados. Con un cliente de verdad, un chat gratuito no ofrece la confidencialidad que exige el secreto profesional (Regla transversal del Estatuto).

---

Si algo no sale como aquí, mira [Problemas frecuentes](problemas-frecuentes.md).
