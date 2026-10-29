#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Decisor único de permisos — Despacho Pessoa (Regla 4 del Estatuto).

Lee despacho/permisos.json y responde si un agente puede leer una ruta,
escribir una ruta o ejecutar un comando. Los hooks de Claude Code y las
reglas de OpenCode se generan desde el mismo archivo, así que no pueden
discrepar de este script.

Uso:
  python herramientas/verificar_permisos.py <agente> <lee|escribe|ejecuta> <ruta-o-comando>
Salida: "permitido" (código 0) o "denegado: <motivo>" (código 1).
Códigos de salida: 0 permitido, 1 denegado, 2 uso incorrecto. El hook de Claude
Code (siguiente tarea) traduce "denegado" a su propio código 2.

Las rutas se resuelven contra la raíz del proyecto (se siguen ".." y enlaces
simbólicos). En los patrones, "*" y "?" actúan dentro de un solo segmento de
ruta y "**" cruza directorios.
"""
import json
import re
import shlex
import sys
from fnmatch import fnmatchcase
from pathlib import Path

RAIZ_POR_DEFECTO = Path(__file__).resolve().parents[1]
RUTA_PERMISOS = RAIZ_POR_DEFECTO / "despacho" / "permisos.json"
ACCIONES = ("lee", "escribe", "ejecuta")
INTERPRETES = ("python", "python3", "py")
METACARACTERES = re.compile(r"[;&|<>`$\n\r^%(){}!]")


def cargar_permisos(ruta: Path = RUTA_PERMISOS) -> dict:
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    if not isinstance(datos, dict):
        raise ValueError("despacho/permisos.json debe ser un objeto JSON.")
    permisos = {k: v for k, v in datos.items() if not k.startswith("_")}
    for agente, reglas in permisos.items():
        for clave in ACCIONES:
            if not isinstance(reglas, dict) or not isinstance(reglas.get(clave), list):
                raise ValueError(f"permisos.json: el agente «{agente}» necesita la lista «{clave}».")
        if not isinstance(reglas.get("internet"), bool):
            raise ValueError(f"permisos.json: el agente «{agente}» necesita «internet» como true o false.")
    return permisos


def normalizar_ruta(ruta: str, raiz: Path, base: Path | None = None) -> str | None:
    """Resuelve la ruta contra la raíz y la devuelve relativa en formato POSIX.
    Las rutas relativas parten de «base» (por defecto la raíz).
    Devuelve None si queda fuera del proyecto."""
    p = Path(ruta.strip().strip('"').strip("'"))
    p = (p if p.is_absolute() else (base or raiz) / p).resolve()
    try:
        return p.relative_to(raiz.resolve()).as_posix()
    except ValueError:
        return None


def _coincide_segmentos(patron: list[str], ruta: list[str]) -> bool:
    if not patron:
        return not ruta
    if patron[0] == "**":
        return any(_coincide_segmentos(patron[1:], ruta[i:]) for i in range(len(ruta) + 1))
    if not ruta:
        return False
    return fnmatchcase(ruta[0], patron[0]) and _coincide_segmentos(patron[1:], ruta[1:])


def _coincide(ruta: str, patrones: list[str]) -> bool:
    segmentos = ruta.split("/")
    return any(_coincide_segmentos(patron.split("/"), segmentos) for patron in patrones)


def _revisar_argumentos(agente: str, argumentos: list[str]) -> tuple[bool, str]:
    """Los scripts del despacho aceptan opciones que cambian de dónde se leen las fuentes
    (--raiz) o la investigación (--investigacion). Un agente no puede apuntarlas fuera del
    corpus real ni fuera de casos/."""
    i = 0
    while i < len(argumentos):
        arg = argumentos[i]
        if arg.lower().startswith("--raiz"):
            return False, f"{agente} no puede cambiar la raíz del corpus (Regla 1)."
        if arg.lower().startswith("--investigacion"):
            if "=" in arg:
                valor = arg.partition("=")[2]
            else:
                i += 1
                valor = argumentos[i] if i < len(argumentos) else ""
            segmentos = valor.replace("\\", "/").strip("/").split("/")
            if segmentos[0] != "casos" or len(segmentos) < 3 or ".." in segmentos or "" in segmentos:
                return False, (f"{agente} solo puede indicar --investigacion dentro de casos/ "
                               f"(Regla 1): intentó «{valor}».")
        i += 1
    return True, "permitido"


def decidir(permisos: dict, agente: str, accion: str, objetivo: str,
            raiz: Path = RAIZ_POR_DEFECTO, cwd: Path | None = None) -> tuple[bool, str]:
    if agente not in permisos:
        return False, f"El agente «{agente}» no está registrado en despacho/permisos.json."
    if accion not in ACCIONES:
        return False, f"Acción desconocida «{accion}». Acciones válidas: lee, escribe, ejecuta."
    reglas = permisos[agente]

    if accion == "ejecuta":
        permitidos = ", ".join(reglas["ejecuta"]) or "ninguno"
        if METACARACTERES.search(objetivo):
            return False, "no se permiten operadores de consola (&&, |, >, $(), …). Regla 4 del Estatuto."
        try:
            partes = shlex.split(objetivo.replace("\\", "/"), posix=True)
        except ValueError:
            return False, "No se pudo interpretar el comando. Regla 4 del Estatuto."
        if len(partes) < 2 or partes[0] not in INTERPRETES:
            return False, (f"{agente} solo puede ejecutar los scripts del despacho con Python "
                           f"({', '.join(INTERPRETES)}): {permitidos}. Regla 4 del Estatuto.")
        if partes[1].startswith("-"):
            return False, "no se permiten opciones del intérprete (-c, -m, …). Regla 4 del Estatuto."
        script = normalizar_ruta(partes[1], raiz, cwd)
        if script is None:
            return False, f"{agente} no puede ejecutar archivos fuera del proyecto. Regla 4 del Estatuto."
        if not _coincide(script, reglas["ejecuta"]):
            return False, (f"{agente} no puede ejecutar «{script}». Scripts permitidos: "
                           f"{permitidos}. Regla 4 del Estatuto.")
        return _revisar_argumentos(agente, partes[2:])

    ruta = normalizar_ruta(objetivo, raiz, cwd)
    if ruta is None:
        return False, f"{agente} no puede tocar archivos fuera del proyecto. Regla 4 del Estatuto."
    # Un agente puede leer su propio archivo de salida (para corregirlo al repetir el paso).
    permitidos_ruta = reglas["lee"] + reglas["escribe"] if accion == "lee" else reglas[accion]
    if _coincide(ruta, permitidos_ruta):
        return True, "permitido"
    verbo = "leer" if accion == "lee" else "escribir"
    motivo = (f"{agente} solo puede {verbo}: {', '.join(permitidos_ruta) or 'nada'}. "
              f"Intentó {verbo} «{ruta}». Regla 4 del Estatuto")
    return False, motivo + (": quien redacta no aprueba." if accion == "escribe" else ".")


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if len(argv) != 4:
        print(__doc__)
        return 2
    _, agente, accion, objetivo = argv
    ok, motivo = decidir(cargar_permisos(), agente, accion, objetivo)
    print("permitido" if ok else f"denegado: {motivo}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
