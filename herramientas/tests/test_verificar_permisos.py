import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))

import verificar_permisos as vp  # noqa: E402


class TestDecidir(unittest.TestCase):
    def setUp(self):
        self.permisos = vp.cargar_permisos(RAIZ / "despacho" / "permisos.json")

    def test_caeiro_escribe_hechos(self):
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "escribe", "casos/caso-prueba/hechos.md")
        self.assertTrue(ok)

    def test_caeiro_lee_su_propio_archivo_de_salida(self):
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "lee", "casos/caso-prueba/hechos.md")
        self.assertTrue(ok)

    def test_caeiro_no_lee_borrador(self):
        ok, motivo = vp.decidir(self.permisos, "01-observador-caeiro", "lee", "casos/caso-prueba/borrador.md")
        self.assertFalse(ok)
        self.assertIn("entrevista-y-pruebas.md", motivo)
        self.assertIn("hechos.md", motivo)

    def test_caeiro_no_escribe_borrador(self):
        ok, motivo = vp.decidir(self.permisos, "01-observador-caeiro", "escribe", "casos/caso-prueba/borrador.md")
        self.assertFalse(ok)
        self.assertIn("Regla 4", motivo)
        self.assertIn("hechos.md", motivo)

    def test_rutas_absolutas_y_backslash_se_normalizan(self):
        ruta = str(RAIZ / "casos" / "caso-prueba" / "hechos.md")
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "escribe", ruta, raiz=RAIZ)
        self.assertTrue(ok)

    def test_nadie_lee_privado(self):
        for agente in ["01-observador-caeiro", "02-investigador-search", "03-redactor-reis",
                       "04-verificador-soares", "05-diablo-campos"]:
            ok, _ = vp.decidir(self.permisos, agente, "lee", "casos/caso-prueba/privado/notas-privado.md")
            self.assertFalse(ok, agente)

    def test_search_lee_fuentes_anidadas(self):
        ok, _ = vp.decidir(self.permisos, "02-investigador-search", "lee", "fuentes/01_salud/ley_1751_de_2015_estatutaria_salud.md")
        self.assertTrue(ok)

    def test_caeiro_ejecuta_solo_calculadora(self):
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "ejecuta",
                           "python herramientas/calcular_plazos.py --modo peticion --fecha-inicio 2026-09-25")
        self.assertTrue(ok)
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "ejecuta", "python herramientas/verificar_corpus.py --sellar")
        self.assertFalse(ok)
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "ejecuta", "rm -rf fuentes")
        self.assertFalse(ok)

    def test_reis_no_ejecuta_nada(self):
        ok, _ = vp.decidir(self.permisos, "03-redactor-reis", "ejecuta", "python herramientas/calcular_plazos.py")
        self.assertFalse(ok)

    def test_agente_desconocido(self):
        ok, motivo = vp.decidir(self.permisos, "99-nadie", "lee", "ESTATUTO.md")
        self.assertFalse(ok)
        self.assertIn("no está registrado", motivo)

    def test_caeiro_lee_expediente_y_entrada_nueva(self):
        for ruta in ("casos/x/00-expediente.md", "casos/x/01-entrada/entrevista-y-pruebas.md"):
            ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "lee", ruta)
            self.assertTrue(ok, ruta)

    def test_caeiro_escribe_hechos_estructura_nueva(self):
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "escribe", "casos/x/02-hechos/hechos.md")
        self.assertTrue(ok)

    def test_caeiro_lee_materia_para_plazos(self):
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "lee", "materias/tutela/plazos.json")
        self.assertTrue(ok)

    def test_search_lee_materia_y_escribe_investigacion_nueva(self):
        ok, _ = vp.decidir(self.permisos, "02-investigador-search", "lee", "materias/tutela/checklist.md")
        self.assertTrue(ok)
        ok, _ = vp.decidir(self.permisos, "02-investigador-search", "escribe", "casos/x/03-investigacion/investigacion.md")
        self.assertTrue(ok)

    def test_redactor_lee_plantilla_de_materia_y_escribe_borrador_nuevo(self):
        ok, _ = vp.decidir(self.permisos, "03-redactor-reis", "lee",
                           "materias/demanda-laboral/plantillas/modelo-demanda-laboral.md")
        self.assertTrue(ok)
        ok, _ = vp.decidir(self.permisos, "03-redactor-reis", "escribe", "casos/x/04-borrador/borrador.md")
        self.assertTrue(ok)

    def test_verificador_lee_borrador_nuevo_y_escribe_informe_nuevo(self):
        ok, _ = vp.decidir(self.permisos, "04-verificador-soares", "lee", "casos/x/04-borrador/borrador.md")
        self.assertTrue(ok)
        ok, _ = vp.decidir(self.permisos, "04-verificador-soares", "escribe",
                           "casos/x/05-auditoria/informe-verificacion.md")
        self.assertTrue(ok)

    def test_contraparte_lee_informe_y_escribe_riesgo_nuevo(self):
        ok, _ = vp.decidir(self.permisos, "05-diablo-campos", "lee",
                           "casos/x/05-auditoria/informe-verificacion.md")
        self.assertTrue(ok)
        ok, _ = vp.decidir(self.permisos, "05-diablo-campos", "escribe",
                           "casos/x/05-auditoria/informe-riesgo.md")
        self.assertTrue(ok)


