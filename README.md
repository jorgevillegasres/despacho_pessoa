# Despacho Pessoa

> **Sistema de trabajo jurídico** con cinco agentes de inteligencia artificial, corpus cerrado y trazabilidad.
> **Paquete:** `despacho-pessoa.zip` · **Licencia:** MIT

Despacho Pessoa es un sistema para despachos jurídicos, abogados independientes y equipos legales que quieren usar IA sin renunciar al control del expediente. La tutela es la materia de ejemplo; el sistema se adapta a otras materias —demanda laboral, concepto, recurso, contrato— cambiando la plantilla, la checklist y el corpus.

Cada agente tiene un oficio, unos límites y una forma conocida de equivocarse. Tú diriges el despacho y firmas.

**El sistema no incluye casos precargados.** La carpeta `casos/` solo contiene la plantilla `_PLANTILLA-CASO` y un índice vacío. El primer paso es crear el expediente de tu caso con `nuevo_caso.py`.

## Lo que incluye

- Cinco agentes con permisos separados: Observador, Investigador, Redactor, Verificador y Abogado del Diablo.
- Siete reglas de trabajo y un Estatuto que cada agente lee antes de actuar.
- Una biblioteca jurídica cerrada, catalogada y sellada con SHA-256.
- Plantillas de tutela y demanda laboral, con checklist y plazos.
- Herramientas determinísticas: calculadora de plazos, verificador de citas y sello del corpus.
- Una plantilla de caso y un creador de expedientes.
- Una página web local con la explicación del sistema y la calculadora.
- La presentación de la conferencia como página web (`web/presentacion.html`), con las ilustraciones de los cinco agentes y del flujo del despacho.
- Prompts listos para usar el sistema en Claude, ChatGPT o Gemini.
- Adaptadores para Claude Code, OpenCode y Codex.
- Instaladores para Windows, macOS y Linux.

## Requisitos

- **Python 3.10 o posterior** para crear casos, calcular plazos y verificar citas. En Windows, si `python` no responde, prueba `py`.
- Un **editor de texto** para abrir y guardar archivos `.md` (Bloc de notas, TextEdit, VS Code o el editor de tu preferencia).
- Para el **modo chat**: un navegador y una cuenta de Claude, ChatGPT o Gemini.
- Para el **modo local**: Claude Code, OpenCode o Codex, según la guía que elijas.

## Empieza en cinco minutos

1. **Descomprime** `despacho-pessoa.zip` en una carpeta de trabajo.
2. **Abre una terminal** en la carpeta del sistema. En Windows: clic derecho en un espacio vacío de la carpeta → **Abrir en Terminal**. En macOS: abre Terminal, escribe `cd ` (con un espacio), arrastra la carpeta y pulsa Enter.
3. **Crea tu caso:**

   ```text
   python herramientas/nuevo_caso.py
   ```

   El script pregunta la materia, el nombre del caso y cómo quieres que te llame el despacho. Copia `casos/_PLANTILLA-CASO/` en `casos/<tu-caso>/`, reemplaza los marcadores y añade una fila a `casos/00-indice.md`.
4. **Completa la entrada.** Abre `casos/<tu-caso>/00-expediente.md` y revisa la materia, el corpus y las rutas. Después escribe la entrevista y el inventario de pruebas en `casos/<tu-caso>/01-entrada/entrevista-y-pruebas.md`. Solo hechos y documentos: nada de conclusiones jurídicas. Lo que no conste se escribe `NO CONSTA`.
5. **Elige el modo de trabajo.** En el chat no instalas agentes; en el modo local los permisos de cada agente los hace cumplir un programa. Las guías están en `docs/guias/`.

## Dos modos de trabajo

