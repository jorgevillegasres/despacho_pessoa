# Modo local - El despacho en Claude Code

**Claude Code** es un asistente de Anthropic que trabaja dentro de una carpeta de tu computador: lee y escribe archivos y ejecuta programas, con los permisos que la carpeta le fije. Se usa desde una **terminal** (una ventana donde se escriben órdenes al computador en lugar de hacer clic). Necesitas una cuenta de Claude con plan de pago (Pro o superior) o créditos de la API.

Lo que cambia frente al chat: aquí los permisos de cada agente los hace cumplir un programa, no una promesa. Caeiro no puede escribir el borrador aunque quiera.

## 1. Instalar

1. Descomprime `despacho-pessoa.zip` en una carpeta de trabajo (Windows: clic derecho → **Extraer todo**; Mac: doble clic). El ZIP ya contiene todo el sistema; no necesitas descargar nada más.
2. Ejecuta el instalador:
   - **Windows:** abre la carpeta descomprimida y haz doble clic en `instalar.cmd`. Si aparece una ventana azul que dice «Windows protegió su PC», mira [esta sección](problemas-frecuentes.md#windows-protegio).
   - **macOS:** abre la aplicación **Terminal** (búscala con la lupa de Spotlight), escribe `bash ` (con un espacio al final), arrastra el archivo `instalar.sh` desde el Finder a la ventana de la Terminal y pulsa Enter.
3. El instalador pregunta «¿Continuar? (S/n)»: pulsa Enter. Luego muestra un menú con cuatro opciones; escribe `1` (Claude Code) y pulsa Enter.
4. El instalador hace cuatro pasos y marca cada uno: comprueba Python (lo usan la calculadora y los validadores), instala Claude Code con **npm** (el instalador de programas que viene con Node, el programa sobre el que funciona Claude Code), comprueba que el corpus está intacto y que la calculadora corre, y termina diciéndote qué escribir primero.

**Versión mínima.** El despacho necesita Claude Code **2.1.295 o posterior**: desde esa versión los controles bloquean siempre. Si ya tenías Claude Code instalado y es más viejo, el instalador te lo avisa en amarillo. Para comprobarlo tú mismo, en la terminal escribe `claude --version`. Para actualizar:

```text
npm install -g @anthropic-ai/claude-code@latest
```

## 2. Abrir el despacho

1. Abre una terminal **dentro de la carpeta del despacho**:
   - **Windows:** en el Explorador de archivos, dentro de la carpeta, clic derecho en un espacio vacío → **Abrir en Terminal**.
   - **macOS:** en la Terminal escribe `cd ` (con un espacio; `cd` es la orden para «entrar a una carpeta»), arrastra la carpeta del despacho a la ventana y pulsa Enter. El instalador te dejó esa orden escrita al final.
2. Escribe `claude.cmd` y pulsa Enter (en macOS, `claude`). En Windows, el `.cmd` del final evita un aviso de seguridad de PowerShell ([por qué](problemas-frecuentes.md#scripts-deshabilitados)). La primera vez te pedirá iniciar sesión en el navegador.
3. Claude Code pregunta si **confías en la carpeta**. Responde que sí. Los controles del despacho son programas que Claude Code solo ejecuta en carpetas de confianza; sin eso, nada bloquea a los agentes.
4. Escribe `/agents` y pulsa Enter. Deben aparecer los cinco agentes del despacho: `01-observador-caeiro`, `02-investigador-search`, `03-redactor-reis`, `04-verificador-soares` y `05-diablo-campos`. Sal del menú con Esc.

## 3. Comprobar que los permisos son reales

Antes de trabajar, pídele a Caeiro algo que no le corresponde. Escribe esto y pulsa Enter:

```text
@01-observador-caeiro Escribe el archivo casos/mi-primer-caso/04-borrador/borrador.md con el texto "prueba".
```

Caeiro solo puede escribir `02-hechos/hechos.md`, así que el sistema lo detiene con un mensaje que empieza por `BLOQUEADO POR EL DESPACHO PESSOA`. No es el modelo portándose bien: es un **hook** (un programa que Claude Code ejecuta antes de cada acción del agente, aquí `herramientas/hook_claude.py`) que compara lo que el agente intenta hacer con `despacho/permisos.json` y, si no coincide, lo bloquea. El hook necesita Python 3.10 o posterior; el instalador ya lo comprobó.

Si Caeiro escribe el archivo sin que nadie lo detenga, algo falta: mira [Claude Code no bloquea a Caeiro](problemas-frecuentes.md#confianza-carpeta).

## 4. Tu caso, paso a paso

Antes de lanzar a los agentes, crea tu caso. Esta versión no trae casos resueltos:

```text
python herramientas/nuevo_caso.py
```

Elige la materia, el nombre y los datos del Director. El script crea `casos/<tu-caso>/` y añade la fila al índice. Después completa `00-expediente.md` y escribe la entrevista y las pruebas en `01-entrada/entrevista-y-pruebas.md`.

En los ejemplos de abajo uso `mi-primer-caso`; cambia ese nombre por el que hayas elegido. Escribe cada orden, espera a que el agente termine con su «Reporte de Cierre» y **lee lo que hizo antes de seguir**: eres el Socio Director y entre paso y paso apruebas.

1. ```text
   @01-observador-caeiro Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida.
   ```
   Caeiro ejecuta la calculadora de plazos y copia su salida literal en la sección 3 de `hechos.md`. Abre el archivo: la tabla de la sección 4 debe recoger lo que el cliente dice y no prueba.

2. ```text
   @02-investigador-search Lee casos/mi-primer-caso/02-hechos/hechos.md y el corpus que indica casos/mi-primer-caso/00-expediente.md, y escribe casos/mi-primer-caso/03-investigacion/investigacion.md.
   ```
3. ```text
   @03-redactor-reis Redacta casos/mi-primer-caso/04-borrador/borrador.md usando solo 02-hechos/hechos.md, 03-investigacion/investigacion.md y la plantilla que indica el expediente.
   ```
4. ```text
   @04-verificador-soares Audita casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-verificacion.md.
   ```
   Soares ejecuta `herramientas/verificar_citas.py`, que busca cada cita del borrador, palabra por palabra, en el archivo de `fuentes/` que la ficha señala.
5. ```text
   @05-diablo-campos Ataca casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-riesgo.md.
   ```

Para otro caso, cambia `mi-primer-caso` por el nombre de la carpeta que creaste.

## 5. Leer los informes y decidir

- `05-auditoria/informe-verificacion.md`: el dictamen de Soares y, cita por cita, el veredicto del verificador automático: `COINCIDE`, `NO COINCIDE` o `FUERA DEL CORPUS`. Lo que está `FUERA DEL CORPUS` no es «inexistente» (Regla 7): te toca a ti decidir si lo verificas en la fuente oficial y lo incorporas, o lo descartas.
- `05-auditoria/informe-riesgo.md`: las grietas que Campos encontró y cómo blindarlas antes de radicar.

Anota tu decisión en `casos/mi-primer-caso/06-decision/decision.md` y en `registro.md` (en la carpeta principal del despacho) con la plantilla «Asiento de Auditoría» del final del archivo: `APROBADO`, `DEVUELTO A REDACTOR` o `DESCARTADO`. **El que firma eres tú** (Regla 6).

Para hacer tú mismo las comprobaciones, en la terminal (fuera de Claude Code; sal con `/exit`):

```text
python herramientas/verificar_citas.py casos/mi-primer-caso/04-borrador/borrador.md
python herramientas/verificar_corpus.py --comprobar
```

Si `python` no responde en tu equipo, prueba `python3` o, en Windows, `py`.

## Límites conocidos en Claude Code

| Control | ¿Lo hace cumplir un programa? |
|---|---|
| Cada agente escribe solo su archivo | Sí: el hook revisa cada escritura contra `despacho/permisos.json` |
| Sin internet | Sí: los agentes no tienen herramientas de internet |
| Leer solo lo permitido | En parte: se revisan las lecturas y búsquedas de archivos, no todo lo que un comando permitido podría leer |
| Ejecutar solo los programas permitidos | Sí: solo los de `permisos.json` (la calculadora y el verificador de citas) |

Lo que ningún programa controla: que el agente use bien lo que lee. Que Caeiro marque `NO CONSTA` o que Reis no adorne depende de la instrucción y de tu revisión.

---

Si algo no sale como aquí, mira [Problemas frecuentes](problemas-frecuentes.md).
