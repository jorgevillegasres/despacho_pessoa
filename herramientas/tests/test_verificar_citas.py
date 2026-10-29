import subprocess, sys, tempfile, unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DATOS = Path(__file__).resolve().parent / "datos"
sys.path.insert(0, str(RAIZ / "herramientas"))
import verificar_citas as vc  # noqa: E402

SCRIPT = str(RAIZ / "herramientas/verificar_citas.py")


class TestNormalizar(unittest.TestCase):
    def test_comillas_y_espacios(self):
        self.assertEqual(vc.normalizar('  “Hola,   mundo”  '), 'Hola, mundo')
        self.assertEqual(vc.normalizar("> «Hola»\n> mundo"), "Hola mundo")
        self.assertEqual(vc.normalizar("**Hola** *mundo*"), "Hola mundo")


class TestInvestigacion(unittest.TestCase):
    def setUp(self):
        self.res = vc.verificar_investigacion(DATOS / "casos/caso-prueba/investigacion.md", raiz=DATOS)

    def get(self, ficha):
        return next(r for r in self.res if r.ficha == ficha)

    def test_ficha_literal_coincide(self):
        f1 = self.get("FICHA-01")
        self.assertEqual(f1.veredicto, "COINCIDE")

    def test_ficha_alterada_no_coincide(self):
        f2 = self.get("FICHA-02")
        self.assertEqual(f2.veredicto, "NO COINCIDE")

    def test_archivo_inexistente_fuera_del_corpus(self):
        f3 = self.get("FICHA-03")
        self.assertEqual(f3.veredicto, "FUERA DEL CORPUS")
        self.assertNotIn("no existe en el ordenamiento", f3.detalle.lower())

    def test_distractor_no_citable(self):
        f4 = self.get("FICHA-04")
        self.assertEqual(f4.veredicto, "NO COINCIDE")
        self.assertIn("no es citable", f4.detalle)

    def test_ruta_que_escapa_o_absoluta_fuera_del_corpus(self):
        self.assertEqual(self.get("FICHA-05").veredicto, "FUERA DEL CORPUS")
        self.assertEqual(self.get("FICHA-06").veredicto, "FUERA DEL CORPUS")

    def test_resumen_no_citable(self):
        with tempfile.TemporaryDirectory() as t:
            raiz = Path(t)
            (raiz / "fuentes").mkdir()
            (raiz / "fuentes/res.md").write_text(
                "# Resumen\n\n- **Tipo de contenido:** resumen\n\n## Parte\n"
                "> \"Texto del resumen suficientemente largo.\"\n", encoding="utf-8")
            inv = raiz / "investigacion.md"
            inv.write_text(
                "### FICHA-01: X\n- **Archivo en el corpus (`fuentes/`):** `fuentes/res.md`\n"
                "- **Ubicación exacta dentro del archivo:** `Parte`\n"
                "- **Cita textual literal (entre comillas):**\n"
                "  > \"Texto del resumen suficientemente largo.\"\n", encoding="utf-8")
            r = vc.verificar_investigacion(inv, raiz=raiz)
            self.assertEqual(r[0].veredicto, "NO COINCIDE")
            self.assertIn("no es citable", r[0].detalle)


class TestBorrador(unittest.TestCase):
    def setUp(self):
        self.res = vc.verificar_borrador(DATOS / "casos/caso-prueba/borrador.md", raiz=DATOS)

    def test_tres_citas_detectadas(self):
        self.assertEqual(len(self.res), 3)

    def test_veredictos(self):
        por_ficha = {r.ficha: r.veredicto for r in self.res}
        self.assertEqual(por_ficha["FICHA-01"], "COINCIDE")
        self.assertEqual(por_ficha["FICHA-02"], "NO COINCIDE")
        self.assertEqual(por_ficha["FICHA-07"], "NO COINCIDE")

    def test_ficha_declara_otro_archivo(self):
        res = vc.verificar_borrador(DATOS / "casos/caso-prueba/borrador-otro-archivo.md", raiz=DATOS)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].veredicto, "NO COINCIDE")
        self.assertIn("la ficha declara otro archivo", res[0].detalle)


