#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hook PreToolUse para Claude Code — Despacho Pessoa.

Claude Code lo lanza con una línea de sh (ver comando_hook en despacho/generar_adaptadores.py)
que prueba python3, python y py, y ejecuta hook_claude.py <agente> con el primero que sea
Python 3.10 o posterior; si ninguno sirve, bloquea.
El JSON {"tool_name": ..., "tool_input": {...}, "cwd": ...} llega por stdin.
Código de salida 2 = bloquear la herramienta y mostrar stderr al agente.
Código 0 = dejar pasar.

Política: FALLA CERRADO y DENIEGA POR DEFECTO. Se bloquea todo lo que no se
entienda (argumentos, JSON, tipos, rutas o comandos ausentes, errores internos,
permisos.json mal formado) y toda herramienta que no esté en una lista conocida.
Para pruebas, la variable de entorno DESPACHO_PERMISOS apunta a otro permisos.json.
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verificar_permisos as vp  # noqa: E402

HERRAMIENTAS_ESCRIBEN = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
HERRAMIENTAS_LEEN = {"Read", "NotebookRead"}
HERRAMIENTAS_BUSCAN = {"Glob", "Grep"}
HERRAMIENTAS_EJECUTAN = {"Bash", "PowerShell", "Monitor"}
HERRAMIENTAS_INTERNET = {"WebFetch", "WebSearch"}
HERRAMIENTAS_DELEGAN = {"Agent", "Task"}
HERRAMIENTAS_INOCUAS = {"TodoWrite", "AskUserQuestion", "BashOutput", "KillShell",
                        "ExitPlanMode", "EnterPlanMode"}
COMODINES = re.compile(r"[*?\[{]")


def bloquear(motivo: str) -> int:
    sys.stderr.write(f"BLOQUEADO POR EL DESPACHO PESSOA: {motivo}\n")
    return 2


def _falta(campo: str) -> int:
    return bloquear(f"la herramienta no indicó {campo}; se bloquea por precaución.")


def _base_de_patron(patron: str) -> str | None:
    """Directorio fijo que precede al primer comodín. None si el patrón es
    absoluto o sube con «..». Cadena vacía si no hay directorio fijo."""
    p = patron.replace("\\", "/")
    if p.startswith("/") or re.match(r"^[A-Za-z]:", p) or ".." in p:
        return None
    m = COMODINES.search(p)
    if not m:
        return p.strip("/")
    prefijo = p[:m.start()]
    return prefijo[:prefijo.rfind("/")].strip("/") if "/" in prefijo else ""


def _main(argv: list[str]) -> int:
    if len(argv) != 2:
        return bloquear("uso incorrecto del hook: se esperaba exactamente un argumento (el agente).")
    agente = argv[1]
    try:
        datos = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError):
        datos = None
    if not isinstance(datos, dict):
        return bloquear("entrada del hook ilegible; se bloquea por precaución.")

    herramienta = datos.get("tool_name")
    if not isinstance(herramienta, str) or not herramienta:
        return bloquear("tool_name inválido; se bloquea por precaución.")
    entrada = datos.get("tool_input")
    if not isinstance(entrada, dict):
        return bloquear("tool_input inválido; se bloquea por precaución.")

    cwd = datos.get("cwd")
    cwd = Path(cwd) if isinstance(cwd, str) and cwd and Path(cwd).is_absolute() else None
    cwd_efectivo = cwd or vp.RAIZ_POR_DEFECTO

    try:
        ruta_permisos = os.environ.get("DESPACHO_PERMISOS")
        permisos = vp.cargar_permisos(Path(ruta_permisos)) if ruta_permisos else vp.cargar_permisos()
    except (ValueError, OSError) as e:
        return bloquear(f"No se pudo cargar despacho/permisos.json ({e}). Se bloquea por precaución.")
    reglas = permisos.get(agente)
    if reglas is None:
        return bloquear(f"El agente «{agente}» no está registrado en despacho/permisos.json.")

    def decidir(accion: str, objetivo: str) -> tuple[bool, str]:
        return vp.decidir(permisos, agente, accion, objetivo, cwd=cwd)

    if herramienta in HERRAMIENTAS_INTERNET or herramienta.startswith("mcp__"):
        if not reglas.get("internet", False):
            return bloquear(f"{agente} no tiene acceso a internet ni a conectores externos. "
                            f"Regla 1 del Estatuto: solo existe lo que está en fuentes/.")
        return 0

    if herramienta in HERRAMIENTAS_INOCUAS:
        return 0
    if herramienta in HERRAMIENTAS_DELEGAN:
        return bloquear(f"{agente} no puede delegar en otros agentes (Regla 4).")

    if herramienta in HERRAMIENTAS_ESCRIBEN | HERRAMIENTAS_LEEN:
        ruta = entrada.get("file_path") or entrada.get("notebook_path")
        if not isinstance(ruta, str) or not ruta:
            return _falta("la ruta")
        accion = "escribe" if herramienta in HERRAMIENTAS_ESCRIBEN else "lee"
        ok, motivo = decidir(accion, ruta)
    elif herramienta in HERRAMIENTAS_BUSCAN:
        ruta = entrada.get("path")
        if ruta is not None and (not isinstance(ruta, str) or not ruta):
            return bloquear("la ruta de búsqueda no es válida; se bloquea por precaución.")
        patron = entrada.get("pattern") if herramienta == "Glob" else entrada.get("glob")
        if patron is not None and not isinstance(patron, str):
            return bloquear("el patrón de búsqueda no es válido; se bloquea por precaución.")
        if herramienta == "Glob" and not patron:
            return _falta("el patrón")
        ok, motivo = True, "permitido"
        if ruta:
            ok, motivo = decidir("lee", ruta)
            if ok and herramienta == "Glob" and _base_de_patron(patron) is None:
                ok, motivo = False, "el patrón de búsqueda sale del directorio indicado. Regla 4 del Estatuto."
        else:
            # Sin path la búsqueda parte del directorio de trabajo.
            if herramienta == "Grep" or not patron:
                ok, motivo = decidir("lee", str(cwd_efectivo))
            if ok and patron:
                base = _base_de_patron(patron)
                if base is None:
                    ok, motivo = False, "el patrón de búsqueda es absoluto o usa «..». Regla 4 del Estatuto."
                elif base == "":
                    ok, motivo = decidir("lee", str(cwd_efectivo))
                else:
                    ok, motivo = decidir("lee", base)
    elif herramienta in HERRAMIENTAS_EJECUTAN:
        comando = entrada.get("command")
        if not isinstance(comando, str) or not comando:
            return _falta("el comando")
        ok, motivo = decidir("ejecuta", comando)
    else:
        return bloquear(f"herramienta «{herramienta}» no autorizada para {agente}.")

    return 0 if ok else bloquear(motivo)


def main(argv: list[str]) -> int:
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    try:
        return _main(argv)
    except Exception as e:  # noqa: BLE001 — falla cerrado ante cualquier error
        return bloquear(f"error interno del hook ({e!r})")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
