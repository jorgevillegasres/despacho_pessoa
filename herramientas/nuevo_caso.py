#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crea un caso nuevo a partir de casos/_PLANTILLA-CASO y de una materia.

Uso interactivo:
  python herramientas/nuevo_caso.py

Uso con argumentos:
  python herramientas/nuevo_caso.py --nombre "Caso de prueba" --materia tutela --director "Jorge" --trato usted

Qué hace:
  1. Lee materias/<materia>/materia.json.
  2. Copia casos/_PLANTILLA-CASO a casos/<slug>/.
  3. Reemplaza los marcadores {{...}} en los archivos .md del caso.
  4. Escribe la sección Director (nombre, trato, título, estilo, presentación).
  5. Agrega una fila a casos/00-indice.md.
  6. Deja el registro inicial en 06-decision/registro-ejecucion.md.

No sobrescribe un caso existente. Si el nombre ya existe, falla con un mensaje claro.
"""
import argparse
import json
import re
import shutil
import sys
import unicodedata
from datetime import date
from pathlib import Path

RAIZ_POR_DEFECTO = Path(__file__).resolve().parents[1]
PLANTILLA = Path("casos") / "_PLANTILLA-CASO"
INDICE = Path("casos") / "00-indice.md"
MARCADOR_INDICE = "<!-- CASOS-NUEVOS -->"


class ErrorDeCaso(ValueError):
    """Error controlado al crear un caso."""


def slugify(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto or "caso"


def cargar_materia(raiz: Path, materia: str) -> dict:
    ruta = raiz / "materias" / materia / "materia.json"
    if not ruta.is_file():
        disponibles = sorted(p.parent.name for p in (raiz / "materias").glob("*/materia.json"))
        raise ErrorDeCaso(
            f"No existe la materia «{materia}» en {ruta}. "
            f"Materias disponibles: {', '.join(disponibles) or 'ninguna'}."
        )
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ErrorDeCaso(f"No pude leer {ruta}: {exc}") from exc
    for clave in ("id", "nombre", "tipo_documento", "plantilla", "checklist", "plazos", "corpus_por_defecto"):
        if clave not in datos:
            raise ErrorDeCaso(f"{ruta}: falta la clave «{clave}».")
    return datos


def siguiente_id(raiz: Path, año: int) -> str:
    patron = re.compile(rf"CASO-{año}-(\d{{3}})")
    maximo = 0
    for ruta in (raiz / "casos").glob("*/00-expediente.md"):
        try:
            texto = ruta.read_text(encoding="utf-8")
        except OSError:
            continue
        for numero in patron.findall(texto):
            maximo = max(maximo, int(numero))
    return f"CASO-{año}-{maximo + 1:03d}"


def _celda(valor: str) -> str:
    return str(valor).replace("|", "\\|").replace("\n", " ").strip()


def agregar_al_indice(raiz: Path, fila: str) -> None:
    ruta = raiz / INDICE
    if not ruta.is_file():
        print(f"Aviso: no existe {ruta}; el caso se creó sin fila en el índice.", file=sys.stderr)
        return
    texto = ruta.read_text(encoding="utf-8")
    if MARCADOR_INDICE not in texto:
        raise ErrorDeCaso(
            f"{ruta} no tiene el marcador {MARCADOR_INDICE}. "
            "Agrégalo debajo de la tabla para que el script sepa dónde insertar."
        )
    texto = texto.replace(MARCADOR_INDICE, f"{fila}\n{MARCADOR_INDICE}", 1)
    ruta.write_text(texto, encoding="utf-8")


def reemplazar_marcadores(carpeta: Path, valores: dict) -> None:
    for ruta in carpeta.rglob("*.md"):
        try:
            texto = ruta.read_text(encoding="utf-8")
        except OSError:
            continue
        original = texto
        for marcador, valor in valores.items():
            texto = texto.replace(marcador, str(valor))
        if texto != original:
            ruta.write_text(texto, encoding="utf-8")


def crear_caso(
    raiz: Path,
    nombre: str,
    materia: str,
    area: str = "general",
    tipo_documento: str | None = None,
    cliente: str = "Anónimo",
    contraparte: str = "NO CONSTA",
    responsable: str = "Socio Director",
    supervisor: str = "NO CONSTA",
    confidencialidad: str = "ficticio / académico",
    director: str = "Socio Director",
    trato: str = "usted",
    titulo: str = "Director",
    estilo: str = "formal",
    presentacion: str = "completa",
    corpus: str | None = None,
    id_caso: str | None = None,
    fecha: str | None = None,
) -> dict:
    raiz = raiz.resolve()
    nombre = nombre.strip()
    if not nombre:
        raise ErrorDeCaso("El nombre del caso no puede estar vacío.")

    trato = trato.strip().lower()
    if trato == "tu":
        trato = "tú"
    if trato not in ("tú", "usted"):
        raise ErrorDeCaso("El trato debe ser «tú» o «usted».")
    presentacion = presentacion.strip().lower()
    if presentacion not in ("completa", "breve", "ninguna"):
        raise ErrorDeCaso("La presentación debe ser «completa», «breve» o «ninguna».")

    datos_materia = cargar_materia(raiz, materia)
    plantilla = raiz / PLANTILLA
    if not plantilla.is_dir():
        raise ErrorDeCaso(f"No existe la plantilla de caso: {plantilla}")

    slug = slugify(nombre)
    destino = raiz / "casos" / slug
    if destino.exists():
        raise ErrorDeCaso(
            f"Ya existe el caso «{destino}». Elige otro nombre o archiva el existente antes de crear uno nuevo."
        )

    hoy = fecha or date.today().isoformat()
    id_final = id_caso or siguiente_id(raiz, int(hoy[:4]))
    if not re.fullmatch(r"CASO-\d{4}-\d{3}", id_final):
        raise ErrorDeCaso(f"El ID «{id_final}» no tiene el formato CASO-AAAA-NNN.")

    tipo = tipo_documento or datos_materia["tipo_documento"]
    corpus_final = corpus or ", ".join(datos_materia["corpus_por_defecto"])

    shutil.copytree(plantilla, destino)
    valores = {
        "{{ID}}": id_final,
        "{{NOMBRE}}": nombre,
        "{{MATERIA}}": materia,
        "{{AREA}}": area,
        "{{TIPO_DOCUMENTO}}": tipo,
        "{{CLIENTE}}": cliente,
        "{{PARTE_CONTRARIA}}": contraparte,
        "{{RESPONSABLE}}": responsable,
        "{{SUPERVISOR}}": supervisor,
        "{{CONFIDENCIALIDAD}}": confidencialidad,
        "{{DIRECTOR}}": director,
        "{{TRATO}}": trato,
        "{{TITULO}}": titulo,
        "{{ESTILO}}": estilo,
        "{{PRESENTACION}}": presentacion,
        "{{FECHA_APERTURA}}": hoy,
        "{{PLANTILLA}}": datos_materia["plantilla"],
        "{{CHECKLIST}}": datos_materia["checklist"],
        "{{PLAZOS}}": datos_materia["plazos"],
        "{{CORPUS}}": corpus_final,
    }
    reemplazar_marcadores(destino, valores)

    fila = (
        f"| {_celda(id_final)} | `{_celda(slug)}` | {_celda(materia)} | {_celda(area)} | "
        f"{_celda(cliente)} | abierto | Ver expediente | {_celda(responsable)} | {_celda(hoy)} |"
    )
    agregar_al_indice(raiz, fila)

    return {
        "id": id_final,
        "slug": slug,
        "carpeta": destino,
        "materia": materia,
        "plantilla": datos_materia["plantilla"],
        "corpus": corpus_final,
        "director": director,
        "trato": trato,
        "presentacion": presentacion,
    }


def _preguntar(texto: str, defecto: str = "") -> str:
    sufijo = f" [{defecto}]" if defecto else ""
    respuesta = input(f"{texto}{sufijo}: ").strip()
    return respuesta or defecto


def modo_interactivo(raiz: Path) -> int:
    print("Nuevo caso — Despacho Pessoa")
    print("Enter acepta el valor entre corchetes.\n")
    materias = sorted(p.parent.name for p in (raiz / "materias").glob("*/materia.json"))
    if not materias:
        print("No hay materias en materias/. Crea una antes de continuar.", file=sys.stderr)
        return 1
    print("Materias disponibles: " + ", ".join(materias))
    materia = _preguntar("Materia", "tutela" if "tutela" in materias else materias[0])
    try:
        datos = cargar_materia(raiz, materia)
    except ErrorDeCaso as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    nombre = _preguntar("Nombre del caso")
    if not nombre:
        print("Error: el nombre es obligatorio.", file=sys.stderr)
        return 1
    director = _preguntar("¿Cómo quiere que lo llame? (puede ser un alias)", "Socio Director")
    trato = _preguntar("¿Trato de tú o de usted?", "usted")
    titulo = _preguntar("Título (Director, Doctor, Abogado...)", "Director")
    estilo = _preguntar("Estilo (formal / cercano)", "formal")
    presentacion = _preguntar("Presentación (completa / breve / ninguna)", "completa")
    area = _preguntar("Área (salud, laboral, familia, civil, ...)", "general")
    tipo = _preguntar("Tipo de documento", datos["tipo_documento"])
    cliente = _preguntar("Cliente / usuario", "Anónimo")
    contraparte = _preguntar("Parte contraria", "NO CONSTA")
    responsable = _preguntar("Responsable", "Socio Director")
    supervisor = _preguntar("Supervisor", "NO CONSTA")
    confidencialidad = _preguntar("Nivel de confidencialidad", "ficticio / académico")
    corpus = _preguntar("Corpus (rutas separadas por coma)", ", ".join(datos["corpus_por_defecto"]))
    print("\nResumen:")
    print(f"  Nombre: {nombre}")
    print(f"  Director: {director} ({trato})")
    print(f"  Presentación: {presentacion}")
    print(f"  Materia: {materia} — {datos['nombre']}")
    print(f"  Tipo: {tipo}")
    print(f"  Plantilla: {datos['plantilla']}")
    print(f"  Corpus: {corpus}")
    if _preguntar("¿Crear el caso? (s/n)", "s").lower() not in ("s", "si", "sí", "y", "yes"):
        print("Cancelado.")
        return 0
    try:
        resultado = crear_caso(
            raiz=raiz, nombre=nombre, materia=materia, area=area, tipo_documento=tipo,
            cliente=cliente, contraparte=contraparte, responsable=responsable,
            supervisor=supervisor, confidencialidad=confidencialidad, corpus=corpus,
            director=director, trato=trato, titulo=titulo, estilo=estilo,
            presentacion=presentacion,
        )
    except ErrorDeCaso as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _imprimir_resultado(resultado)
    return 0


def _imprimir_resultado(resultado: dict) -> None:
    print(f"\nCaso creado: {resultado['carpeta']}")
    print(f"ID: {resultado['id']}")
    print(f"Director: {resultado['director']} ({resultado['trato']})")
    print(f"Presentación: {resultado['presentacion']}")
    print(f"Materia: {resultado['materia']}")
    print(f"Plantilla: {resultado['plantilla']}")
    print(f"Corpus: {resultado['corpus']}")
    print("\nSiguiente paso: abre 01-entrada/entrevista-y-pruebas.md y pega la entrevista.")
    print("Para abrir el despacho, escribe: Abrir despacho")


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", default=str(RAIZ_POR_DEFECTO), help="Raíz del proyecto")
    ap.add_argument("--nombre", help="Nombre del caso")
    ap.add_argument("--materia", help="Identificador de la materia (carpeta en materias/)")
    ap.add_argument("--area", default="general", help="Área sustantiva (salud, laboral, familia, ...)")
    ap.add_argument("--tipo", dest="tipo_documento", help="Tipo de documento")
    ap.add_argument("--cliente", default="Anónimo")
    ap.add_argument("--contraparte", default="NO CONSTA")
    ap.add_argument("--responsable", default="Socio Director")
    ap.add_argument("--supervisor", default="NO CONSTA")
    ap.add_argument("--confidencialidad", default="ficticio / académico")
    ap.add_argument("--director", default="Socio Director", help="Nombre o alias del Director")
    ap.add_argument("--trato", default="usted", choices=["tú", "tu", "usted"], help="Trato al Director")
    ap.add_argument("--titulo", default="Director", help="Director, Doctor, Abogado...")
    ap.add_argument("--estilo", default="formal", help="formal / cercano")
    ap.add_argument("--presentacion", default="completa", choices=["completa", "breve", "ninguna"],
                    help="Presentación de apertura del caso")
    ap.add_argument("--corpus", help="Rutas del corpus separadas por coma")
    ap.add_argument("--id", dest="id_caso", help="ID del caso (CASO-AAAA-NNN)")
    ap.add_argument("--fecha", help="Fecha de apertura (AAAA-MM-DD)")
    args = ap.parse_args(argv)

    raiz = Path(args.raiz).resolve()
    if not args.nombre or not args.materia:
        return modo_interactivo(raiz)
    try:
        resultado = crear_caso(
            raiz=raiz, nombre=args.nombre, materia=args.materia, area=args.area,
            tipo_documento=args.tipo_documento, cliente=args.cliente, contraparte=args.contraparte,
            responsable=args.responsable, supervisor=args.supervisor,
            confidencialidad=args.confidencialidad, director=args.director,
            trato=args.trato, titulo=args.titulo, estilo=args.estilo,
            presentacion=args.presentacion, corpus=args.corpus,
            id_caso=args.id_caso, fecha=args.fecha,
        )
    except ErrorDeCaso as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    _imprimir_resultado(resultado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