class TestCLI(unittest.TestCase):
    def correr(self, *args):
        return subprocess.run([sys.executable, SCRIPT, *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_sale_1_si_hay_fallas(self):
        r = self.correr(DATOS / "casos/caso-prueba/borrador.md", "--raiz", DATOS)
        self.assertEqual(r.returncode, 1)
        self.assertIn("✔", r.stdout)
        self.assertIn("✘", r.stdout)
        self.assertIn("sin ficha autorizada", r.stdout)

    def test_borrador_sin_citas_sale_1(self):
        r = self.correr(DATOS / "casos/caso-vacio/borrador.md", "--raiz", DATOS,
                        "--investigacion", DATOS / "casos/caso-prueba/investigacion.md")
        self.assertEqual(r.returncode, 1)
        self.assertIn("[Fuente: FICHA-XX", r.stdout)

    def test_nombre_de_archivo_invalido_sale_2(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "otro.md"
            p.write_text("x", encoding="utf-8")
            r = self.correr(p, "--raiz", DATOS)
            self.assertEqual(r.returncode, 2)


import unicodedata  # noqa: E402

Q1 = "Toda persona tiene derecho a presentar peticiones respetuosas y a obtener pronta resolución."
NORMA = (
    "# Norma\n\n- **Tipo de contenido:** literal\n- **Identificador Oficial:** Ley de Prueba 1 de 2026\n\n"
    "## Artículo 1 — Objeto\n> \"" + Q1 + "\"\n"
)


def ficha(n, archivo, ubic, cita_bloque):
    return (
        f"### FICHA-{n:02d}: X\n- **Tipo de fuente:** Ley\n"
        f"- **Archivo en el corpus (`fuentes/`):** `{archivo}`\n"
        f"- **Ubicación exacta dentro del archivo:** `{ubic}`\n"
        f"- **Cita textual literal (entre comillas):**\n{cita_bloque}\n"
        f"- **Hecho(s) del caso al que se aplica:** `HECHO-01`\n\n"
    )


def bq(texto):
    return f"  > \"{texto}\"\n"


class Base(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.raiz = Path(self._t.name)
        (self.raiz / "fuentes").mkdir()
        (self.raiz / "caso").mkdir()
        self.inv = self.raiz / "caso/investigacion.md"
        self.borr = self.raiz / "caso/borrador.md"

    def corpus(self, nombre, texto):
        p = self.raiz / "fuentes" / nombre
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")

    def escribir(self, inv=None, borr=None):
        if inv is not None:
            self.inv.write_text(inv, encoding="utf-8")
        if borr is not None:
            self.borr.write_text(borr, encoding="utf-8")

    def inv_res(self):
        return vc.verificar_investigacion(self.inv, raiz=self.raiz)

    def borr_res(self):
        return vc.verificar_borrador(self.borr, raiz=self.raiz, investigacion=self.inv)

    def cli(self, ruta):
        return subprocess.run([sys.executable, SCRIPT, str(ruta), "--raiz", str(self.raiz)],
                              capture_output=True, text=True, encoding="utf-8")


class TestBorradorFalloCerrado(Base):
    def test_diez_etiquetas_con_formatos_raros_dan_diez_resultados(self):
        A = "fuentes/n.md"
        self.corpus("n.md", NORMA)
        self.escribir(ficha(1, A, "Artículo 1 — Objeto", bq(Q1)))
        partes = [
            f'"{Q1}" [Fuente: FICHA-01 de investigacion.md — Archivo: {A}]',
            f'"{Q1}" [Fuente: FICHA-01]',
            f'"{Q1}" [Fuente: FICHA-01 de investigacion.md — Archivo: `{A}`]',
            f'"{Q1}". [Fuente: FICHA-01 - Archivo: {A}]',
            f'**"{Q1}"** **[Fuente: FICHA-01]**',
            f'("{Q1}" (Fuente: FICHA-01))',
            f'La Corte dijo «"{Q1}"» [Fuente: FICHA-01]',
            '"Hola" [Fuente: FICHA-01]',
            f'"{Q1}" [Fuente: FICHA-01 de investigacion.md — Archivo: {A}]',
            f'"{Q1}" [Fuente: FICHA-01]',
        ]
        self.escribir(borr="# B\n\n" + "\n\n".join(partes) + "\n")
        res = self.borr_res()
        self.assertEqual(len(res), 10)
        for i, r in enumerate(res):
            self.assertEqual(r.veredicto, "NO COINCIDE" if i == 7 else "COINCIDE", (i, r))
        self.assertEqual(self.cli(self.borr).returncode, 1)

    def test_comillas_anidadas_reproducidas_coincide_y_alteradas_no(self):
        self.corpus("n.md", NORMA)
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)))
        ok = f'La Corte dijo «"{Q1}"» [Fuente: FICHA-01]' + chr(10)
        self.escribir(borr=ok)
        self.assertEqual(self.borr_res()[0].veredicto, "COINCIDE")
        self.escribir(borr=ok.replace("tiene derecho a", "tiene el deber de"))
        self.assertEqual(self.borr_res()[0].veredicto, "NO COINCIDE")

    def test_borrador_que_no_reproduce_la_ficha(self):
        self.corpus("n.md", NORMA)
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)),
                      '"Algo completamente distinto que el juez nunca dijo." [Fuente: FICHA-01]\n')
        r = self.borr_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("el borrador no reproduce la cita de la ficha", r.detalle)

    def test_ficha_inexistente_es_sin_ficha_autorizada(self):
        self.corpus("n.md", NORMA)
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)),
                      f'"{Q1}" [Fuente: FICHA-09]\n')
        r = self.borr_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("sin ficha autorizada en investigacion.md (Regla 2)", r.detalle)

    def test_ficha_sin_archivo(self):
        self.corpus("n.md", NORMA)
        self.escribir("### FICHA-01: X\n- **Cita textual literal (entre comillas):**\n" + bq(Q1),
                      f'"{Q1}" [Fuente: FICHA-01]\n')
        r = self.borr_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("la ficha no declara archivo", r.detalle)

    def test_borrador_no_utf8_sale_2(self):
        self.escribir(inv="### FICHA-01: X\n")
        self.borr.write_bytes(b"\xff\xfe\x00 cita \xe9\xe9 [Fuente: FICHA-01]")
        self.assertEqual(self.cli(self.borr).returncode, 2)


