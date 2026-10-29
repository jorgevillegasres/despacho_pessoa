# Problemas frecuentes

Si el instalador o una herramienta te muestran un error, busca aquí la sección que te indicó.
Si tu problema no está, anótalo y consúltalo con el responsable del sistema.

Varias secciones hablan de la **terminal**: es la ventana donde se escriben órdenes al computador. En Windows se abre con clic derecho dentro de la carpeta del despacho → **Abrir en Terminal**; en Mac es la aplicación **Terminal** (búscala con la lupa de Spotlight).

<a id="python"></a>
## Python no está instalado o no responde

**Qué ves:** el instalador dice que no encontró Python 3, o al escribir `python` se abre la Microsoft Store.

**Por qué:** Windows trae un atajo llamado `python` que solo abre la tienda. No es Python.

**Qué hacer en Windows (opción A, la recomendada):**
1. Abre una terminal (clic derecho dentro de la carpeta del despacho → Abrir en Terminal).
2. Escribe esta orden y pulsa Enter: `winget install --id Python.Python.3.13 -e`
   (*winget* es el instalador de aplicaciones de Windows; ya viene en Windows 11, no hay que instalarlo).
3. Cierra la terminal y ábrela de nuevo: las ventanas abiertas no se enteran de los programas recién instalados.
4. Vuelve a hacer doble clic en `instalar.cmd`.

**Qué hacer en Windows (opción B):** entra a https://www.python.org/downloads/ y descarga Python 3 (3.10 o posterior). Según la fecha, python.org te entrega uno de dos instaladores:
- Si es el **instalador clásico** (una pantalla con casillas), **marca la casilla "Add python.exe to PATH"** antes de pulsar *Install Now*.
- Si es el nuevo **"Python install manager"** (un administrador que no tiene esa casilla), termina de instalarlo, abre una terminal nueva y escribe: `py install 3.13`.

Después, en cualquiera de las dos opciones, cierra la terminal y vuelve a abrir `instalar.cmd`.

**Si al escribir `python` sigue abriéndose la Microsoft Store:** apaga el atajo: Configuración → Aplicaciones → Configuración avanzada de aplicaciones → Alias de ejecución de aplicaciones, y apaga los dos que dicen `python.exe` y `python3.exe`.

**En macOS:** el Python que trae el sistema es la versión 3.9, demasiado vieja para el despacho. La forma más sencilla es descargar el instalador `.pkg` desde https://www.python.org/downloads/, abrirlo, seguir los pasos, cerrar la Terminal y abrirla de nuevo. Si ya usas Homebrew, también sirve `brew install python` (si no lo tienes, no hace falta: usa el `.pkg`). En Linux (Ubuntu): `sudo apt install python3`.

<a id="descomprimir"></a>
## Primero hay que descomprimir el ZIP

**Qué ves:** al hacer doble clic en `instalar.cmd`, una ventana negra dice "Primero descomprime el ZIP".

**Por qué:** abriste `instalar.cmd` dentro del ZIP sin extraerlo. Windows deja ver los archivos, pero el instalador necesita los demás archivos de la carpeta.

**Qué hacer:**
1. Clic derecho sobre el archivo ZIP > **Extraer todo** > Extraer.
2. Abre la carpeta nueva que se crea y haz doble clic en `instalar.cmd` desde ahí.

<a id="windows-protegio"></a>
## Windows dice "Windows protegió su PC"

**Qué ves:** al abrir `instalar.cmd`, aparece una ventana azul que dice "Windows protegió su PC".

**Por qué:** es normal. Windows desconfía de cualquier archivo que viene de internet y no conoce al autor. El código del despacho es público y puedes revisarlo.

**Qué hacer:** haz clic en **Más información** y luego en **Ejecutar de todas formas**.

Para que no vuelva a aparecer, antes de extraer el ZIP: clic derecho sobre el ZIP > Propiedades > marca **Desbloquear** (abajo) > Aceptar. Después extrae el ZIP otra vez.