class TestBypasses(unittest.TestCase):
    def setUp(self):
        self.permisos = vp.cargar_permisos(RAIZ / "despacho" / "permisos.json")

    def d(self, agente, accion, objetivo):
        return vp.decidir(self.permisos, agente, accion, objetivo)

    def test_traversal_escritura_denegada(self):
        ok, motivo = self.d("01-observador-caeiro", "escribe", "casos/x/../../../../Windows/hechos.md")
        self.assertFalse(ok)
        self.assertIn("fuera del proyecto", motivo)
        self.assertIn("Regla 4", motivo)

    def test_traversal_lectura_denegada(self):
        ok, _ = self.d("02-investigador-search", "lee", "fuentes/../../../Users/alguien/.ssh/id_rsa")
        self.assertFalse(ok)

    def test_traversal_que_vuelve_a_permitido_se_resuelve(self):
        ok, _ = self.d("02-investigador-search", "lee", "fuentes/../ESTATUTO.md")
        self.assertTrue(ok)

    def test_ruta_absoluta_fuera_denegada(self):
        fuera = str(Path(tempfile.gettempdir()).resolve() / "hechos.md")
        ok, motivo = self.d("01-observador-caeiro", "escribe", fuera)
        self.assertFalse(ok)
        self.assertIn("fuera del proyecto", motivo)

    def test_asterisco_no_cruza_directorios(self):
        for agente in ["01-observador-caeiro", "04-verificador-soares", "05-diablo-campos"]:
            ok, _ = self.d(agente, "lee", "casos/c/privado/x/entrevista-y-pruebas.md")
            self.assertFalse(ok, agente)
        ok, _ = self.d("04-verificador-soares", "lee", "casos/c/privado/x/hechos.md")
        self.assertFalse(ok)

    def test_fuentes_anidadas_siguen_permitidas(self):
        ok, _ = self.d("05-diablo-campos", "lee", "fuentes/01_salud/a/b.md")
        self.assertTrue(ok)
        ok, _ = self.d("05-diablo-campos", "lee", "fuentes/x.md")
        self.assertTrue(ok)

    def test_operadores_de_consola_denegados(self):
        base = "python herramientas/calcular_plazos.py"
        for extra in [" && rm -rf x", " | cat", " > salida.txt", " $(whoami)", " `whoami`", "\nrm x", " ; ls"]:
            ok, motivo = self.d("01-observador-caeiro", "ejecuta", base + extra)
            self.assertFalse(ok, extra)
            self.assertIn("operadores de consola", motivo)

    def test_backslash_windows_permitido(self):
        ok, _ = self.d("01-observador-caeiro", "ejecuta", r"python herramientas\calcular_plazos.py --modo peticion")
        self.assertTrue(ok)

    def test_interprete_con_directorio_denegado(self):
        ok, _ = self.d("01-observador-caeiro", "ejecuta", "./python herramientas/calcular_plazos.py")
        self.assertFalse(ok)

    def test_opciones_del_interprete_denegadas(self):
        ok, motivo = self.d("01-observador-caeiro", "ejecuta", "python -c pass")
        self.assertFalse(ok)
        self.assertIn("opciones del intérprete", motivo)
        ok, _ = self.d("01-observador-caeiro", "ejecuta", "python -m http.server")
        self.assertFalse(ok)

    def test_script_con_traversal_denegado(self):
        ok, _ = self.d("01-observador-caeiro", "ejecuta", "python herramientas/../herramientas/verificar_citas.py")
        self.assertFalse(ok)

    def test_raiz_alterna_denegada(self):
        base = "python herramientas/verificar_citas.py casos/x/borrador.md"
        for extra in [" --raiz herramientas/tests/datos", " --raiz=herramientas/tests/datos",
                      " --raiz .", r" --raiz C:\otro", " --RAIZ x"]:
            ok, motivo = self.d("04-verificador-soares", "ejecuta", base + extra)
            self.assertFalse(ok, extra)
            self.assertIn("no puede cambiar la raíz del corpus (Regla 1)", motivo)
        ok, _ = self.d("04-verificador-soares", "ejecuta", base)
        self.assertTrue(ok)

    def test_investigacion_fuera_de_casos_denegada(self):
        base = "python herramientas/verificar_citas.py casos/x/borrador.md"
        for extra in [" --investigacion herramientas/tests/datos/investigacion.md",
                      " --investigacion=herramientas/tests/datos/investigacion.md",
                      " --investigacion casos/../fuera/investigacion.md",
                      " --investigacion casos/x/../../investigacion.md",
                      " --investigacion /tmp/investigacion.md",
                      " --investigacion casos",
                      " --investigacion"]:
            ok, motivo = self.d("04-verificador-soares", "ejecuta", base + extra)
            self.assertFalse(ok, extra)
            self.assertIn("Regla 1", motivo)
        for extra in [" --investigacion casos/x/investigacion.md", r" --investigacion casos\x\investigacion.md",
                      " --investigacion=casos/x/investigacion.md"]:
            ok, motivo = self.d("04-verificador-soares", "ejecuta", base + extra)
            self.assertTrue(ok, (extra, motivo))

    def test_lectura_denegada_sin_frase_de_escritura(self):
        ok, motivo = self.d("03-redactor-reis", "lee", "casos/c/informe-riesgo.md")
        self.assertFalse(ok)
        self.assertIn("Regla 4", motivo)
        self.assertNotIn("quien redacta no aprueba", motivo)