class TestFichaYCorpusRigor(Base):
    def test_ficha_multiparrafo_con_segundo_parrafo_inventado(self):
        P2 = "Segundo párrafo realmente presente en la norma de prueba."
        self.corpus("n.md", NORMA + "> \"" + P2 + "\"\n")
        ok = bq(Q1) + "\n" + bq(P2)
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", ok))
        self.assertEqual(self.inv_res()[0].veredicto, "COINCIDE")
        mal = bq(Q1) + "\n" + bq("Segundo párrafo inventado que la norma nunca contuvo.")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", mal))
        self.assertEqual(self.inv_res()[0].veredicto, "NO COINCIDE")

    def test_cita_inline_en_la_linea_de_la_etiqueta(self):
        self.corpus("n.md", NORMA)
        txt = ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", "").replace(
            "(entre comillas):**\n", f"(entre comillas):** \"{Q1}\"\n")
        self.escribir(txt)
        self.assertEqual(self.inv_res()[0].veredicto, "COINCIDE")

    def test_cita_tomada_de_metadatos_del_encabezado(self):
        self.corpus("n.md", NORMA)
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq("Ley de Prueba 1 de 2026")))
        self.assertEqual(self.inv_res()[0].veredicto, "NO COINCIDE")

    def test_cita_cosida_entre_dos_blockquotes(self):
        A, B = "Primera parte del texto citable aquí.", "Segunda parte del texto citable aquí."
        self.corpus("n.md", NORMA + "\n## Artículo 2\n> \"" + A + "\"\n\n> \"" + B + "\"\n")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 2", bq(A + " " + B)))
        self.assertEqual(self.inv_res()[0].veredicto, "NO COINCIDE")

    def test_tipo_distractor_con_backticks(self):
        self.corpus("n.md", NORMA.replace("literal", "`distractor`"))
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)))
        r = self.inv_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("no es citable", r.detalle)

    def test_nombre_de_archivo_distractor(self):
        self.corpus("DISTRACTOR-x.md", NORMA)
        self.escribir(ficha(1, "fuentes/DISTRACTOR-x.md", "Artículo 1 — Objeto", bq(Q1)))
        r = self.inv_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("no es citable", r.detalle)

    def test_sin_tipo_de_contenido_avisa(self):
        self.corpus("n.md", "# N\n\n## Artículo 1 — Objeto\n> \"" + Q1 + "\"\n")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)))
        r = self.inv_res()[0]
        self.assertEqual(r.veredicto, "COINCIDE")
        self.assertIn("el archivo no declara Tipo de contenido", r.detalle)

    def test_ubicacion_con_limite_de_palabra(self):
        self.corpus("n.md", NORMA.replace("## Artículo 1 — Objeto", "## Artículo 10 — Otro"))
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1", bq(Q1)))
        r = self.inv_res()[0]
        self.assertEqual(r.veredicto, "COINCIDE")
        self.assertIn("⚠", r.detalle)
        self.assertIn("la cita está bajo «Artículo 10 — Otro», no bajo «Artículo 1»", r.detalle)

    def test_corpus_en_nfd(self):
        self.corpus("n.md", unicodedata.normalize("NFD", NORMA))
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)))
        self.assertEqual(self.inv_res()[0].veredicto, "COINCIDE")

    def test_archivo_existente_fuera_de_fuentes(self):
        (self.raiz / "x.md").write_text(NORMA, encoding="utf-8")
        self.escribir(ficha(1, "fuentes/../x.md", "Artículo 1 — Objeto", bq(Q1)))
        self.assertEqual(self.inv_res()[0].veredicto, "FUERA DEL CORPUS")

    def test_etiqueta_con_mayusculas_y_dos_puntos_fuera_del_negrita(self):
        self.corpus("n.md", NORMA)
        txt = ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)).replace(
            "- **Archivo en el corpus (`fuentes/`):** `", "- **Archivo en el Corpus**: `")
        self.escribir(txt)
        self.assertEqual(self.inv_res()[0].veredicto, "COINCIDE")

    def test_ficha_mal_formada(self):
        self.escribir("### FICHA-01: X\n- **Cita textual literal (entre comillas):**\n" + bq(Q1))
        r = self.inv_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("ficha mal formada: falta", r.detalle)

    def test_corpus_ilegible(self):
        p = self.raiz / "fuentes/n.md"
        p.write_bytes(b"\xff\xfe\x00# \xe9\xe9")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)))
        r = self.inv_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("no se pudo leer", r.detalle)