Si la ventana azul **no** tiene el botón "Ejecutar de todas formas", o si el doble clic no hace nada, mira la sección [Smart App Control](#smart-app-control).

<a id="smart-app-control"></a>
## Windows 11 no deja ejecutar `instalar.cmd` (Smart App Control)

**Qué ves:** haces doble clic en `instalar.cmd` y no pasa nada, o aparece un aviso de que la aplicación está bloqueada **sin** el botón "Ejecutar de todas formas".

**Por qué:** algunos Windows 11 nuevos traen activado *Smart App Control*, una protección que solo deja correr programas conocidos y no ofrece la salida de la sección anterior ([Windows protegió su PC](#windows-protegio), que es el caso de *SmartScreen*). Apagarlo es permanente y no lo recomendamos.

**Qué hacer:** usa el despacho en el modo chat, sin instalar nada ([guía del modo chat](nivel-1-chat.md)), o pide ayuda a quien administra el sistema.

<a id="node"></a>
## Node no está instalado

**Qué ves:** el instalador dice que no encontró Node. Node es el programa sobre el que funcionan Claude Code, OpenCode y Codex.

**Qué hacer:** descarga la versión **LTS** desde https://nodejs.org/, instálala con las opciones por defecto, cierra el instalador del despacho y vuelve a abrirlo. En macOS: `brew install node`. En Linux (Ubuntu): `sudo apt install nodejs npm`.

<a id="git"></a>
## Git no está instalado (Claude Code en Windows)

**Qué ves:** el instalador dice que no pudo instalar Git, o Claude Code se queja de que no encuentra *Git Bash*.

**Por qué:** en Windows, Claude Code necesita Git for Windows para ejecutar comandos.

**Qué hacer:** descárgalo desde https://git-scm.com/download/win, instálalo con las opciones por defecto y vuelve a abrir el instalador.

<a id="instalar-herramienta"></a>
## No se pudo instalar la herramienta (npm)

**Qué ves:** un error de `npm install -g`. `npm` es el instalador de programas que viene con Node.

**Qué hacer:**
- Si estás en la red de la universidad y el error habla de *proxy*, *ETIMEDOUT* o *certificate*, conéctate a otra red (por ejemplo, los datos del celular) y repite.
- En macOS o Linux, si el error dice `EACCES` (permiso denegado): no uses `sudo`. Instala Node con Homebrew (`brew install node`) y repite; o ejecuta `npm config set prefix ~/.npm-global`, añade `~/.npm-global/bin` a tu PATH y repite.
- Si nada funciona, usa el despacho en el modo chat: [guía del modo chat](nivel-1-chat.md).

<a id="terminal-nueva"></a>
## Después de instalar, dice que no reconoce `claude`, `opencode` o `codex`

**Qué ves:** el instalador terminó bien, pero al escribir el nombre de la herramienta la terminal responde que no lo reconoce ("no se reconoce como nombre de un cmdlet", "command not found").

**Por qué:** una terminal abierta no se entera de los programas que se instalaron después de abrirla.

**Qué hacer:** cierra la terminal, abre una nueva en la carpeta del despacho y vuelve a escribir el nombre.

<a id="verificacion"></a>
## La comprobación final falló

**Qué ves:** "El corpus de fuentes/ no coincide con su sello" o "La calculadora de plazos no corrió".

**Qué hacer:**
- **Corpus:** alguien cambió, añadió o borró un archivo de `fuentes/`. No edites esa carpeta: es el corpus cerrado. Descarga el ZIP de nuevo en otra carpeta y vuelve a ejecutar el instalador allí.
- **Calculadora:** casi siempre es una versión vieja de Python. Escribe `python --version`; si es menor que 3.10, instala una nueva (sección [Python](#python)).

<a id="scripts-deshabilitados"></a>
## "La ejecución de scripts está deshabilitada en este sistema"

**Qué ves:** al escribir `claude`, `opencode` o `codex` en PowerShell aparece ese mensaje en rojo.

**Por qué:** Windows bloquea por defecto cierto tipo de programas en PowerShell.

**Qué hacer:** escribe el nombre con `.cmd` al final: `claude.cmd`, `opencode.cmd` o `codex.cmd`. Funciona igual y no hay que cambiar ningún ajuste de seguridad.

<a id="mac-command-line-tools"></a>
## macOS: "The python3 command requires the command line developer tools"

**Qué ves:** en Mac aparece una ventana que ofrece instalar las *command line developer tools* (herramientas para programadores de Apple, una descarga grande que no necesitas).

**Por qué:** el Mac no tiene Python y, en su lugar, ofrece ese paquete.

**Qué hacer:** pulsa **Not now** (Ahora no) e instala Python con el `.pkg` de https://www.python.org/downloads/ (sección [Python](#python)). Luego vuelve a ejecutar el instalador.

<a id="mac-permission-denied"></a>
## macOS: "zsh: permission denied" al abrir `instalar.sh`

**Qué ves:** haces doble clic en `instalar.sh`, o escribes `./instalar.sh`, y la Terminal responde "permission denied" (permiso denegado).

**Por qué:** al descomprimir el ZIP, el archivo pierde el permiso de ejecutarse solo. No es un error tuyo.

**Qué hacer:** en la Terminal escribe `bash ` (con un espacio al final), arrastra `instalar.sh` desde el Finder a la ventana de la Terminal y pulsa Enter. Así el programa `bash` lo ejecuta sin necesitar ese permiso.

<a id="confianza-carpeta"></a>
## Claude Code no bloquea a Caeiro cuando intenta escribir el borrador

**Por qué:** los controles del despacho son programas que Claude Code ejecuta solo si confías en la carpeta y solo bloquean siempre desde la versión 2.1.295.

**Qué hacer:**
1. Cierra Claude Code, ábrelo de nuevo en la carpeta del despacho y, cuando pregunte si confías en ella, responde que sí.
2. Comprueba la versión con `claude --version`: debe ser 2.1.295 o posterior. Si es menor (el instalador también te lo avisa), actualiza con: `npm install -g @anthropic-ai/claude-code@latest` y abre Claude Code de nuevo.

<a id="opencode-pregunta"></a>
## OpenCode pregunta en vez de bloquear

**Qué ves:** al pedirle a Caeiro que escriba `borrador.md`, OpenCode te pide permiso en lugar de negarse.

**Qué hacer:** responde que **no**. Anota tu versión (`opencode --version`) y consúltalo con el responsable del sistema: el despacho está probado con la versión que se indica en la [guía de OpenCode](nivel-2-opencode.md).

<a id="codex-agentes"></a>
## Codex no reconoce los agentes (`unknown agent_type`)

**Qué hacer:** usa la ruta alternativa de la [guía de Codex](nivel-2-codex.md#si-codex-no-reconoce-los-agentes): pide el rol por su nombre en un hilo nuevo. En Codex la separación de funciones queda en la instrucción, no en un permiso.
