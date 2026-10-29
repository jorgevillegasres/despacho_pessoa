# Modo local - El despacho en OpenCode

**OpenCode** es un asistente de código abierto que trabaja dentro de una carpeta de tu computador, como Claude Code, y puede usar modelos de varios proveedores (Anthropic, OpenAI, Google y otros). Se usa desde una **terminal** (una ventana donde se escriben órdenes al computador en lugar de hacer clic). Necesitas una cuenta con alguno de esos proveedores.

En OpenCode los permisos de cada agente son **reglas por ruta**: el archivo de cada agente dice qué carpetas y archivos puede leer, cuáles puede editar y qué comandos puede ejecutar, y OpenCode las aplica. Comprueba tu versión con `opencode --version`.

## 1. Instalar

1. Descomprime `despacho-pessoa.zip` en una carpeta de trabajo (Windows: clic derecho → **Extraer todo**; Mac: doble clic). El ZIP ya contiene todo el sistema; no necesitas descargar nada más.
2. Ejecuta el instalador:
   - **Windows:** abre la carpeta descomprimida y haz doble clic en `instalar.cmd`. Si aparece «Windows protegió su PC», mira [esta sección](problemas-frecuentes.md#windows-protegio).
   - **macOS:** abre la aplicación **Terminal**, escribe `bash ` (con un espacio al final), arrastra `instalar.sh` a la ventana y pulsa Enter.
3. A «¿Continuar? (S/n)» pulsa Enter. En el menú de cuatro opciones escribe `2` (OpenCode) y pulsa Enter.
4. El instalador comprueba Python, instala OpenCode con **npm** (el instalador de programas que viene con Node), comprueba el corpus y la calculadora, y te dice qué escribir primero.

## 2. Abrir el despacho

1. Abre una terminal **dentro de la carpeta del despacho**:
   - **Windows:** en el Explorador de archivos, dentro de la carpeta, clic derecho en un espacio vacío → **Abrir en Terminal**.
   - **macOS:** en la Terminal escribe `cd ` (con un espacio; `cd` es la orden para «entrar a una carpeta»), arrastra la carpeta del despacho a la ventana y pulsa Enter.
2. Escribe `opencode.cmd` y pulsa Enter (en macOS, `opencode`). En Windows, el `.cmd` del final evita un aviso de seguridad de PowerShell ([por qué](problemas-frecuentes.md#scripts-deshabilitados)).
3. **La primera vez**, conecta un proveedor de modelos: escribe `/connect`, elige el proveedor con el que tengas cuenta y sigue las instrucciones (te pedirá iniciar sesión o pegar una clave). Solo hay que hacerlo una vez.
4. A diferencia de Claude Code, OpenCode **no pregunta si confías en la carpeta**: lee las reglas del despacho al abrirla. (El instalador menciona esa pregunta porque es común a las tres herramientas; en OpenCode simplemente no aparece.)
5. Escribe `@`: se despliega la lista de agentes y deben aparecer los cinco del despacho: `01-observador-caeiro`, `02-investigador-search`, `03-redactor-reis`, `04-verificador-soares` y `05-diablo-campos`.

## 3. Comprobar que los permisos son reales

Pídele a Caeiro algo que no le corresponde:

```text
@01-observador-caeiro Escribe el archivo casos/mi-primer-caso/04-borrador/borrador.md con el texto "prueba".
```

OpenCode lo niega: el archivo del agente (`.opencode/agents/01-observador-caeiro.md`, generado desde `despacho/permisos.json`) solo le permite editar `casos/*/02-hechos/hechos.md` (el `*` significa «cualquier carpeta de caso»). Todo lo demás está en `deny`.

Si en lugar de negar **te pregunta** si lo autorizas, responde que no y mira [OpenCode pregunta en vez de bloquear](problemas-frecuentes.md#opencode-pregunta).

## 4. Tu caso, paso a paso

Antes de lanzar a los agentes, crea tu caso. Esta versión no trae casos resueltos:

```text
python herramientas/nuevo_caso.py
```

Elige la materia, el nombre y los datos del Director. El script crea `casos/<tu-caso>/` y añade la fila al índice. Después completa `00-expediente.md` y escribe la entrevista y las pruebas en `01-entrada/entrevista-y-pruebas.md`.

En los ejemplos de abajo uso `mi-primer-caso`; cambia ese nombre por el que hayas elegido. Las cinco órdenes son las mismas que en Claude Code, una a la vez, leyendo cada resultado y su «Reporte de Cierre» antes de seguir:

1. ```text
   @01-observador-caeiro Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida.
   ```
2. ```text
   @02-investigador-search Lee casos/mi-primer-caso/02-hechos/hechos.md y el corpus que indica casos/mi-primer-caso/00-expediente.md, y escribe casos/mi-primer-caso/03-investigacion/investigacion.md.
   ```
3. ```text
   @03-redactor-reis Redacta casos/mi-primer-caso/04-borrador/borrador.md usando solo 02-hechos/hechos.md, 03-investigacion/investigacion.md y la plantilla que indica el expediente.
   ```
4. ```text
   @04-verificador-soares Audita casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-verificacion.md.
   ```
5. ```text
   @05-diablo-campos Ataca casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-riesgo.md.
   ```

Para otro caso, cambia `mi-primer-caso` por el nombre de la carpeta que creaste.

## 5. Leer los informes y decidir

Igual que en Claude Code: en `05-auditoria/informe-verificacion.md`, el dictamen de Soares y el veredicto del verificador de citas para cada cita (`COINCIDE`, `NO COINCIDE` o `FUERA DEL CORPUS`); en `05-auditoria/informe-riesgo.md`, las grietas que Campos encontró y cómo blindarlas. Anota tu decisión en `casos/mi-primer-caso/06-decision/decision.md` y en `registro.md` (carpeta principal del despacho) con la plantilla «Asiento de Auditoría» del final del archivo. **El que firma eres tú** (Regla 6).

Para comprobar las citas tú mismo, en la terminal (fuera de OpenCode):

```text
python herramientas/verificar_citas.py casos/mi-primer-caso/04-borrador/borrador.md
python herramientas/verificar_corpus.py --comprobar
```

Si `python` no responde, prueba `python3` o, en Windows, `py`.

## Límites conocidos en OpenCode

| Control | ¿Lo hace cumplir un programa? |
|---|---|
| Cada agente escribe solo su archivo | Sí: reglas por ruta en `.opencode/agents/` |
| Sin internet | Sí: los agentes no tienen herramientas de internet |
| Leer solo lo permitido | En parte: depende de que la versión instalada aplique las reglas de lectura; se confirma en el ensayo |
| Ejecutar solo los programas permitidos | Sí: reglas por comando (la calculadora y el verificador de citas) |

Lo que ningún programa controla: que el agente use bien lo que lee. Eso sigue dependiendo de la instrucción y de tu revisión.

---

Si algo no sale como aquí, mira [Problemas frecuentes](problemas-frecuentes.md).