class TestCitaEntrecomillada(Base):
    T = " [Fuente: FICHA-01 de investigacion.md — Archivo: fuentes/n.md]"

    def preparar(self, borrador):
        self.corpus("n.md", NORMA)
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1)), borrador)
        return self.borr_res()

    def test_sufijo_inventado(self):
        r = self.preparar(f'"{Q1} Además se indemnizará de oficio."{self.T}\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "NO COINCIDE")
        self.assertIn("la cita entrecomillada añade texto que no está en la ficha", r[0].detalle)

    def test_prefijo_inventado(self):
        r = self.preparar(f'"Siempre y sin excepción, {Q1}"{self.T}\n')
        self.assertEqual(r[0].veredicto, "NO COINCIDE")
        self.assertIn("añade texto", r[0].detalle)

    def test_dos_citas_una_etiqueta(self):
        r = self.preparar(f'"Texto inventado de otra fuente totalmente." y "{Q1}"{self.T}\n')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0].veredicto, "COINCIDE")
        self.assertEqual(r[1].veredicto, "NO COINCIDE")
        self.assertIn("cita entre comillas sin etiqueta propia", r[1].detalle)

    def test_cita_sin_comillas_es_referencia_con_aviso(self):
        r = self.preparar(f'{Q1}{self.T}')
        self.assertEqual(r[0].veredicto, "COINCIDE")
        self.assertIn("sin cita textual", r[0].detalle)

    def test_cita_parcial_coincide(self):
        r = self.preparar(f'"tiene derecho a presentar peticiones respetuosas"{self.T}\n')
        self.assertEqual(r[0].veredicto, "COINCIDE")

    def test_cita_cortada_a_mitad_de_palabra(self):
        r = self.preparar(f'"iene derecho a presentar peticiones respetuosas"{self.T}\n')
        self.assertEqual(r[0].veredicto, "NO COINCIDE")
        r = self.preparar(f'"tiene derecho a presentar peticiones respetuos"{self.T}\n')
        self.assertEqual(r[0].veredicto, "NO COINCIDE")

    def test_etiquetas_con_rotulo_distinto(self):
        for tag in ("[FICHA-01]", "[Fuentes: FICHA-01]"):
            r = self.preparar(f'"{Q1}" {tag}\n')
            self.assertEqual(len(r), 1, tag)
            self.assertEqual(r[0].veredicto, "COINCIDE", tag)
            self.assertIn("etiqueta con formato distinto a [Fuente: FICHA-XX", r[0].detalle)

    def test_cita_sin_etiqueta_en_el_borrador(self):
        r = self.preparar(f'"{Q1}"{self.T}\n\nLa Corte afirmó "Una frase entrecomillada sin etiqueta alguna."\n')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1].veredicto, "NO COINCIDE")
        self.assertIn("cita entre comillas sin etiqueta [Fuente: FICHA-XX]", r[1].detalle)
        self.assertEqual(r[1].linea, 3)

    def test_etiqueta_sin_archivo_avisa(self):
        r = self.preparar(f'"{Q1}" [Fuente: FICHA-01]\n')
        self.assertEqual(r[0].veredicto, "COINCIDE")
        self.assertIn("la etiqueta no indica Archivo", r[0].detalle)

    def test_ficha_multiparrafo_en_el_borrador(self):
        P2 = "Segundo párrafo realmente presente en la norma de prueba."
        self.corpus("n.md", NORMA + "> \"" + P2 + "\"\n")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1) + "\n" + bq(P2)),
                      f'"{Q1}" "{P2}"{self.T}\n')
        r = self.borr_res()
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "COINCIDE")

    def test_cita_demasiado_corta(self):
        self.corpus("n.md", NORMA + "\n## Artículo 3\n> \"Corta frase.\"\n")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 3", bq("Corta frase")))
        r = self.inv_res()[0]
        self.assertEqual(r.veredicto, "NO COINCIDE")
        self.assertIn("demasiado corta", r.detalle)

    def test_blockquotes_adyacentes_no_se_cosen(self):
        A, B = "Primera parte del texto citable aquí.", "Segunda parte del texto citable aquí."
        self.corpus("n.md", NORMA + "\n## Artículo 2\n> \"" + A + "\"\n> \"" + B + "\"\n")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 2", bq(A + " " + B)))
        self.assertEqual(self.inv_res()[0].veredicto, "NO COINCIDE")
        self.escribir(ficha(1, "fuentes/n.md", "Artículo 2", bq(B)))
        self.assertEqual(self.inv_res()[0].veredicto, "COINCIDE")

    def test_archivo_real_ley_1755(self):
        cita = ("Toda persona tiene derecho a presentar peticiones respetuosas a las autoridades, en los "
                "términos señalados en este código, por motivos de interés general o particular, y a "
                "obtener pronta resolución completa y de fondo sobre la misma.")
        self.escribir(ficha(1, "fuentes/00_transversal/ley_1755_de_2015_peticion.md", "Artículo 13", bq(cita)))
        r = vc.verificar_investigacion(self.inv, raiz=RAIZ)[0]
        self.assertEqual(r.veredicto, "COINCIDE", r.detalle)


