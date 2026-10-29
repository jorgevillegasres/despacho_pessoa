import json, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "herramientas"))
import verificar_corpus as vcorp  # noqa: E402

SCRIPT = RAIZ / "herramientas" / "verificar_corpus.py"


class TestSello(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.fuentes = self.tmp / "fuentes"
        (self.fuentes / "a").mkdir(parents=True)
        (self.fuentes / "a" / "uno.md").write_text("uno", encoding="utf-8")
        (self.fuentes / "dos.md").write_text("dos", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args, "--fuentes", str(self.fuentes)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_sellar_y_comprobar_sin_cambios(self):
        vcorp.sellar(self.fuentes)
        self.assertTrue((self.fuentes / "SELLO.json").exists())
        cambios = vcorp.comprobar(self.fuentes)
        self.assertEqual(cambios, {"añadidos": [], "borrados": [], "modificados": []})

    def test_sello_se_escribe_con_saltos_lf(self):
        vcorp.sellar(self.fuentes)
        self.assertNotIn(b"\r", (self.fuentes / "SELLO.json").read_bytes())

    def test_detecta_modificado_añadido_y_borrado(self):
        vcorp.sellar(self.fuentes)
        (self.fuentes / "dos.md").write_text("dos cambiado", encoding="utf-8")
        (self.fuentes / "tres.md").write_text("tres", encoding="utf-8")
        (self.fuentes / "a" / "uno.md").unlink()
        cambios = vcorp.comprobar(self.fuentes)
        self.assertEqual(cambios["modificados"], ["dos.md"])
        self.assertEqual(cambios["añadidos"], ["tres.md"])
        self.assertEqual(cambios["borrados"], ["a/uno.md"])

    def test_comprobar_sin_sello_avisa(self):
        with self.assertRaises(FileNotFoundError):
            vcorp.comprobar(self.fuentes)

    def test_sello_no_afecta_huellas(self):
        a = vcorp.sellar(self.fuentes)["archivos"]
        b = vcorp.sellar(self.fuentes)["archivos"]
        self.assertEqual(a, b)
        self.assertNotIn("SELLO.json", b)

    def test_sello_corrupto_json(self):
        (self.fuentes / "SELLO.json").write_text("{no es json", encoding="utf-8")
        with self.assertRaises(ValueError):
            vcorp.comprobar(self.fuentes)
        r = self.cli("--comprobar")
        self.assertEqual(r.returncode, 2)
        self.assertIn("corrupto", r.stdout)

    def test_sello_sin_archivos(self):
        (self.fuentes / "SELLO.json").write_text(json.dumps({"x": 1}), encoding="utf-8")
        with self.assertRaises(ValueError):
            vcorp.comprobar(self.fuentes)
        self.assertEqual(self.cli("--comprobar").returncode, 2)

    def test_renombrado_es_borrado_mas_añadido(self):
        vcorp.sellar(self.fuentes)
        (self.fuentes / "dos.md").rename(self.fuentes / "dos_nuevo.md")
        c = vcorp.comprobar(self.fuentes)
        self.assertEqual(c["borrados"], ["dos.md"])
        self.assertEqual(c["añadidos"], ["dos_nuevo.md"])
        self.assertEqual(c["modificados"], [])

    def test_cli_intacto_y_cambio(self):
        self.assertEqual(self.cli("--sellar").returncode, 0)
        r = self.cli("--comprobar")
        self.assertEqual(r.returncode, 0)
        self.assertIn("intacto", r.stdout)
        (self.fuentes / "dos.md").write_text("otro", encoding="utf-8")
        r = self.cli("--comprobar")
        self.assertEqual(r.returncode, 1)
        self.assertIn("dos.md", r.stdout)

    def test_cli_sin_sello(self):
        r = self.cli("--comprobar")
        self.assertEqual(r.returncode, 1)
        self.assertIn("--sellar", r.stdout)

    def _enlace(self, destino, origen, dir_=False):
        try:
            os.symlink(origen, destino, target_is_directory=dir_)
        except (OSError, NotImplementedError):
            self.skipTest("el sistema no permite crear enlaces simbólicos")

    def test_rechaza_enlace_a_archivo(self):
        self._enlace(self.fuentes / "enlace.md", self.fuentes / "dos.md")
        with self.assertRaises(ValueError) as cm:
            vcorp.sellar(self.fuentes)
        self.assertIn("enlaces simbólicos", str(cm.exception))
        self.assertIn("enlace.md", str(cm.exception))
        r = self.cli("--sellar")
        self.assertEqual(r.returncode, 2)
        self.assertIn("enlaces simbólicos", r.stdout)

    def test_rechaza_enlace_a_directorio(self):
        self._enlace(self.fuentes / "carpeta", self.fuentes / "a", dir_=True)
        with self.assertRaises(ValueError):
            vcorp.huellas(self.fuentes)
        self.assertEqual(self.cli("--sellar").returncode, 2)

    def test_archivos_como_lista_o_texto_es_corrupto(self):
        for malo in ([], "abc", {"a.md": 5}):
            (self.fuentes / "SELLO.json").write_text(json.dumps({"archivos": malo}), encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                vcorp.comprobar(self.fuentes)
            self.assertIn("ruta→hash", str(cm.exception))
            self.assertEqual(self.cli("--comprobar").returncode, 2)

    def test_cli_carpeta_inexistente(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--sellar", "--fuentes", str(self.tmp / "nada")],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 2)

    def test_cli_sellar_mensaje(self):
        r = self.cli("--sellar")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Sello escrito", r.stdout)


if __name__ == "__main__":
    unittest.main()
