import json, re, subprocess, sys, unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
GEN = RAIZ / "web" / "generar_datos_web.py"
DATOS = RAIZ / "web" / "assets" / "datos.js"


def leer_datos():
    texto = DATOS.read_text(encoding="utf-8")
    m = re.search(r"window\.DESPACHO = (\{.*\});\s*$", texto, re.S)
    return json.loads(m.group(1))


class TestDatosWeb(unittest.TestCase):
    def test_datos_al_dia(self):
        r = subprocess.run([sys.executable, str(GEN), "--comprobar"], capture_output=True,
                           text=True, encoding="utf-8", cwd=RAIZ)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_festivos_iguales_al_json(self):
        esperado = json.loads((RAIZ / "herramientas" / "festivos_colombia.json").read_text(encoding="utf-8"))
        self.assertEqual(leer_datos()["festivos"], esperado)

    def test_cinco_fichas_completas(self):
        agentes = leer_datos()["agentes"]
        self.assertEqual([a["id"][:2] for a in agentes], ["01", "02", "03", "04", "05"])
        for a in agentes:
            for clave in ("nombre", "heteronimo", "descripcion", "cita", "produce", "falla", "lee", "escribe"):
                self.assertTrue(a[clave], f"{a['id']}: falta {clave}")
            self.assertNotIn("`", a["falla"])
            self.assertTrue(a["falla"].endswith("."))

    def test_ninguna_ficha_lee_notas_del_privado(self):
        for a in leer_datos()["agentes"]:
            self.assertFalse([r for r in a["lee"] if "privado" in r], a["id"])

if __name__ == "__main__":
    unittest.main()
