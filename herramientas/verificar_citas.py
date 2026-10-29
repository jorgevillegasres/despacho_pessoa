#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador determinístico de citas — Despacho Pessoa (Reglas 2 y 7 del Estatuto).

Comprueba que cada cita textual declarada en investigacion.md (fichas) o usada
en borrador.md existe LITERALMENTE en el archivo de fuentes/ que se declara.
Falla cerrado: toda etiqueta [Fuente: FICHA-XX] del borrador produce un
veredicto; nada se descarta en silencio.

Uso:
  python herramientas/verificar_citas.py casos/<caso>/investigacion.md
  python herramientas/verificar_citas.py casos/<caso>/borrador.md [--investigacion ruta]
Códigos: 0 todo coincide · 1 hay NO COINCIDE o FUERA DEL CORPUS · 2 error de uso.

Vocabulario (Regla 7): este script solo sabe lo que hay en fuentes/. «FUERA DEL
CORPUS» significa que el archivo no está en la carpeta; nunca significa que no
exista en el ordenamiento jurídico.
"""
import argparse
import functools
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

RAIZ_POR_DEFECTO = Path(__file__).resolve().parents[1]
COMILLAS = {"“": '"', "”": '"', "«": '"', "»": '"', "„": '"', "‘": "'", "’": "'"}
TIPOS_NO_CITABLES = {"distractor", "resumen"}
LARGO_MINIMO_CITA = 15
CIERRES = '"”»'
APERTURAS = '"“«'


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFC", texto)
    for a, b in COMILLAS.items():
        texto = texto.replace(a, b)
    texto = re.sub(r"^\s*>+\s?", "", texto, flags=re.M)        # quita > de blockquote
    texto = re.sub(r"\*\*|__|\*|_(?=\w)|(?<=\w)_", "", texto)   # quita énfasis markdown
    texto = texto.replace('"', "")                              # las comillas no son parte de la cita
    return re.sub(r"\s+", " ", texto).strip()


@dataclass
class Resultado:
    ficha: str
    archivo: str
    veredicto: str      # COINCIDE | NO COINCIDE | FUERA DEL CORPUS
    detalle: str
    cita: str = ""
    linea: int = 0


@dataclass
class Ficha:
    id: str
    linea: int
    archivo: str = ""
    ubicacion: str = ""
    parrafos: list = field(default_factory=list)

    def faltantes(self):
        f = []
        if not self.archivo:
            f.append("archivo en el corpus")
        if not self.ubicacion:
            f.append("ubicación exacta")
        if not self.parrafos:
            f.append("cita textual literal")
        return f


# ---------------------------------------------------------------- corpus

def _ruta_corpus(archivo_rel: str, raiz: Path):
    """Devuelve la ruta real solo si cae dentro de raiz/fuentes; si no, None."""
    base = (raiz / "fuentes").resolve()
    try:
        p = (raiz / archivo_rel).resolve()
        p.relative_to(base)
    except (ValueError, OSError):
        return None
    return p if p.is_file() else None


TIPO_RE = re.compile(r"\*\*Tipo de contenido:?\*\*:?\s*([^\n]+)", re.I)


def _parsear_corpus(crudo: str):
    """((texto_norm, encabezado_norm), ...) solo de cuerpos de blockquote, y tipo."""
    m = TIPO_RE.search(crudo)
    tipo = None
    if m:
        v = m.group(1).replace("`", "").replace("*", "").strip().lower()
        tipo = re.split(r"[\s,;.(]+", v)[0] if v else None
    parrafos = []
    encabezado = ""
    buf = []

    def vaciar():
        if buf:
            t = normalizar("\n".join(buf))
            if t:
                parrafos.append((t, encabezado))
            buf.clear()

    for ln in crudo.splitlines():
        st = ln.strip()
        if st.startswith("#"):
            vaciar()
            encabezado = normalizar(re.sub(r"^#+\s*", "", st))
        elif st.startswith(">"):
            if re.fullmatch(r">+\s*", st):
                vaciar()
            else:
                if buf and buf[-1].rstrip()[-1:] in CIERRES and st.lstrip("> ")[:1] in APERTURAS:
                    vaciar()    # dos citas entrecomilladas contiguas no se cosen
                buf.append(st)
        else:
            vaciar()
    vaciar()
    return tuple(parrafos), tipo


@functools.lru_cache(maxsize=256)
def _leer_corpus_cache(ruta_str: str, mtime_ns: int):
    try:
        crudo = Path(ruta_str).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return (), None, True
    parrafos, tipo = _parsear_corpus(crudo)
    return parrafos, tipo, False


def _leer_corpus(ruta: Path):
    """(parrafos, tipo_contenido|None, error)."""
    try:
        mtime = ruta.stat().st_mtime_ns
    except OSError:
        return (), None, True
    return _leer_corpus_cache(str(ruta), mtime)


def _ubicacion_coincide(declarada: str, real: str) -> bool:
    u, h = declarada.lower(), real.lower()
    for a, b in ((u, h), (h, u)):
        if a and re.search(r"(?<!\w)" + re.escape(a) + r"(?!\w)", b):
            return True
    return False


def _cotejar(ficha, archivo_rel, parrafos_cita, ubicacion, raiz, linea=0, cita="") -> Resultado:
    def res(v, d):
        return Resultado(ficha, archivo_rel, v, d, cita, linea)

    ruta = _ruta_corpus(archivo_rel, raiz)
    if ruta is None:
        return res("FUERA DEL CORPUS",
                   f"el archivo «{archivo_rel}» no está en fuentes/ (no se puede verificar; "
                   "esto no significa que la norma o sentencia no exista)")
    if "distractor" in ruta.name.lower():
        return res("NO COINCIDE", "el archivo no es citable (su nombre lo marca como DISTRACTOR)")
    parrafos, tipo, error = _leer_corpus(ruta)
    if error:
        return res("NO COINCIDE", "el archivo está en fuentes/ pero no se pudo leer (codificación)")
    if tipo in TIPOS_NO_CITABLES:
        return res("NO COINCIDE", f"el archivo no es citable (tipo: {tipo})")
    avisos = []
    primeros_encabezados = None
    for i, p in enumerate(parrafos_cita, 1):
        c = normalizar(p)
        if len(c) < LARGO_MINIMO_CITA:
            return res("NO COINCIDE",
                       f"la cita es demasiado corta (menos de {LARGO_MINIMO_CITA} caracteres) para verificarla")
        halladas = [h for t, h in parrafos if c in t]
        if not halladas:
            donde = f" (párrafo {i} de {len(parrafos_cita)})" if len(parrafos_cita) > 1 else ""
            return res("NO COINCIDE", f"la cita no aparece literalmente en un mismo párrafo citado del archivo{donde}")
        if primeros_encabezados is None:
            primeros_encabezados = halladas
    if ubicacion and primeros_encabezados is not None:
        u = normalizar(ubicacion)
        if not any(_ubicacion_coincide(u, h) for h in primeros_encabezados):
            real = primeros_encabezados[0] or "(sin encabezado)"
            avisos.append(f"⚠ aviso: la cita está bajo «{real}», no bajo «{ubicacion}»")
    if tipo is None:
        avisos.append("⚠ aviso: el archivo no declara Tipo de contenido")
    return res("COINCIDE", " ".join(["la cita aparece literalmente en el archivo"] + avisos))


# ---------------------------------------------------------------- fichas

FICHA_RE = re.compile(r"^###\s+(FICHA-\d+)[^\n]*\n(.*?)(?=^###\s+FICHA-|\Z)", re.S | re.M)
ARCHIVO_RE = re.compile(r"Archivo en el corpus[^\n]*?:[\s*:]*`?([^`\n]+?)`?[\s*]*$", re.I | re.M)
UBICACION_RE = re.compile(r"Ubicaci[oó]n exacta[^\n]*?:[\s*:]*`?([^`\n]+?)`?[\s*]*$", re.I | re.M)
CITA_ETIQUETA_RE = re.compile(r"Cita textual literal[^\n]*?:[\s*]*(.*)$", re.I)


def _parsear_cita(cuerpo: str) -> list:
    lineas = cuerpo.splitlines()
    ini = next((i for i, ln in enumerate(lineas) if re.search(r"Cita textual literal", ln, re.I)), None)
    if ini is None:
        return []
    parrafos, buf = [], []

    def vaciar():
        if buf:
            t = "\n".join(buf)
            if normalizar(t):
                parrafos.append(t)
            buf.clear()

    m = CITA_ETIQUETA_RE.search(lineas[ini])
    if m and m.group(1).strip("* \t"):
        buf.append(m.group(1))
    for ln in lineas[ini + 1:]:
        st = ln.strip()
        if st == "" or re.fullmatch(r">+", st):
            vaciar()
        elif st.startswith(">"):
            buf.append(st)
        else:
            break
    vaciar()
    return parrafos


def _parsear_fichas(ruta: Path) -> list:
    texto = Path(ruta).read_text(encoding="utf-8")
    fichas = []
    for m in FICHA_RE.finditer(texto):
        cuerpo = m.group(2)
        a = ARCHIVO_RE.search(cuerpo)
        u = UBICACION_RE.search(cuerpo)
        fichas.append(Ficha(m.group(1), texto.count("\n", 0, m.start()) + 1,
                            a.group(1).strip() if a else "",
                            u.group(1).strip() if u else "",
                            _parsear_cita(cuerpo)))
    return fichas


def fichas_duplicadas(ruta: Path) -> list:
    vistas, avisos = {}, []
    for f in _parsear_fichas(ruta):
        if f.id in vistas:
            avisos.append(f"⚠ {f.id} duplicada en {Path(ruta).name} (líneas {vistas[f.id]} y {f.linea}); "
                          "se usa la primera")
        else:
            vistas[f.id] = f.linea
    return avisos


def verificar_investigacion(ruta: Path, raiz: Path = RAIZ_POR_DEFECTO) -> list:
    resultados = []
    for f in _parsear_fichas(Path(ruta)):
        cita = "\n\n".join(f.parrafos)
        faltan = f.faltantes()
        if faltan:
            resultados.append(Resultado(f.id, f.archivo, "NO COINCIDE",
                                        "ficha mal formada: falta " + ", ".join(faltan), cita, f.linea))
        else:
            resultados.append(_cotejar(f.id, f.archivo, f.parrafos, f.ubicacion, Path(raiz), f.linea, cita))
    return resultados


# ---------------------------------------------------------------- borrador

TAG_RE = re.compile(
    r"[`(\[*]*(?:\s*\b(?:Fuentes?|Ficha)\s*:\s*|(?<=[\[(`])\s*)(FICHA-\d+)"
    r"((?:(?!FICHA-)[^\]\)\n\"“”«»]){0,200})[\]\)]*\**`?", re.I)
HECHO_TAG_RE = re.compile(r"`?\[\s*Fuente:\s*HECHO-\d+[^\]]*\]`?", re.I)
ETIQUETA_OK_RE = re.compile(r"\[\s*Fuente:\s*FICHA-\d+", re.I)
ARCHIVO_TAG_RE = re.compile(r"Archivo:\s*`?([^\s`\]\)]+)", re.I)
BLANCO_RE = re.compile(r"\n[ \t]*\n")
ENCABEZADO_RE = re.compile(r"^#+[^\n]*(?:\n|$)", re.M)
PARENTESIS_FINAL_RE = re.compile(r'\s*\([^()"“”«»\n]{1,60}\)\s*$')
CODIGO_RE = re.compile(r"`[^`\n]*`")
SEGMENTO_RE = re.compile(r'[«“"]([^«»“”"]{%d,})[»”"]' % LARGO_MINIMO_CITA)
_ABRE = {"»": "«", "”": '“"', '"': '"“'}
SIN_CITA = "⚠ referencia a la ficha sin cita textual; no hay texto que cotejar"


def _recortar(s: str) -> str:
    """Quita puntuación, énfasis, backticks y un paréntesis final (p. ej. «(art. 86 CP)»)."""
    s = s.rstrip(" \t\n.,;:*`")
    s = PARENTESIS_FINAL_RE.sub("", s)
    return s.rstrip(" \t\n.,;:*`)")


def _ultimo_segmento(sp: str, parrafos=None):
    """(indice_apertura, interior) de la cita que termina justo al final de sp, o None.

    Con comillas rectas, si el segmento más cercano no corresponde a la ficha se amplía de dos
    en dos comillas (por comillas internas) y se acepta el primero que corresponda."""
    if not sp or sp[-1] not in CIERRES:
        return None
    c = sp[-1]
    if c == '"':
        pos = [i for i in range(len(sp) - 2, -1, -1) if sp[i] in '"“']
        if not pos:
            return None
        if parrafos:
            for i in pos[::2]:
                if _juzgar_segmento(sp[i + 1:-1], parrafos) is None:
                    return i, sp[i + 1:-1]
        return pos[0], sp[pos[0] + 1:-1]
    abre = _ABRE[c]
    profundidad = 0
    for i in range(len(sp) - 2, -1, -1):
        ch = sp[i]
        if ch == c:
            profundidad += 1
        elif ch in abre:
            if profundidad == 0:
                return i, sp[i + 1:-1]
            profundidad -= 1
    return None


def _clave(texto: str) -> str:
    return normalizar(texto).rstrip(" .,;:")


def _es_porcion(seg: str, parrafo: str) -> bool:
    """seg es un tramo contiguo de parrafo, de al menos LARGO_MINIMO_CITA, que empieza y termina en límite de palabra."""
    if len(seg) < LARGO_MINIMO_CITA:
        return False
    ini = parrafo.find(seg)
    while ini != -1:
        fin = ini + len(seg)
        if (ini == 0 or not parrafo[ini - 1].isalnum()) and (fin == len(parrafo) or not parrafo[fin].isalnum()):
            return True
        ini = parrafo.find(seg, ini + 1)
    return False


def _juzgar_segmento(seg: str, parrafos: list):
    """None si el segmento es igual a un párrafo de la ficha o una porción válida; si no, el motivo."""
    s = _clave(seg)
    claves = [_clave(p) for p in parrafos]
    for k in claves:
        if s == k or _es_porcion(s, k):
            return None
    if any(k and k in s for k in claves):
        return "la cita entrecomillada añade texto que no está en la ficha"
    return "el borrador no reproduce la cita de la ficha: la cita entrecomillada no coincide con ella"


def _se_solapa(ini, fin, rangos):
    return any(ini < f and i < fin for i, f in rangos)


def _bajo_hechos(texto: str, pos: int) -> bool:
    """True si el último encabezado antes de pos menciona HECHOS."""
    ultimo = None
    for h in ENCABEZADO_RE.finditer(texto, 0, pos):
        ultimo = h.group(0)
    return ultimo is not None and "hechos" in ultimo.lower()


def _es_marcador(contenido: str) -> bool:
    c = contenido.strip()
    return c.startswith("[") or bool(re.search(r"Fuente:|NO CONSTA", c, re.I))


def _rangos_corchetes(texto: str) -> list:
    """(inicio, fin) de cada par [ ... ] dentro de una misma línea."""
    rangos, pila, base = [], [], 0
    for ln in texto.split("\n"):
        pila.clear()
        for k, ch in enumerate(ln):
            if ch == "[":
                pila.append(base + k)
            elif ch == "]" and pila:
                rangos.append((pila.pop(), base + k))
        base += len(ln) + 1
    return rangos


def verificar_borrador(ruta: Path, raiz: Path = RAIZ_POR_DEFECTO, investigacion=None) -> list:
    ruta = Path(ruta)
    inv = Path(investigacion) if investigacion else ruta.parent / "investigacion.md"
    declaradas = {}
    if inv.is_file():
        for f in _parsear_fichas(inv):
            declaradas.setdefault(f.id, f)
    texto = ruta.read_text(encoding="utf-8")

    def linea_de(pos):
        return texto.count("\n", 0, pos) + 1

    def inicio_de_tramo(fin, minimo):
        blancos = [b.end() for b in BLANCO_RE.finditer(texto, 0, fin)]
        ini = max(blancos[-1] if blancos else 0, minimo)
        for h in ENCABEZADO_RE.finditer(texto, 0, fin):
            ini = max(ini, h.end())
        return ini

    resultados = []
    manejados = []          # rangos [ini, fin) de citas entrecomilladas ya atendidas
    eventos = sorted([(m.start(), "FICHA", m) for m in TAG_RE.finditer(texto)] +
                     [(m.start(), "HECHO", m) for m in HECHO_TAG_RE.finditer(texto)], key=lambda e: e[0])
    fin_previo = 0
    for _pos, tipo, m in eventos:
        if m.start() < fin_previo:
            continue    # etiqueta solapada con la anterior
        if tipo == "HECHO":
            # las citas que terminan justo antes de una etiqueta HECHO-NN se rigen por hechos.md
            ini = inicio_de_tramo(m.start(), fin_previo)
            tramo = _recortar(texto[ini:m.start()])
            ult = _ultimo_segmento(tramo)
            if ult is not None:
                manejados.append((ini + ult[0], ini + len(tramo)))
                if not _bajo_hechos(texto, m.start()):
                    resultados.append(Resultado(
                        "(HECHO)", "", "AVISO",
                        "cita bajo etiqueta HECHO fuera de la sección de hechos: no se coteja aquí",
                        ult[1], linea_de(m.start())))
            fin_previo = m.end()
            continue

        ficha_id = m.group(1).upper()
        ma = ARCHIVO_TAG_RE.search(m.group(2))
        archivo_tag = ma.group(1).strip() if ma else ""
        linea = linea_de(m.start())
        f = declaradas.get(ficha_id)
        multi = bool(f and len(f.parrafos) > 1)
        inicio = inicio_de_tramo(m.start(), fin_previo)
        if multi:
            inicio = max(fin_previo, max([h.end() for h in ENCABEZADO_RE.finditer(texto, 0, m.start())] or [0]))
        span = _recortar(texto[inicio:m.start()])
        fin_previo = m.end()

        # segmentos entrecomillados de este tramo: (inicio_abs, fin_abs, interior)
        segmentos, otros, desbalance = [], [], False

        def buscar(s):
            return [(inicio + sm.start(), inicio + sm.end(), sm.group(1)) for sm in SEGMENTO_RE.finditer(s)]

        if multi:
            segmentos = buscar(span)
        else:
            ult = _ultimo_segmento(span, f.parrafos if f else None)
            if ult is not None:
                i0, interior = ult
                segmentos = [(inicio + i0, inicio + len(span), interior)]
                otros = buscar(span[:i0])
                previo = span[:i0]
                desbalance = (previo.count('"') % 2 == 1 or
                              previo.count("“") + previo.count("«") > previo.count("”") + previo.count("»"))
            else:
                otros = buscar(span)
        for i0, f0, _ in segmentos + otros:
            manejados.append((i0, f0))

        def res(v, d, archivo=None, _id=ficha_id, _at=archivo_tag, _sp=span, _ln=linea):
            return Resultado(_id, archivo if archivo is not None else _at, v, d, _sp, _ln)

        resultados.append(_juzgar_etiqueta(m, ficha_id, archivo_tag, f, inv, span,
                                           segmentos, res, raiz, linea, desbalance))
        for i0, _f0, interior in otros:
            resultados.append(Resultado(
                "(sin etiqueta)", "", "NO COINCIDE",
                "cita entre comillas sin etiqueta propia: cada cita necesita su [Fuente: FICHA-XX ...]",
                interior, linea_de(i0)))

    codigo = [(c.start(), c.end()) for c in CODIGO_RE.finditer(texto)]
    corchetes = _rangos_corchetes(texto)
    for sm in SEGMENTO_RE.finditer(texto):
        if _se_solapa(sm.start(), sm.end(), manejados):
            continue
        if sm.group(1).lstrip().startswith("["):
            continue    # marcador de plantilla entrecomillado: "[Cita textual exacta ...]"
        if any(a <= sm.start() and sm.end() <= b and _es_marcador(texto[a + 1:b]) for a, b in codigo):
            continue    # código en línea con una etiqueta o marcador
        if any(a <= sm.start() and sm.end() <= b and _es_marcador(texto[a + 1:b]) for a, b in corchetes):
            continue    # [Fuente: ...] o [NO CONSTA ...]
        resultados.append(Resultado(
            "(sin etiqueta)", "", "NO COINCIDE",
            "cita entre comillas sin etiqueta [Fuente: FICHA-XX] (formato: [Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/...])",
            sm.group(1), linea_de(sm.start())))
    return resultados


def _juzgar_etiqueta(m, ficha_id, archivo_tag, f, inv, span, segmentos, res, raiz, linea, desbalance=False):
    if f is None:
        return res("NO COINCIDE", f"sin ficha autorizada en {inv.name} (Regla 2)")
    if not f.archivo:
        return res("NO COINCIDE", "la ficha no declara archivo")
    if archivo_tag and archivo_tag != f.archivo:
        return res("NO COINCIDE", f"la ficha declara otro archivo: «{f.archivo}»")
    faltan = f.faltantes()
    if faltan:
        return res("NO COINCIDE", "ficha mal formada: falta " + ", ".join(faltan), f.archivo)
    r = _cotejar(ficha_id, f.archivo, f.parrafos, f.ubicacion, Path(raiz), linea, span)
    if r.veredicto != "COINCIDE":
        return r
    avisos = []
    if not segmentos:
        avisos.append(SIN_CITA)
    else:
        if desbalance:
            return res("NO COINCIDE", "comillas desbalanceadas antes de la cita", f.archivo)
        for _i, _f, interior in segmentos:
            motivo = _juzgar_segmento(interior, f.parrafos)
            if motivo:
                return res("NO COINCIDE", motivo, f.archivo)
    if not ETIQUETA_OK_RE.search(m.group(0)):
        avisos.append("⚠ aviso: etiqueta con formato distinto a [Fuente: FICHA-XX de investigacion.md — Archivo: fuentes/...]")
    if not archivo_tag:
        avisos.append("⚠ aviso: la etiqueta no indica Archivo")
    if avisos:
        r.detalle = " ".join([r.detalle] + avisos)
    return r


# ---------------------------------------------------------------- salida

MENSAJE_SIN_CITAS_BORRADOR = (
    "No se encontró ninguna cita con el formato esperado. Cada cita debe ir entre comillas "
    "seguida de la etiqueta: \"texto literal\" [Fuente: FICHA-XX de investigacion.md — "
    "Archivo: fuentes/...]"
)
MENSAJE_SIN_CITAS_INVESTIGACION = (
    "No se encontró ninguna ficha con el formato esperado. Cada ficha empieza con un encabezado "
    "`### FICHA-NN: título` y trae los campos «Archivo en el corpus», «Ubicación exacta dentro "
    "del archivo» y «Cita textual literal» (ver plantillas/ficha-cita.md)."
)


def imprimir(resultados, titulo, avisos=(), mensaje_vacio=MENSAJE_SIN_CITAS_BORRADOR) -> int:
    print(titulo)
    for a in avisos:
        print(a)
    if not any(r.veredicto != "AVISO" for r in resultados):
        for r in resultados:       # solo avisos: equivale a no haber citas con etiqueta de ficha
            print(f"⚠ L{r.linea} {r.ficha} · AVISO")
            print(f"    {r.detalle}")
        print(mensaje_vacio)
        return 1
    problemas = cotejadas = sin_cita = 0
    for r in sorted(resultados, key=lambda x: x.linea):
        c = normalizar(r.cita)
        muestra = f" · «{c[:60]}{'…' if len(c) > 60 else ''}»" if c else ""
        if r.veredicto == "AVISO":
            print(f"⚠ L{r.linea} {r.ficha} · AVISO{muestra}")
            print(f"    {r.detalle}")
            continue
        ok = r.veredicto == "COINCIDE"
        marca, palabra = ("✔" if ok else "✘"), r.veredicto
        if not ok:
            problemas += 1
        elif SIN_CITA in r.detalle:
            sin_cita += 1
            marca, palabra = "◌", "REFERENCIA"
        else:
            cotejadas += 1
        print(f"{marca} L{r.linea} {r.ficha} · {palabra} · {r.archivo or '(sin archivo)'}{muestra}")
        print(f"    {r.detalle}")
    print(f"Resumen: {cotejadas} citas cotejadas · {sin_cita} referencias sin cita textual "
          f"(revisar a mano) · {problemas} con problemas.")
    return 1 if problemas else 0


def main() -> int:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Verifica citas contra fuentes/ (Reglas 2 y 7).")
    ap.add_argument("archivo", help="casos/<caso>/investigacion.md o borrador.md")
    ap.add_argument("--investigacion", help="ruta de investigacion.md (por defecto, junto al borrador)")
    ap.add_argument("--raiz", default=str(RAIZ_POR_DEFECTO), help="raíz del proyecto (contiene fuentes/)")
    args = ap.parse_args()

    ruta = Path(args.archivo)
    raiz = Path(args.raiz)
    for entrada in (ruta, Path(args.investigacion) if args.investigacion else None):
        if entrada is not None and "privado" in {p.lower() for p in entrada.resolve().parts}:
            print("Error: las notas internas del despacho no se usan como entrada.", file=sys.stderr)
            return 2
    if ruta.name not in ("investigacion.md", "borrador.md"):
        print("Error: el archivo debe llamarse investigacion.md o borrador.md.", file=sys.stderr)
        return 2
    if not ruta.is_file():
        print(f"Error: no existe el archivo {ruta}.", file=sys.stderr)
        return 2
    try:
        if ruta.name == "investigacion.md":
            return imprimir(verificar_investigacion(ruta, raiz), f"Fichas de {ruta}",
                            fichas_duplicadas(ruta), MENSAJE_SIN_CITAS_INVESTIGACION)
        inv = Path(args.investigacion) if args.investigacion else ruta.parent / "investigacion.md"
        if not inv.is_file():
            print(f"Error: no se encontró {inv}; indique --investigacion.", file=sys.stderr)
            return 2
        return imprimir(verificar_borrador(ruta, raiz, inv), f"Citas de {ruta}", fichas_duplicadas(inv))
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error: no se pudo leer un archivo de entrada como UTF-8 ({e}).", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
