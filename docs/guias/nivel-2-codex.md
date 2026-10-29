# Modo local - El despacho en Codex

**Codex** es el asistente de OpenAI que trabaja dentro de una carpeta de tu computador. Existe como aplicación de escritorio y como programa de **terminal** (una ventana donde se escriben órdenes al computador en lugar de hacer clic). Necesitas una cuenta de ChatGPT con un plan que incluya Codex.

**Lo que hay que saber antes de empezar:** en Codex la separación de funciones queda **en la instrucción, no en un permiso**. Codex no deja fijar, agente por agente, qué archivos puede escribir cada uno; lo que hace el despacho es decírselo en el texto de cada agente y, en dos de ellos, pedirles que no escriban nada. Es la diferencia entre una regla que un programa hace cumplir (Claude Code, OpenCode) y una que el modelo promete cumplir (Codex, chat), y por eso vale la pena verla en vivo.

## 1. Instalar

- **Terminal (la ruta de esta guía):**
  1. Descomprime `despacho-pessoa.zip` en una carpeta de trabajo (Windows: clic derecho → **Extraer todo**; Mac: doble clic). El ZIP ya contiene todo el sistema; no necesitas descargar nada más.
  2. Windows: doble clic en `instalar.cmd` (si aparece «Windows protegió su PC», mira [esta sección](problemas-frecuentes.md#windows-protegio)). macOS: abre la **Terminal**, escribe `bash ` (con un espacio al final), arrastra `instalar.sh` a la ventana y pulsa Enter.
  3. A «¿Continuar? (S/n)» pulsa Enter. En el menú de cuatro opciones escribe `3` (Codex) y pulsa Enter. El instalador comprueba Python, instala Codex con **npm** (el instalador de programas que viene con Node), comprueba el corpus y la calculadora, y te dice qué escribir primero.
- **Aplicación de escritorio:** descárgala desde la página oficial de Codex e inicia sesión. Aun así, ejecuta el instalador del despacho eligiendo `4` (no instala ninguna herramienta) para que compruebe Python, el corpus y la calculadora.

## 2. Abrir el despacho

- **Terminal:** abre una terminal dentro de la carpeta del despacho (Windows: clic derecho en un espacio vacío → **Abrir en Terminal**; macOS: escribe `cd ` con un espacio, arrastra la carpeta a la ventana y pulsa Enter; `cd` es la orden para «entrar a una carpeta»). Escribe `codex.cmd` y pulsa Enter (en macOS, `codex`). La primera vez te pedirá iniciar sesión.
- **Aplicación:** abre la carpeta del despacho como proyecto.

Codex lee `AGENTS.md` al abrir la carpeta: ahí están las reglas del despacho, la tabla de los cinco agentes y las órdenes de un caso de ejemplo. Los agentes están definidos en `.codex/agents/`. Si Codex pregunta si confías en la carpeta, responde que sí.

## 3. Tu caso, paso a paso

Antes de lanzar a los agentes, crea tu caso. Esta versión no trae casos resueltos:

```text
python herramientas/nuevo_caso.py
```

Elige la materia, el nombre y los datos del Director. El script crea `casos/<tu-caso>/` y añade la fila al índice. Después completa `00-expediente.md` y escribe la entrevista y las pruebas en `01-entrada/entrevista-y-pruebas.md`.

En Codex no se usa `@`: se pide el agente por su nombre. En los ejemplos de abajo uso `mi-primer-caso`; cambia ese nombre por el que hayas elegido. Escribe una orden a la vez, espera el «Reporte de Cierre» y lee el resultado antes de seguir:

1. ```text
   Usa el agente 01-observador-caeiro para leer casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribir casos/mi-primer-caso/02-hechos/hechos.md según su contrato de salida.
   ```
2. ```text
   Usa el agente 02-investigador-search para leer casos/mi-primer-caso/02-hechos/hechos.md y el corpus que indica casos/mi-primer-caso/00-expediente.md, y escribir casos/mi-primer-caso/03-investigacion/investigacion.md.
   ```
3. ```text
   Usa el agente 03-redactor-reis para redactar casos/mi-primer-caso/04-borrador/borrador.md usando solo 02-hechos/hechos.md, 03-investigacion/investigacion.md y la plantilla que indica el expediente.
   ```
4. ```text
   Usa el agente 04-verificador-soares para auditar casos/mi-primer-caso/04-borrador/borrador.md y escribir casos/mi-primer-caso/05-auditoria/informe-verificacion.md.
   ```
   En Codex, Soares **no escribe el archivo**: tiene instrucción de entregar el informe completo como texto en su respuesta. Cópialo y guárdalo tú como `casos/mi-primer-caso/05-auditoria/informe-verificacion.md` (ábrelo con el Bloc de notas o TextEdit, pega y guarda con ese nombre exacto). Es la manera de que quien audita no toque el expediente cuando no hay un permiso que lo impida.
5. ```text
   Usa el agente 05-diablo-campos para atacar casos/mi-primer-caso/04-borrador/borrador.md y escribir casos/mi-primer-caso/05-auditoria/informe-riesgo.md.
   ```
   Igual que Soares, Campos devuelve el informe como texto: guárdalo como `casos/mi-primer-caso/05-auditoria/informe-riesgo.md`.

Para comprobar las citas con el programa, en una terminal (fuera de Codex):

```text
python herramientas/verificar_citas.py casos/mi-primer-caso/04-borrador/borrador.md
python herramientas/verificar_corpus.py --comprobar
```

Si `python` no responde, prueba `python3` o, en Windows, `py`.

## 4. Leer los informes y decidir

En `05-auditoria/informe-verificacion.md`, el dictamen de Soares cita por cita (`COINCIDE`, `NO COINCIDE` o `FUERA DEL CORPUS`); en `05-auditoria/informe-riesgo.md`, las grietas que Campos encontró. Anota tu decisión en `casos/mi-primer-caso/06-decision/decision.md` y en `registro.md` (carpeta principal del despacho) con la plantilla «Asiento de Auditoría» del final del archivo. **El que firma eres tú** (Regla 6).

<a id="si-codex-no-reconoce-los-agentes"></a>
## Si Codex no reconoce los agentes

Si Codex responde algo como `unknown agent_type`, dice que no conoce ese agente o simplemente lo ignora y hace el trabajo él mismo, usa la ruta alternativa: abre **un hilo nuevo por cada paso** (en Codex, un hilo es una conversación; una nueva por agente, como en el chat) y pide el rol por su archivo. Por ejemplo, para el paso 1:

```text
Asume el rol definido en despacho/agentes/01-observador-caeiro.md, respeta sus permisos por instrucción, lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md.
```

Cambia el número y el nombre del agente en cada paso (`02-investigador-search`, `03-redactor-reis`, `04-verificador-soares`, `05-diablo-campos`). Para Soares y Campos, añade al final: «no escribas ningún archivo; entrega el informe como texto».

## Límites conocidos en Codex

| Control | ¿Lo hace cumplir un programa? |
|---|---|
| Cada agente escribe solo su archivo | No: por instrucción. Soares y Campos devuelven texto en lugar de escribir |
| Sin internet | En parte: depende de la configuración de Codex en tu equipo; el agente tiene la prohibición por instrucción |
| Leer solo lo permitido | No: por instrucción |
| Ejecutar solo los programas permitidos | En parte: Search, Reis y Campos no tienen terminal; Caeiro y Soares sí, y la lista de programas queda en la instrucción |

Por eso en Codex tu revisión pesa más: abre cada archivo que un agente produjo y comprueba que no tocó nada más.

---

Si algo no sale como aquí, mira [Problemas frecuentes](problemas-frecuentes.md).
