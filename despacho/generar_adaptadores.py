#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de adaptadores — Despacho Pessoa.

Lee despacho/agentes/*.md y despacho/permisos.json y escribe:
  .claude/agents/<id>.md + .claude/settings.json + CLAUDE.md   (Claude Code)
  .opencode/agents/<id>.md                                     (OpenCode)
  .codex/agents/<id>.toml + AGENTS.md                          (Codex)
  prompts-chat/<id>-chat.md                                    (chat: Claude, ChatGPT, Gemini)

Uso: python despacho/generar_adaptadores.py [--agentes DIR] [--salida DIR] [--solo-validar]
Los archivos generados no se editan a mano: se edita el núcleo y se vuelve a correr.
Nota: el hook de Claude Code lee la variable opcional DESPACHO_PERMISOS; nunca
debe fijarse en settings.json ni en los adaptadores.
"""
import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIR_AGENTES = RAIZ / "despacho" / "agentes"
RUTA_PERMISOS = RAIZ / "despacho" / "permisos.json"
RUTA_APERTURA = RAIZ / "despacho" / "apertura.md"

sys.path.insert(0, str(RAIZ / "herramientas"))
import verificar_permisos as vp  # noqa: E402

ADVERTENCIA = ("ARCHIVO GENERADO por despacho/generar_adaptadores.py a partir de "
               "despacho/agentes/{id}.md y despacho/permisos.json. No editar a mano.")
ADVERTENCIA_APERTURA = ("ARCHIVO GENERADO por despacho/generar_adaptadores.py a partir de "
                        "despacho/apertura.md. No editar a mano.")

CIERRE = """
## Reporte de cierre (obligatorio)

Termina siempre tu intervención con este bloque:

### Reporte de Cierre — {nombre} ({heteronimo})
- **Qué hice:** archivo generado o auditado, en una línea.
- **Qué falta:** vacíos, pruebas ausentes o pasos siguientes.
- **Qué decisión necesito del Socio Director:** una pregunta concreta.
"""

SECCIONES = ("## Identidad y oficio", "## Procedimiento", "## Contrato de salida")
CLAVES = ("id", "nombre", "heteronimo", "descripcion", "temperatura", "produce", "cita")
SOLO_LECTURA_CODEX = ("04-verificador-soares", "05-diablo-campos")
DENEGAR_CLAUDE = ["Read(./casos/**/privado/**)", "Edit(./fuentes/**)"]


def q(valor) -> str:
    """Cadena JSON: válida como escalar entre comillas en YAML y como cadena básica en TOML."""
    return json.dumps(valor, ensure_ascii=False)


def literal_toml(texto: str) -> str:
    """Cadena multilínea literal de TOML ('''…'''); si el texto lo impide, cadena JSON."""
    if "'''" in texto or "\r" in texto or texto.endswith("'"):
        return q(texto)
    return "'''\n" + texto + "'''"


def _encabezado(cuerpo: str, titulo: str):
    return re.search(rf"^{re.escape(titulo)}[ \t]*$", cuerpo, re.M)


def leer_nucleo(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8-sig")
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n(.*)", texto, re.S)
    if not m:
        raise ValueError(f"{ruta.name}: falta la cabecera entre --- ---")
    meta = {}
    for linea in m.group(1).splitlines():
        if not linea.strip():
            continue
        clave, _, valor = linea.partition(":")
        clave = clave.strip()
        if clave in meta:
            raise ValueError(f"{ruta.name}: clave repetida en la cabecera: {clave}")
        meta[clave] = valor.strip()
    faltan = [c for c in CLAVES if c not in meta]
    if faltan:
        raise ValueError(f"{ruta.name}: faltan en la cabecera: {', '.join(faltan)}")
    vacias = [c for c in CLAVES if not meta[c]]
    if vacias:
        raise ValueError(f"{ruta.name}: valores vacíos en la cabecera: {', '.join(vacias)}")
    if not re.fullmatch(r"\d{2}-[a-z0-9-]+", meta["id"]):
        raise ValueError(f"{ruta.name}: id inválido «{meta['id']}» (formato NN-nombre)")
    if meta["id"] != ruta.stem:
        raise ValueError(f"{ruta.name}: el id «{meta['id']}» no coincide con el nombre del archivo")
    try:
        float(meta["temperatura"])
    except ValueError:
        raise ValueError(f"{ruta.name}: temperatura no numérica «{meta['temperatura']}»") from None
    cuerpo = m.group(2).strip()
    posiciones = []
    for s in SECCIONES:
        h = _encabezado(cuerpo, s)
        posiciones.append(h.start() if h else -1)
    if any(p < 0 for p in posiciones) or posiciones != sorted(posiciones):
        raise ValueError(f"{ruta.name}: deben existir, en orden, las secciones {', '.join(SECCIONES)}")
    meta["cuerpo"] = cuerpo
    return meta


def seccion_permisos(agente_id: str, permisos: dict) -> str:
    p = permisos[agente_id]
    lee = "\n".join(f"  - `{r}`" for r in p["lee"])
    escribe = "\n".join(f"  - `{r}`" for r in p["escribe"])
    ejecuta = "\n".join(f"  - `python {s}`" for s in p["ejecuta"]) or "  - (ninguno)"
    internet = "permitidos" if p["internet"] else "prohibidos (Regla 1: solo existe lo que está en fuentes/)"
    nota_python = ("  Si el comando `python` no funciona en tu equipo, usa `python3` (o `py` en Windows) con los mismos argumentos.\n"
                   if p["ejecuta"] else "")
    return (f"## Permisos y límites (Regla 4 del Estatuto)\n\n"
            f"Estos límites se hacen cumplir por el sistema en Claude Code (hooks) y OpenCode (permisos por ruta); "
            f"en Codex y en chat dependen de ti.\n\n"
            f"- **Solo puedes leer:**\n{lee}\n"
            f"- **Solo puedes escribir:**\n{escribe}\n"
            f"  Puedes leer tu propio archivo de salida para corregirlo.\n"
            f"- **Solo puedes ejecutar:**\n{ejecuta}\n{nota_python}"
            f"- **Internet y conectores externos:** {internet}.\n"
            f"- La carpeta `casos/*/privado/` está fuera de tu alcance: no la leas ni la menciones.\n\n"
            f"(El `*` en una ruta significa «cualquier carpeta de caso».)\n")


def prompt_completo(a: dict, permisos: dict) -> str:
    bloque = seccion_permisos(a["id"], permisos)
    cuerpo = re.sub(r"^## Procedimiento[ \t]*$", lambda m: bloque + "\n## Procedimiento",
                    a["cuerpo"], count=1, flags=re.M)
    titulo = f"# Agente {a['id'][:2]} — {a['nombre']} ({a['heteronimo']})\n\n> *{a['cita']}*\n\n"
    return titulo + cuerpo + "\n" + CIERRE.format(nombre=a["nombre"], heteronimo=a["heteronimo"])


def escribir(destino: Path, texto: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8", newline="\n")


def leer_apertura() -> str:
    try:
        texto = RUTA_APERTURA.read_text(encoding="utf-8").strip()
    except OSError:
        return ""
    # El título del archivo se conserva en apertura.md, pero no se repite
    # cuando el texto se inyecta en AGENTS.md, CLAUDE.md o el prompt de chat.
    return re.sub(r"^# .*\n+", "", texto, count=1).strip()


# ---------- Claude Code ----------
def comando_hook(agente_id: str) -> str:
    """Una línea de sh (Claude Code usa sh en macOS/Linux y Git Bash en Windows) que busca un
    Python >= 3.10 entre python3, python y py. La sonda lee stdin de /dev/null para no consumir
    el JSON del hook. Si ninguno sirve, bloquea (exit 2) con un mensaje claro."""
    return ('for p in python3 python py; do '
            "\"$p\" -c 'import sys; sys.exit(sys.version_info < (3, 10))' </dev/null >/dev/null 2>&1 "
            f'&& exec "$p" "${{CLAUDE_PROJECT_DIR:-.}}/herramientas/hook_claude.py" {agente_id}; done; '
            "echo 'BLOQUEADO POR EL DESPACHO PESSOA: no encontré Python 3.10 o posterior "
            "(ver docs/guias/problemas-frecuentes.md#python).' >&2; exit 2")


def escribir_claude(a, permisos, raiz):
    p = permisos[a["id"]]
    tools = ["Read", "Glob", "Grep", "Write", "Edit"] + (["Bash"] if p["ejecuta"] else [])
    fm = f"""---
name: {a['id']}
description: {q(a['descripcion'])}
tools: {', '.join(tools)}
disallowedTools: WebFetch, WebSearch, Agent, Task
hooks:
  PreToolUse:
    - matcher: "*"
      hooks:
        - type: command
          command: {q(comando_hook(a['id']))}
          onFailure: "block"
---
<!-- {ADVERTENCIA.format(id=a['id'])} -->

"""
    escribir(raiz / ".claude" / "agents" / f"{a['id']}.md", fm + prompt_completo(a, permisos))


def escribir_settings_claude(raiz):
    datos = {"permissions": {"deny": DENEGAR_CLAUDE}}
    escribir(raiz / ".claude" / "settings.json", json.dumps(datos, indent=2, ensure_ascii=False) + "\n")


# ---------- OpenCode ----------
def _lineas(patrones_permitidos, final_denegado=()):
    s = '    "*": deny\n'
    for r in patrones_permitidos:
        s += f"    {q(r)}: allow\n"
    for r in final_denegado:
        s += f"    {q(r)}: deny\n"
    return s


def escribir_opencode(a, permisos, raiz):
    p = permisos[a["id"]]
    lectura = []
    for r in p["lee"] + p["escribe"]:   # puede leer su propio archivo de salida
        for x in ([r, r[:-3] + "/*"] if r.endswith("/**") else [r]):
            if x not in lectura:
                lectura.append(x)
    read = _lineas(lectura, ["casos/*/privado/**"])
    # Claves por verificar en la versión instalada de OpenCode (2.0.28); si no existen, se ignoran.
    busqueda = "".join(f"  {k}:" + chr(10) + read for k in ("grep", "glob", "list"))
    edit = _lineas(p["escribe"])
    if p["ejecuta"]:
        cmds = []
        for s in p["ejecuta"]:
            for i in vp.INTERPRETES:
                cmds += [f"{i} {s}", f"{i} {s} *"]
        bash_bloque = "  bash:\n" + _lineas(cmds)
    else:
        bash_bloque = "  bash: deny\n"
    fm = f"""---
description: {q(a['descripcion'])}
mode: subagent
temperature: {float(a['temperatura'])}
permission:
  read:
{read}{busqueda}  edit:
{edit}{bash_bloque}  webfetch: deny
  websearch: deny
  task: deny
  external_directory: deny
---
<!-- {ADVERTENCIA.format(id=a['id'])} -->

"""
    escribir(raiz / ".opencode" / "agents" / f"{a['id']}.md", fm + prompt_completo(a, permisos))


# ---------- Codex ----------
def escribir_codex(a, permisos, raiz):
    p = permisos[a["id"]]
    instrucciones = prompt_completo(a, permisos)
    if a["id"] in SOLO_LECTURA_CODEX:
        instrucciones += ("\n## Nota para Codex\nNo escribas ningún archivo. Entrega el contenido completo de "
                          f"`{a['produce']}` en tu respuesta; el Socio Director lo guardará en la carpeta del caso.\n")
    toml = (f"# {ADVERTENCIA.format(id=a['id'])}\n"
            f"name = {q(a['id'])}\n"
            f"description = {q(a['descripcion'])}\n"
            f"developer_instructions = {literal_toml(instrucciones)}\n")
    if not p["ejecuta"]:
        toml += "\n[features]\nshell_tool = false\n"
    escribir(raiz / ".codex" / "agents" / f"{a['id']}.toml", toml)


# ---------- Chat ----------
RUTAS_ANTIGUAS = {
    "casos/*/hechos.md",
    "casos/*/investigacion.md",
    "casos/*/borrador.md",
    "casos/*/informe-verificacion.md",
    "casos/*/informe-riesgo.md",
    "casos/*/entrevista-y-pruebas.md",
}


def para_alumno(ruta: str) -> str:
    if ruta == "casos/*/01-entrada/**":
        return "la carpeta `01-entrada/` de tu caso (entrevista y pruebas)"
    m = re.fullmatch(r"casos/\*/(?:(0\d-[^/]+)/)?([^/*]+)", ruta)
    if m:
        subcarpeta = f"{m.group(1)}/" if m.group(1) else ""
        return f"`{subcarpeta}{m.group(2)}` de la carpeta de tu caso"
    if ruta == "fuentes/**":
        return "todos los archivos de `fuentes/00_transversal/` y de la carpeta de tu materia"
    if ruta == "materias/**":
        return "la carpeta `materias/<materia>/` de tu materia (plantilla, checklist y plazos)"
    if ruta == "plantillas/**":
        return "la carpeta `plantillas/` (plantillas compartidas)"
    return f"`{ruta}`"


def escribir_chat(a, permisos, raiz):
    p = permisos[a["id"]]
    lee = ["ESTATUTO.md"] + [
        r for r in p["lee"]
        if r != "ESTATUTO.md" and r not in RUTAS_ANTIGUAS
    ]
    lineas = []
    for r in lee:
        texto = para_alumno(r)
        if texto not in lineas:
            lineas.append(texto)
    pegar = "\n".join(f"- {x}" for x in lineas)
    cabecera = (f"<!-- {ADVERTENCIA.format(id=a['id'])} -->\n"
                f"# Prompt para chat — {a['nombre']} ({a['heteronimo']})\n\n"
                f"**Cómo usarlo:** abre una conversación nueva (un chat = un agente), desactiva la búsqueda web "
                f"si tu chat la tiene, copia todo lo que hay debajo de la línea y pégalo. Después pega el contenido "
                f"de estos archivos (ábrelos con el Bloc de notas (Windows) o TextEdit (Mac) y copia todo):\n\n{pegar}\n\n"
                f"Guarda la respuesta como `{a['produce']}` en la subcarpeta que indica tu `00-expediente.md` "
                f"(por ejemplo, `02-hechos/`, `03-investigacion/`, `04-borrador/` o `05-auditoria/`).\n\n---\n\n")
    escribir(raiz / "prompts-chat" / f"{a['id']}-chat.md", cabecera + prompt_completo(a, permisos))


def escribir_apertura_chat(raiz):
    apertura = leer_apertura()
    cabecera = (f"<!-- {ADVERTENCIA_APERTURA} -->\n"
                f"# Apertura del Despacho Pessoa — para chat\n\n"
                f"**Cómo usarlo:** pégalo al inicio de una conversación nueva, antes del prompt de Caeiro. "
                f"Si ya conoces el despacho, responde «Vamos al caso» y pasa al prompt de Caeiro. "
                f"En el chat no hay escritura automática: copia el nombre y el trato a la sección "
                f"`Director` de tu `00-expediente.md`.\n\n"
                f"---\n\n")
    escribir(raiz / "prompts-chat" / "00-apertura-chat.md", cabecera + apertura + "\n")


# ---------- CLAUDE.md / AGENTS.md ----------
COMANDOS = [
    ("01-observador-caeiro",
     "Lee casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribe casos/mi-primer-caso/02-hechos/hechos.md según tu contrato de salida.",
     "leer casos/mi-primer-caso/01-entrada/entrevista-y-pruebas.md y escribir casos/mi-primer-caso/02-hechos/hechos.md según su contrato de salida."),
    ("02-investigador-search",
     "Lee casos/mi-primer-caso/02-hechos/hechos.md y el corpus que indica casos/mi-primer-caso/00-expediente.md, y escribe casos/mi-primer-caso/03-investigacion/investigacion.md.",
     "leer casos/mi-primer-caso/02-hechos/hechos.md y el corpus que indica casos/mi-primer-caso/00-expediente.md, y escribir casos/mi-primer-caso/03-investigacion/investigacion.md."),
    ("03-redactor-reis",
     "Redacta casos/mi-primer-caso/04-borrador/borrador.md usando solo 02-hechos/hechos.md, 03-investigacion/investigacion.md y la plantilla que indica el expediente.",
     "redactar casos/mi-primer-caso/04-borrador/borrador.md usando solo 02-hechos/hechos.md, 03-investigacion/investigacion.md y la plantilla que indica el expediente."),
    ("04-verificador-soares",
     "Audita casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-verificacion.md.",
     "auditar casos/mi-primer-caso/04-borrador/borrador.md y escribir casos/mi-primer-caso/05-auditoria/informe-verificacion.md."),
    ("05-diablo-campos",
     "Ataca casos/mi-primer-caso/04-borrador/borrador.md y escribe casos/mi-primer-caso/05-auditoria/informe-riesgo.md.",
     "atacar casos/mi-primer-caso/04-borrador/borrador.md y escribir casos/mi-primer-caso/05-auditoria/informe-riesgo.md."),
]


def instrucciones_proyecto(agentes, para_codex: bool) -> str:
    filas = "\n".join(f"| `{a['id']}` | {a['nombre']} ({a['heteronimo']}) | `{a['produce']}` |" for a in agentes)
    apertura = leer_apertura()
    if para_codex:
        cmds = "\n".join(f"{n}. Usa el agente `{i}` para {inf}" for n, (i, _, inf) in enumerate(COMANDOS, 1))
        extra = ("\n## Si los agentes personalizados no están disponibles\n"
                 "Si Codex responde `unknown agent_type` o ignora los archivos de `.codex/agents/`, asume tú el rol "
                 "pedido en un hilo nuevo por cada paso: lee `despacho/agentes/<id>.md`, respeta sus permisos por "
                 "instrucción (lee solo lo que su sección «Permisos y límites» permite y escribe solo su archivo) y "
                 "termina con su Reporte de Cierre. Los agentes 04 y 05 devuelven su informe como texto para que el "
                 "Socio Director lo copie al archivo correspondiente.\n")
    else:
        cmds = "\n".join(f"{n}. `@{i} {imp}`" for n, (i, imp, _) in enumerate(COMANDOS, 1))
        extra = ("\n## Nota para quien instala (humano)\n"
                 "- Al abrir el proyecto, acepta el diálogo de confianza de la carpeta: sin eso Claude Code "
                 "no ejecuta los hooks de los agentes.\n"
                 "- Requiere Claude Code v2.1.295 o posterior (campo `onFailure` de los hooks).\n"
                 "- `.claude/settings.json` es generado por el generador; tus ajustes personales van en "
                 "`.claude/settings.local.json`.\n")
    return f"""<!-- ARCHIVO GENERADO por despacho/generar_adaptadores.py. No editar a mano. -->
# Despacho Pessoa — Instrucciones del proyecto

Este proyecto es un despacho jurídico multiagente para redactar y auditar documentos jurídicos con controles contra la alucinación. La tutela es la materia de ejemplo; las materias (tutela, demanda laboral, ...) están en `materias/`. La norma suprema es `ESTATUTO.md`: léelo antes de cualquier tarea.

## Reglas para el agente principal (tú, al abrir este proyecto)
- No redactes, investigues ni audites tú mismo. Delega en el agente que corresponda, en orden, y espera la aprobación del Socio Director entre pasos.
- Antes de cada caso, lee `casos/<caso>/00-expediente.md`: de allí salen la materia, la plantilla, el corpus y las rutas. No asumas que el caso es una tutela.
- Nunca cites normas ni sentencias de memoria. Solo existe lo que está en el corpus del expediente (Regla 1).
- Nunca cuentes días hábiles: `python herramientas/calcular_plazos.py` (Regla 5).
- No leas ni menciones nada de `casos/*/privado/`: son notas internas del despacho.
- Lo que no está en el corpus se declara `FUERA DEL CORPUS`, nunca "inexistente" (Regla 7).

## Apertura del despacho
{apertura}

## Los agentes y el orden del flujo
| Agente | Rol | Produce |
|---|---|---|
{filas}

Flujo: entrevista → 01 → (humano aprueba hechos) → 02 → 03 → 04 y 05 sobre el mismo borrador → (humano decide y asienta en `registro.md`).

## Comandos de un caso (ejemplo)
Crea tu caso con `python herramientas/nuevo_caso.py` y reemplaza `mi-primer-caso` por el nombre que elegiste. Estas son las cinco órdenes, una por agente y en orden:
{cmds}

## Casos
- `casos/00-indice.md`: tablero de casos.
- `casos/_PLANTILLA-CASO/`: plantilla para crear un caso nuevo.
- `python herramientas/nuevo_caso.py`: crea la carpeta y la carátula del caso.
- `python herramientas/nuevo_caso.py --materia tutela --nombre "Caso de prueba"`: ejemplo no interactivo.

## Validadores
- `python herramientas/verificar_citas.py casos/<caso>/borrador.md`
- `python herramientas/verificar_corpus.py --comprobar`
- `python herramientas/calcular_plazos.py --demo-casos`
{extra}"""


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agentes", default=str(DIR_AGENTES), help="Carpeta con los archivos del núcleo")
    ap.add_argument("--salida", default=None, help="Carpeta raíz de salida (por defecto, la raíz del repositorio)")
    ap.add_argument("--solo-validar", action="store_true", help="Solo comprobar el núcleo, sin escribir nada")
    args = ap.parse_args()

    agentes_por_defecto = Path(args.agentes).resolve() == DIR_AGENTES.resolve()
    if not args.solo_validar and not agentes_por_defecto and args.salida is None:
        print("Error: con --agentes distinto del núcleo del repositorio hay que indicar --salida "
              "(o usar --solo-validar); no se sobrescribe el repositorio.", file=sys.stderr)
        return 1
    raiz = Path(args.salida) if args.salida else RAIZ

    try:
        agentes = [leer_nucleo(p) for p in sorted(Path(args.agentes).glob("[0-9][0-9]-*.md"))]
        if not agentes:
            raise ValueError(f"No hay archivos de agente en {args.agentes}")
    except (ValueError, OSError) as e:
        print(f"Núcleo inválido: {e}", file=sys.stderr)
        return 1
    try:
        permisos = vp.cargar_permisos(RUTA_PERMISOS)
    except (ValueError, OSError) as e:
        print(f"Permisos inválidos: {e}", file=sys.stderr)
        return 1
    ids = [a["id"] for a in agentes]
    for a in agentes:
        if a["id"] not in permisos:
            print(f"Núcleo inválido: {a['id']} no está en despacho/permisos.json", file=sys.stderr)
            return 1
    for sobrante in sorted(set(permisos) - set(ids)):
        print(f"Aviso: permisos.json tiene «{sobrante}» pero no hay archivo de núcleo para él.")

    if args.solo_validar:
        print(f"Núcleo válido: {len(agentes)} agentes.")
        return 0
    try:
        for a in agentes:
            escribir_claude(a, permisos, raiz)
            escribir_opencode(a, permisos, raiz)
            escribir_codex(a, permisos, raiz)
            escribir_chat(a, permisos, raiz)
        escribir_apertura_chat(raiz)
        escribir_settings_claude(raiz)
        escribir(raiz / "CLAUDE.md", instrucciones_proyecto(agentes, False))
        escribir(raiz / "AGENTS.md", instrucciones_proyecto(agentes, True))
    except OSError as e:
        print(f"No se pudo escribir: {e}", file=sys.stderr)
        return 1
    print(f"Generados {len(agentes)} agentes × 4 adaptadores + settings.json + CLAUDE.md + AGENTS.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