| Modo | Qué necesita | Guía |
|---|---|---|
| **Modo chat** (sin instalar agentes) | Un navegador y Python para crear el caso | [Modo chat](docs/guias/nivel-1-chat.md) |
| **Modo local** con Claude Code | Windows, macOS o Linux | [Claude Code](docs/guias/nivel-2-claude-code.md) |
| **Modo local** con OpenCode | Windows, macOS o Linux | [OpenCode](docs/guias/nivel-2-opencode.md) |
| **Modo local** con Codex | Windows, macOS o Linux | [Codex](docs/guias/nivel-2-codex.md) |
| **Calcular un plazo** | Nada; funciona en el navegador | [Calculadora](web/calculadora.html) |
| **Ver la conferencia** | Nada; funciona en el navegador | [Presentación](web/presentacion.html) · [en línea](https://jorgevillegasres.github.io/despacho_pessoa/presentacion.html) |
| **Resolver un error** | — | [Problemas frecuentes](docs/guias/problemas-frecuentes.md) |

## El flujo del despacho

| | Agente | Heterónimo | Oficio | Escribe |
|---|---|---|---|---|
| 01 | El Observador | Alberto Caeiro | Separa lo probado de lo que solo se dice; marca `NO CONSTA` | `02-hechos/hechos.md` |
| 02 | El Investigador | Alexander Search | Busca en el corpus cerrado y arma fichas de cita literales | `03-investigacion/investigacion.md` |
| 03 | El Redactor | Ricardo Reis | Redacta el documento solo con los hechos y las fichas | `04-borrador/borrador.md` |
| 04 | El Verificador | Bernardo Soares | Coteja cada cita y cada fecha; nunca reescribe | `05-auditoria/informe-verificacion.md` |
| 05 | El Abogado del Diablo | Álvaro de Campos | Ataca el borrador como el juez o la contraparte | `05-auditoria/informe-riesgo.md` |
| — | El Socio Director | Tú | Decides, corriges y firmas | `06-decision/decision.md` y `registro.md` |

El flujo es secuencial: entrevista → 01 → (tú apruebas los hechos) → 02 → 03 → 04 y 05 sobre el mismo borrador → (tú decides y asientas en `registro.md`). Un chat nuevo para cada agente en el modo chat; un agente a la vez en el modo local.

## Las siete reglas y cómo se hacen cumplir

| Regla | Cómo se hace cumplir |
|---|---|
| 1. Corpus cerrado: solo existe lo que está en `fuentes/` | Sin herramientas de internet en Claude Code y OpenCode; por instrucción en Codex y en el chat |
| 2. Ninguna cita sin ficha | `herramientas/verificar_citas.py` coteja cada cita palabra por palabra (ignora comillas y formato) |
| 3. «No consta» ante la duda | Por instrucción al agente y por tu revisión; Soares coteja cada hecho |
| 4. Quien redacta no aprueba | `despacho/permisos.json`, aplicado por código en Claude Code y OpenCode |
| 5. Plazos con herramienta, nunca con el modelo | `herramientas/calcular_plazos.py` y la calculadora web; que el agente la use depende de la instrucción y de tu revisión |
| 6. El humano firma | Por ti: nada sale sin tu firma en `registro.md` |
| 7. Fuera del corpus no es inexistente | El verificador de citas emite tres veredictos: `COINCIDE`, `NO COINCIDE` o `FUERA DEL CORPUS` |

El texto completo está en [ESTATUTO.md](ESTATUTO.md).

## La biblioteca

La biblioteca jurídica está en `fuentes/`. Es un **corpus cerrado**: los agentes solo pueden citar lo que está allí. El catálogo está en [`fuentes/00-indice.md`](fuentes/00-indice.md), con una fila por fuente, su tipo, la materia, el problema jurídico, el estado de cotejo y si es citable.

- `fuentes/00_transversal/`: Constitución, tutela, derecho de petición.
- `fuentes/01_salud/`: salud.
- `fuentes/02_laboral/`: trabajo y estabilidad ocupacional.
- `fuentes/03_habeas_data/`: habeas data y reportes negativos.

Parte de la biblioteca se trajo de una base indexada de jurisprudencia y normas colombianas: esos archivos conservan el enlace al PDF de cada providencia o a la norma indexada, declaran la fecha de consulta y quedan en estado `Consulta registrada` hasta que alguien los coteje contra el sitio oficial. El catálogo dice cuáles son.

`fuentes/SELLO.json` guarda la huella SHA-256 de cada archivo. Antes y después de trabajar:

```text
python herramientas/verificar_corpus.py --comprobar
```

Si añades una fuente, escribe su cabecera, actualiza `fuentes/00-indice.md` y vuelve a sellar con `python herramientas/verificar_corpus.py --sellar`.

## Crear un caso nuevo

`nuevo_caso.py` es la puerta de entrada del sistema. Crea la carpeta del caso, reemplaza los marcadores de la plantilla y deja el expediente listo para que lo llenes.

```text
python herramientas/nuevo_caso.py
```

También puedes hacerlo sin preguntas:

```text
python herramientas/nuevo_caso.py --materia tutela --nombre "Mi primer caso" --director "Ana" --trato usted
```

La estructura que crea es esta:

```text
casos/mi-primer-caso/
├── 00-expediente.md              # carátula: materia, corpus, rutas, Director
├── 01-entrada/
│   ├── entrevista-y-pruebas.md   # lo que ves y lo que tienes
│   └── pruebas/                  # documentos del expediente
├── 02-hechos/hechos.md           # salida de Caeiro
├── 03-investigacion/             # salida de Search
├── 04-borrador/                  # salida de Reis
├── 05-auditoria/                 # informes de Soares y Campos
├── 06-decision/                  # tu decisión y el registro del caso
└── 07-archivo/
```

Para una demanda laboral, usa `--materia demanda-laboral`. Las materias están en `materias/`; cada una trae su plantilla, checklist, plazos y corpus por defecto. Para añadir una materia, copia una carpeta de `materias/` y edita `materia.json`, la plantilla, la checklist y los plazos.

## Cómo hablarle a los agentes

En Claude Code y OpenCode se usa `@`; en Codex se pide el agente por su nombre. Estas son las cinco órdenes de un caso llamado `mi-primer-caso`; cambia ese nombre por el tuyo:

```text
@01-observador-caeiro Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida.

@02-investigador-search Lee casos/mi-primer-caso/02-hechos/hechos.md y el corpus que indica casos/mi-primer-caso/00-expediente.md, y escribe casos/mi-primer-caso/03-investigacion/investigacion.md.

@03-redactor-reis Redacta casos/mi-primer-caso/04-borrador/borrador.md usando solo 02-hechos/hechos.md, 03-investigacion/investigacion.md y la plantilla que indica el expediente.

@04-verificador-soares Audita casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-verificacion.md.

@05-diablo-campos Ataca casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-riesgo.md.
```

En Codex, la primera orden se escribe así:

```text
Usa el agente 01-observador-caeiro para leer casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribir casos/mi-primer-caso/02-hechos/hechos.md según su contrato de salida.
```

Lee el **Reporte de Cierre** de cada agente antes de pasar al siguiente. Tú eres el Socio Director: apruebas los hechos, revisas las citas y decides.

## Verificar antes de firmar

```text
python herramientas/verificar_corpus.py --comprobar
python herramientas/verificar_citas.py casos/mi-primer-caso/04-borrador/borrador.md
python -m unittest discover -s herramientas/tests
node --test web/tests/plazos.test.js
```

La calculadora y los validadores también se pueden usar sin abrir un agente. Si `python` no responde en tu equipo, prueba `python3` o, en Windows, `py`.

## Para quien quiera mirar por dentro

```text
despacho/agentes/        Los cinco agentes (se editan aquí, una sola vez)
despacho/permisos.json   Qué lee, escribe y ejecuta cada agente
despacho/apertura.md     La mesa de recepción del despacho
materias/                Plantillas, checklists y plazos por tipo de documento
casos/_PLANTILLA-CASO/   Plantilla para crear un caso
casos/00-indice.md       Tablero de casos (empieza vacío)
fuentes/                 La biblioteca jurídica, sellada con fuentes/SELLO.json
herramientas/            Calculadora, verificador de citas, verificador del corpus y creador de casos
docs/guias/              Guías de uso
web/                     Página de inicio y calculadora
prompts-chat/            Prompts listos para el modo chat
.claude/ .opencode/ .codex/   Versiones generadas para cada herramienta (no se editan a mano)
```

- Crear un caso: `python herramientas/nuevo_caso.py`
- Regenerar los agentes: `python despacho/generar_adaptadores.py`
- Regenerar los datos de la web: `python web/generar_datos_web.py`
- Pruebas: `python -m unittest discover -s herramientas/tests` y `node --test web/tests/plazos.test.js`

## Privacidad

Los casos que construyas deben ser **ficticios o estar rigurosamente anonimizados**. Nunca pegues en un chat gratuito datos reales de una persona: nombres, cédulas, historias clínicas, radicados o secretos profesionales. El Estatuto lo prohíbe y el secreto profesional no se negocia por comodidad.

## Licencia

MIT. Puedes usar, copiar, modificar y distribuir el despacho, conservando el aviso de licencia.