class TestEsquema(unittest.TestCase):
    def _cargar(self, datos):
        with tempfile.TemporaryDirectory() as t:
            ruta = Path(t) / "p.json"
            ruta.write_text(json.dumps(datos), encoding="utf-8")
            return vp.cargar_permisos(ruta)

    def test_falta_clave(self):
        with self.assertRaises(ValueError) as cm:
            self._cargar({"01-x": {"lee": [], "escribe": [], "internet": False}})
        self.assertIn("01-x", str(cm.exception))
        self.assertIn("ejecuta", str(cm.exception))

    def test_internet_debe_ser_booleano(self):
        with self.assertRaises(ValueError):
            self._cargar({"01-x": {"lee": [], "escribe": [], "ejecuta": [], "internet": "no"}})

    def test_valido(self):
        self.assertIn("01-x", self._cargar({"_n": "x", "01-x": {"lee": [], "escribe": [], "ejecuta": [], "internet": False}}))


class TestCwd(unittest.TestCase):
    def setUp(self):
        self.permisos = vp.cargar_permisos(RAIZ / "despacho" / "permisos.json")

    def test_ruta_relativa_se_resuelve_contra_cwd(self):
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "escribe", "caso-prueba/hechos.md",
                           raiz=RAIZ, cwd=RAIZ / "casos")
        self.assertTrue(ok)

    def test_cwd_fuera_de_la_raiz_deniega(self):
        ok, _ = vp.decidir(self.permisos, "01-observador-caeiro", "escribe", "casos/caso-prueba/hechos.md",
                           raiz=RAIZ, cwd=RAIZ.parent)
        self.assertFalse(ok)


class TestCargaYMetacaracteres(unittest.TestCase):
    def test_json_no_objeto(self):
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "p.json"
            ruta.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                vp.cargar_permisos(ruta)

    def test_rechaza_bang_y_llaves(self):
        permisos = vp.cargar_permisos(RAIZ / "despacho" / "permisos.json")
        for cmd in ["python herramientas/calcular_plazos.py !x", "python herramientas/calcular_plazos.py {a}"]:
            ok, _ = vp.decidir(permisos, "01-observador-caeiro", "ejecuta", cmd)
            self.assertFalse(ok, cmd)


class TestCLI(unittest.TestCase):
    def test_cli_denegado_sale_con_1(self):
        r = subprocess.run([sys.executable, str(RAIZ / "herramientas" / "verificar_permisos.py"),
                            "01-observador-caeiro", "escribe", "casos/caso-prueba/borrador.md"],
                           capture_output=True, text=True, cwd=RAIZ, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("denegado", r.stdout.lower())

    def _cli(self, *args):
        return subprocess.run([sys.executable, str(RAIZ / "herramientas" / "verificar_permisos.py"), *args],
                              capture_output=True, text=True, cwd=RAIZ, encoding="utf-8")

    def test_cli_permitido_sale_con_0(self):
        r = self._cli("01-observador-caeiro", "escribe", "casos/caso-prueba/hechos.md")
        self.assertEqual(r.returncode, 0)
        self.assertIn("permitido", r.stdout)

    def test_cli_uso_incorrecto_sale_con_2(self):
        self.assertEqual(self._cli("solo-uno").returncode, 2)


if __name__ == "__main__":
    unittest.main()