class TestPlantilla(Base):
    A = "fuentes/n.md"
    T = " [Fuente: FICHA-01 de investigacion.md — Archivo: fuentes/n.md]"

    def preparar(self, borrador, corpus=NORMA, cita=Q1):
        self.corpus("n.md", corpus)
        self.escribir(ficha(1, self.A, "Artículo 1 — Objeto", bq(cita)), borrador)
        return self.borr_res()

    def test_etiqueta_entre_backticks_como_en_la_plantilla(self):
        r = self.preparar(f'"{Q1}" `{self.T.strip()}`.\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "COINCIDE")

    def test_etiqueta_sin_cita_es_referencia(self):
        r = self.preparar(f'La acción es procedente según la norma `{self.T.strip()}`.\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "COINCIDE")
        self.assertIn("referencia a la ficha sin cita textual; no hay texto que cotejar", r[0].detalle)

    def test_texto_de_la_ficha_sin_comillas_es_referencia(self):
        r = self.preparar(f'{Q1}{self.T}\n')
        self.assertEqual(r[0].veredicto, "COINCIDE")
        self.assertIn("sin cita textual", r[0].detalle)

    def test_cita_de_hechos_en_la_seccion_de_hechos_no_exige_ficha(self):
        r = self.preparar('## II. HECHOS\n1. Dice: "La entidad no respondió la petición en el término legal." '
                          '`[Fuente: HECHO-01 de hechos.md — Prueba P-01]`.\n')
        self.assertEqual(r, [])

    def test_cita_de_hechos_fuera_de_la_seccion_de_hechos_avisa(self):
        r = self.preparar('## III. FUNDAMENTOS\nDice: "La entidad no respondió la petición en el término legal." '
                          '`[Fuente: HECHO-01 de hechos.md — Prueba P-01]`.\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "AVISO")
        self.assertIn("cita bajo etiqueta HECHO fuera de la sección de hechos: no se coteja aquí", r[0].detalle)
        out = self.cli(self.borr)
        self.assertEqual(out.returncode, 1, out.stdout)
        self.assertIn("fuera de la sección de hechos", out.stdout)
        self.assertIn("[Fuente: FICHA-XX", out.stdout)

    def test_cita_de_hechos_antes_de_etiqueta_de_ficha_en_el_mismo_parrafo(self):
        r = self.preparar('## II. HECHOS\n"La entidad no respondió la petición en el término legal." '
                          '[Fuente: HECHO-01 de hechos.md — Prueba P-01] y la ley dispone '
                          f'"{Q1}"{self.T}\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "COINCIDE")

    def test_marcadores_de_plantilla_se_ignoran(self):
        r = self.preparar('Nota "[Cita textual exacta de la norma o sentencia]" y '
                          '[NO CONSTA EN EL EXPEDIENTE "dato inventado de relleno largo"] y '
                          '`[Fuente: FICHA-XX "texto largo de ejemplo aquí"]`.\n')
        self.assertEqual(r, [])

    def test_corchetes_ordinarios_no_ocultan_citas(self):
        r = self.preparar('La Corte [ha sostenido que "una regla inventada que la Corte nunca dijo" '
                          'en reiterada jurisprudencia].\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "NO COINCIDE")
        self.assertIn("sin etiqueta", r[0].detalle)

    def test_backticks_ordinarios_no_ocultan_citas(self):
        r = self.preparar('`"una regla inventada que la Corte nunca dijo"`\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "NO COINCIDE")
        self.assertIn("sin etiqueta", r[0].detalle)

    def test_comillas_desbalanceadas_antes_de_la_cita(self):
        r = self.preparar(f'dijo "la EPS debe indemnizar siempre y "{Q1}"{self.T}\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "NO COINCIDE")
        self.assertIn("comillas desbalanceadas antes de la cita", r[0].detalle)

    def test_referencia_sin_cita_se_muestra_con_circulo_y_referencia(self):
        self.preparar(f'Es procedente por la norma{self.T}\n')
        out = self.cli(self.borr).stdout
        linea = [l for l in out.splitlines() if "FICHA-01" in l][0]
        self.assertTrue(linea.startswith("◌"), linea)
        self.assertIn("REFERENCIA", linea)
        self.assertNotIn("COINCIDE", linea)
        self.assertNotIn("✔", linea)

    def test_resumen_separa_referencias_sin_cita(self):
        t = self.T
        r = self.preparar(f'"{Q1}"{t}\n\nEs procedente por la norma{t}\n\n'
                          f'"Texto inventado largo que no está en la ficha."{t}\n')
        self.assertEqual([x.veredicto for x in r], ["COINCIDE", "COINCIDE", "NO COINCIDE"])
        out = self.cli(self.borr).stdout
        self.assertIn("Resumen: 1 citas cotejadas · 1 referencias sin cita textual (revisar a mano) · "
                      "1 con problemas.", out)

    def test_cita_sola_dentro_de_corchetes_si_se_marca(self):
        r = self.preparar('["Una frase inventada entre corchetes sin etiqueta."]\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "NO COINCIDE")

    def test_parentesis_despues_de_la_cita(self):
        r = self.preparar(f'"{Q1}" (art. 86 CP){self.T}\n')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "COINCIDE")
        self.assertNotIn("sin etiqueta", r[0].detalle)

    def test_mencion_suelta_de_ficha_no_es_etiqueta(self):
        r = self.preparar('Como explica la FICHA-01 de este expediente, la acción procede.\n')
        self.assertEqual(r, [])

    def test_comillas_internas_se_amplian(self):
        corpus = NORMA.replace(Q1, 'La presente acción es "improcedente" hoy.')
        cita = 'La presente acción es "improcedente" hoy.'
        r = self.preparar(f'"{cita}"{self.T}\n', corpus=corpus, cita=cita)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].veredicto, "COINCIDE", r[0].detalle)

    def test_salida_ordenada_por_linea(self):
        self.preparar(f'Frase "Una frase entrecomillada sin etiqueta alguna." aquí.\n\n"{Q1}"{self.T}\n')
        out = self.cli(self.borr).stdout
        self.assertLess(out.index("(sin etiqueta)"), out.index("FICHA-01"))

    def test_borrador_conforme_a_modelo_tutela_con_corpus_real(self):
        d = DATOS / "casos/caso-plantilla"
        r = subprocess.run([sys.executable, SCRIPT, str(d / "borrador.md"), "--raiz", str(RAIZ)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout)
        res = vc.verificar_borrador(d / "borrador.md", raiz=RAIZ)
        self.assertTrue(res)
        self.assertTrue(all(x.veredicto == "COINCIDE" for x in res), res)


class TestSalida(Base):
    def test_rechaza_rutas_bajo_privado(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "casos" / "c" / "privado"
            d.mkdir(parents=True)
            (d / "borrador.md").write_text("x", encoding="utf-8")
            (d / "investigacion.md").write_text("x", encoding="utf-8")
            otro = Path(tmp) / "casos" / "c" / "borrador.md"
            otro.write_text("x", encoding="utf-8")
            r = subprocess.run([sys.executable, SCRIPT, str(d / "borrador.md"), "--raiz", tmp],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 2)
            self.assertIn("las notas internas del despacho no se usan como entrada", r.stderr)
            r = subprocess.run([sys.executable, SCRIPT, str(otro), "--raiz", tmp,
                                "--investigacion", str(d / "investigacion.md")],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 2)
            self.assertIn("las notas internas del despacho no se usan como entrada", r.stderr)
            mayus = Path(tmp) / "casos" / "c2" / "PRIVADO"
            mayus.mkdir(parents=True)
            (mayus / "borrador.md").write_text("x", encoding="utf-8")
            r = subprocess.run([sys.executable, SCRIPT, str(mayus / "borrador.md"), "--raiz", tmp],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 2)
            self.assertIn("las notas internas del despacho no se usan como entrada", r.stderr)

    def test_linea_y_cita_en_la_salida_y_duplicados(self):
        self.corpus("n.md", NORMA)
        f = ficha(1, "fuentes/n.md", "Artículo 1 — Objeto", bq(Q1))
        self.escribir(inv="# I\n\n" + f + f)
        r = self.cli(self.inv)
        self.assertIn("L3", r.stdout)
        self.assertIn(Q1[:60], r.stdout)
        self.assertIn("duplicada", r.stdout)

    def test_investigacion_sin_fichas_describe_el_formato(self):
        self.escribir(inv="# I\n\nnada\n")
        r = self.cli(self.inv)
        self.assertEqual(r.returncode, 1)
        self.assertIn("### FICHA-", r.stdout)


if __name__ == "__main__":
    unittest.main()
