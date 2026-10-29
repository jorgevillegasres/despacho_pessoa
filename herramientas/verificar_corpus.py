#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sello de integridad del corpus — Despacho Pessoa (Regla 1 del Estatuto).

  python herramientas/verificar_corpus.py --sellar      # escribe fuentes/SELLO.json
  python herramientas/verificar_corpus.py --comprobar   # compara y lista cambios
Códigos: 0 sin cambios · 1 hay cambios o no hay sello · 2 error de uso o sello corrupto.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTES_POR_DEFECTO = RAIZ / "fuentes"
NOMBRE_SELLO = "SELLO.json"


def huellas(fuentes: Path) -> dict[str, str]:
    salida = {}
    for p in sorted(fuentes.rglob("*")):
        if p.is_symlink():
            raise ValueError(f"el corpus no debe contener enlaces simbólicos: {p.relative_to(fuentes).as_posix()}")
        if p.is_file() and p.name != NOMBRE_SELLO:
            rel = p.relative_to(fuentes).as_posix()
            salida[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return salida


def sellar(fuentes: Path = FUENTES_POR_DEFECTO) -> dict:
    datos = {"sellado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "algoritmo": "sha256", "archivos": huellas(fuentes)}
    with open(fuentes / NOMBRE_SELLO, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(datos, indent=2, ensure_ascii=False) + "\n")
    return datos


def comprobar(fuentes: Path = FUENTES_POR_DEFECTO) -> dict[str, list[str]]:
    ruta_sello = fuentes / NOMBRE_SELLO
    if not ruta_sello.is_file():
        raise FileNotFoundError(f"No hay sello en {ruta_sello}. Corre primero --sellar.")
    try:
        previo = json.loads(ruta_sello.read_text(encoding="utf-8"))["archivos"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise ValueError(f"El sello {ruta_sello} está corrupto: {e}") from e
    if not isinstance(previo, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in previo.items()):
        raise ValueError(f"El sello {ruta_sello} está corrupto: 'archivos' debe ser un objeto de ruta→hash")
    actual = huellas(fuentes)
    return {
        "añadidos": sorted(set(actual) - set(previo)),
        "borrados": sorted(set(previo) - set(actual)),
        "modificados": sorted(k for k in set(actual) & set(previo) if actual[k] != previo[k]),
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--sellar", action="store_true")
    g.add_argument("--comprobar", action="store_true")
    ap.add_argument("--fuentes", default=str(FUENTES_POR_DEFECTO))
    args = ap.parse_args()
    fuentes = Path(args.fuentes)
    if not fuentes.is_dir():
        print(f"No existe la carpeta {fuentes}.")
        return 2

    if args.sellar:
        try:
            d = sellar(fuentes)
        except ValueError as e:
            print(f"No se pudo sellar: {e}.")
            return 2
        print(f"Sello escrito: {len(d['archivos'])} archivos de {fuentes} registrados el {d['sellado']}.")
        return 0

    try:
        c = comprobar(fuentes)
    except FileNotFoundError as e:
        print(e)
        return 1
    except ValueError as e:
        print(e)
        return 2
    if not any(c.values()):
        print(f"El corpus está intacto: coincide con el sello ({len(huellas(fuentes))} archivos).")
        return 0
    print("El corpus CAMBIÓ respecto al sello:")
    for clave, etiqueta in (("añadidos", "Añadidos"), ("borrados", "Borrados"), ("modificados", "Modificados")):
        for rel in c[clave]:
            print(f"  {etiqueta:<11} {rel}")
    print("Si el cambio fue intencional, vuelve a correr --sellar y anótalo en registro.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
