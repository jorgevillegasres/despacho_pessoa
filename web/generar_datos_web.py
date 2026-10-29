#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera web/assets/datos.js — Despacho Pessoa.

La página web no puede leer los archivos del sistema desde el navegador. Este script
copia en un solo archivo JavaScript los festivos (herramientas/festivos_colombia.json)
y la ficha de cada agente (despacho/agentes/*.md + despacho/permisos.json).

Uso: python web/generar_datos_web.py [--comprobar]
  --comprobar  no escribe nada; sale con 1 si datos.js no coincide con sus fuentes.
"""
import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "web" / "assets" / "datos.js"
FESTIVOS = RAIZ / "herramientas" / "festivos_colombia.json"


sys.path.insert(0, str(RAIZ / "despacho"))
import generar_adaptadores as ga  # noqa: E402


def modo_de_fallar(cuerpo: str, id_agente: str) -> str:
    m = re.search(r"Tu modo típico de fallar es (.+?\.)(?:\s|$)", cuerpo)
    if not m:
        raise ValueError(f"{id_agente}: falta la frase «Tu modo típico de fallar es …» en Identidad y oficio")
    texto = m.group(1).replace("`", "")
    return texto[0].upper() + texto[1:]


def construir() -> str:
    festivos = json.loads(FESTIVOS.read_text(encoding="utf-8"))
    permisos = json.loads(ga.RUTA_PERMISOS.read_text(encoding="utf-8"))
    agentes = []
    for ruta in sorted(ga.DIR_AGENTES.glob("[0-9][0-9]-*.md")):
        a = ga.leer_nucleo(ruta)
        p = permisos[a["id"]]
        agentes.append({
            "id": a["id"], "nombre": a["nombre"], "heteronimo": a["heteronimo"],
            "descripcion": a["descripcion"], "cita": a["cita"], "produce": a["produce"],
            "falla": modo_de_fallar(a["cuerpo"], a["id"]),
            "lee": [r for r in p["lee"] if r not in ga.RUTAS_ANTIGUAS],
            "escribe": [r for r in p["escribe"] if r not in ga.RUTAS_ANTIGUAS],
            "ejecuta": p["ejecuta"],
        })
    datos = {"festivos": festivos, "agentes": agentes}
    return ("// ARCHIVO GENERADO por web/generar_datos_web.py desde herramientas/festivos_colombia.json,\n"
            "// despacho/agentes/*.md y despacho/permisos.json. No editar a mano.\n"
            "window.DESPACHO = " + json.dumps(datos, ensure_ascii=False, indent=2) + ";\n")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--comprobar", action="store_true", help="No escribir; avisar si datos.js está desactualizado")
    args = ap.parse_args()
    try:
        nuevo = construir()
    except (ValueError, OSError, KeyError) as e:
        print(f"No pude generar los datos de la web: {e}")
        return 1
    if args.comprobar:
        actual = DESTINO.read_text(encoding="utf-8") if DESTINO.exists() else ""
        if actual != nuevo:
            print("web/assets/datos.js está desactualizado. Corre: python web/generar_datos_web.py")
            return 1
        print("web/assets/datos.js está al día.")
        return 0
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text(nuevo, encoding="utf-8", newline="\n")
    print(f"Escrito {DESTINO.relative_to(RAIZ).as_posix()}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
